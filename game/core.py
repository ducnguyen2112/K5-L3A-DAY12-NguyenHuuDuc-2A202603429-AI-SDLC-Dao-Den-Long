import math, random

TUNING = {
 'player_speed':6.0,'carry_capacity':20,'lantern_cost':10,'lantern_count_night1':5,
 'pickup_radius':1.3,'interact_radius':2.7,'pulse_cost':3,'pulse_radius':6.0,
 'night1_duration_s':300.0,'flames':3,'invuln_s':2.0,'hit_drop_ratio':.25,
 'pulse_stun_s':3.0,'pulse_push_m':3.0,'pulse_cooldown_s':1.0,'safe_radius':5.0,
 'shade_speed':2.1,'shade_hit_radius':.9,'fall_enabled':False,
 'score':{'per_mote':10,'per_lantern':200,'per_stun':25,'per_second_left':2,'per_flame_left':100}}

def _num(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def _pos(p):
    return isinstance(p,list) and len(p)==3 and all(_num(v) for v in p)
def _dist(a,b): return math.hypot(a[0]-b[0],a[2]-b[2])
def _round(v): return round(float(v),3)
def _rp(p): return [_round(x) for x in p]

def validate_scenario(s):
    if not isinstance(s,dict): raise ValueError('scenario must be object')
    for key in ('player','motes','shades','lanterns'):
        if key in s and not isinstance(s[key], (dict,list)): raise ValueError('invalid '+key)
    if 'player' in s:
        p=s['player'];
        if not isinstance(p,dict) or ('pos' in p and not _pos(p['pos'])): raise ValueError('invalid player')
        for k in ('carried','flames'):
            if k in p and (not _num(p[k]) or p[k]<0 or int(p[k])!=p[k]): raise ValueError('invalid player '+k)
    for k in ('motes',):
        if k in s and not all(_pos(x) for x in s[k]): raise ValueError('invalid '+k)
    if 'shades' in s:
        if not all(isinstance(x,dict) and _pos(x.get('pos')) for x in s['shades']): raise ValueError('invalid shades')
    if 'lanterns' in s:
        for x in s['lanterns']:
            if not isinstance(x,dict) or x.get('id') not in ['L1','L2','L3','L4','L5'] or ('pos' in x and not _pos(x['pos'])): raise ValueError('invalid lantern')
            if 'lit' in x and not isinstance(x['lit'],bool): raise ValueError('invalid lit')
            if 'deposited' in x and (not _num(x['deposited']) or x['deposited']<0): raise ValueError('invalid deposit')
    for k in ('random_motes','random_shades'):
        if k in s and not isinstance(s[k],bool): raise ValueError('invalid '+k)
    if 'time_left_s' in s and (not _num(s['time_left_s']) or s['time_left_s']<0): raise ValueError('invalid time')
    return s

def validate_inputs(data):
    if not isinstance(data,dict) or not isinstance(data.get('frames',[]),list): raise ValueError('inputs.frames must be array')
    out=[]; last=-1
    for f in data.get('frames',[]):
        if not isinstance(f,dict) or not isinstance(f.get('tick'),int) or isinstance(f.get('tick'),bool) or f['tick']<0 or f['tick']<=last: raise ValueError('ticks must increase')
        last=f['tick']; q=dict(f); q.pop('tick')
        if 'move' in q and (not isinstance(q['move'],list) or len(q['move'])!=2 or not all(_num(v) and -1<=v<=1 for v in q['move'])): raise ValueError('invalid move')
        if 'cam_yaw_deg' in q and not _num(q['cam_yaw_deg']): raise ValueError('invalid yaw')
        for k in ('jump','interact','pulse'):
            if k in q and not isinstance(q[k],bool): raise ValueError('invalid '+k)
        out.append((f['tick'],q))
    return out

class Game:
 def __init__(self,seed=1,scenario=None):
  self.rng=random.Random(seed); s=validate_scenario(scenario or {})
  self.tick=0; self.state='playing'; self.score=0; self.time_left=float(s.get('time_left_s',TUNING['night1_duration_s']))
  p=s.get('player',{}); self.player={'pos':list(p.get('pos',[0,0,0])),'flames':int(p.get('flames',TUNING['flames'])),'carried':int(p.get('carried',0))}; self.invuln=0; self.cooldown=0
  r=20; self.lanterns=[{'id':'L'+str(i+1),'pos':[r*math.cos(math.pi/2+i*2*math.pi/5),0,r*math.sin(math.pi/2+i*2*math.pi/5)],'deposited':0,'lit':False} for i in range(5)]
  for x in s.get('lanterns',[]):
   z=next((a for a in self.lanterns if a['id']==x['id']),None)
   if z: z.update({k:x[k] for k in ('pos','deposited','lit') if k in x})
  self.motes=[{'id':'M'+str(i+1),'pos':list(x)} for i,x in enumerate(s.get('motes',[]))]
  if 'motes' not in s and s.get('random_motes',True):
   for i in range(65):
    a=self.rng.random()*math.tau; rr=5+self.rng.random()*22; self.motes.append({'id':'M'+str(len(self.motes)+1),'pos':[rr*math.cos(a),0,rr*math.sin(a)]})
  self.shades=[{'id':x.get('id','S'+str(i+1)),'pos':list(x['pos']),'state':'chase','stun':0} for i,x in enumerate(s.get('shades',[]))]
  if 'shades' not in s and s.get('random_shades',True): self.shades += [{'id':'S'+str(i+1),'pos':[(-1)**i*15,0,(-1)**(i//2)*15],'state':'chase','stun':0} for i in range(3)]
  self.inputs={'move':[0,0],'cam_yaw_deg':0,'jump':False,'interact':False,'pulse':False}; self._won_bonus=False
 def _event(self,name,data=None): return {'type':'event','tick':self.tick+1,'name':name,**({'data':data} if data is not None else {})}
 def step(self,patch=None):
  if self.state!='playing': self.tick+=1; return []
  old=dict(self.inputs); self.inputs.update(patch or {}); ev=[]; dt=1/60; self.time_left=max(0,self.time_left-dt); self.invuln=max(0,self.invuln-dt); self.cooldown=max(0,self.cooldown-dt)
  m=self.inputs['move']; n=math.hypot(m[0],m[1]);
  if n>1: m=[m[0]/n,m[1]/n]
  a=math.radians(self.inputs['cam_yaw_deg']); dx=(m[0]*math.cos(a)+m[1]*math.sin(a))*TUNING['player_speed']*dt; dz=(-m[0]*math.sin(a)+m[1]*math.cos(a))*TUNING['player_speed']*dt
  self.player['pos'][0]+=dx; self.player['pos'][2]+=dz
  radius=math.hypot(self.player['pos'][0],self.player['pos'][2])
  if radius>29.5:
   self.player['pos'][0]*=29.5/radius; self.player['pos'][2]*=29.5/radius
  if not hasattr(self,'vy'): self.vy=0
  if self.inputs['jump'] and not old['jump'] and self.player['pos'][1]<=0: self.vy=6
  if self.vy or self.player['pos'][1]>0:
   self.player['pos'][1]=max(0,self.player['pos'][1]+self.vy*dt); self.vy-=16*dt
   if self.player['pos'][1]==0: self.vy=0
  for mo in self.motes[:]:
   if self.player['carried']<TUNING['carry_capacity'] and _dist(self.player['pos'],mo['pos'])<=TUNING['pickup_radius']:
    self.motes.remove(mo); self.player['carried']+=1; self.score+=TUNING['score']['per_mote']; ev.append(self._event('mote_picked',{'carried':self.player['carried']}))
  if self.inputs['interact'] and not old['interact']:
   for l in self.lanterns:
    if not l['lit'] and _dist(self.player['pos'],l['pos'])<=TUNING['interact_radius'] and self.player['carried']:
     amount=min(self.player['carried'],TUNING['lantern_cost']-l['deposited']); l['deposited']+=amount; self.player['carried']-=amount; ev.append(self._event('deposit',{'lantern_id':l['id'],'amount':amount,'deposited':l['deposited']}))
     if l['deposited']>=TUNING['lantern_cost']: l['lit']=True; self.score+=TUNING['score']['per_lantern']; ev.append(self._event('lantern_lit',{'lantern_id':l['id']}))
     break
  if self.inputs['pulse'] and not old['pulse'] and self.player['carried']>=TUNING['pulse_cost'] and self.cooldown<=0:
   self.player['carried']-=TUNING['pulse_cost']; self.cooldown=TUNING['pulse_cooldown_s']; ids=[]
   for sh in self.shades:
    if _dist(self.player['pos'],sh['pos'])<=TUNING['pulse_radius']:
     sh['state']='stunned'; sh['stun']=TUNING['pulse_stun_s']; ids.append(sh['id']); self.score+=TUNING['score']['per_stun']
     px=sh['pos'][0]-self.player['pos'][0]; pz=sh['pos'][2]-self.player['pos'][2]; pd=math.hypot(px,pz)
     if pd==0: px,pz,pd=1,0,1
     sh['pos'][0]+=px/pd*TUNING['pulse_push_m']; sh['pos'][2]+=pz/pd*TUNING['pulse_push_m']
   ev.append(self._event('pulse',{'stunned_ids':ids}))
  for sh in self.shades:
   if sh['stun']>0: sh['stun']=max(0,sh['stun']-dt); sh['state']='stunned' if sh['stun'] else 'chase'; continue
   dx=self.player['pos'][0]-sh['pos'][0]; dz=self.player['pos'][2]-sh['pos'][2]; d=math.hypot(dx,dz)
   if d>0:
    step=min(d,TUNING['shade_speed']*dt); sh['pos'][0]+=dx/d*step; sh['pos'][2]+=dz/d*step
   if any(l['lit'] and _dist(sh['pos'],l['pos'])<TUNING['safe_radius'] for l in self.lanterns):
    # Lit lanterns are safe: retreat along the radial direction.
    for l in self.lanterns:
     if l['lit'] and _dist(sh['pos'],l['pos'])<TUNING['safe_radius']:
      vx=sh['pos'][0]-l['pos'][0]; vz=sh['pos'][2]-l['pos'][2]; vd=math.hypot(vx,vz) or 1
      sh['pos'][0]=l['pos'][0]+vx/vd*TUNING['safe_radius']; sh['pos'][2]=l['pos'][2]+vz/vd*TUNING['safe_radius']
      break
   if _dist(self.player['pos'],sh['pos'])<=TUNING['shade_hit_radius'] and self.invuln<=0 and not any(l['lit'] and _dist(self.player['pos'],l['pos'])<=TUNING['safe_radius'] for l in self.lanterns):
    self.player['flames']-=1; self.invuln=TUNING['invuln_s']; drop=min(self.player['carried'],math.floor(self.player['carried']* TUNING['hit_drop_ratio'])); self.player['carried']-=drop; ev.append(self._event('player_hit',{'by':'shade','flames':self.player['flames'],'dropped':drop}))
  if all(x['lit'] for x in self.lanterns): self.state='won'; self.score+=int(self.time_left*TUNING['score']['per_second_left'])+self.player['flames']*TUNING['score']['per_flame_left']; ev.append(self._event('game_over',{'result':'won','reason':'all_lit'}))
  elif self.player['flames']<=0: self.state='lost'; ev.append(self._event('game_over',{'result':'lost','reason':'no_flames'}))
  elif self.time_left<=0: self.state='lost'; ev.append(self._event('game_over',{'result':'lost','reason':'dawn'}))
  self.tick+=1; return ev
 def snapshot(self):
  return {'type':'snapshot','tick':self.tick,'sim_tick':self.tick,'state':self.state,'time_left_s':_round(self.time_left),'score':self.score,'player':{'pos':_rp(self.player['pos']),'flames':self.player['flames'],'carried':self.player['carried'],'invuln_s':_round(self.invuln),'pulse_cooldown_s':_round(self.cooldown)},'lanterns':[{'id':l['id'],'pos':_rp(l['pos']),'lit':l['lit'],'deposited':l['deposited']} for l in self.lanterns],'shades':[{'id':s['id'],'pos':_rp(s['pos']),'state':s['state'],'stunned_remaining_s':_round(s['stun'])} for s in self.shades],'motes_active':len(self.motes),'motes':[{'id':m['id'],'pos':_rp(m['pos'])} for m in self.motes]}
