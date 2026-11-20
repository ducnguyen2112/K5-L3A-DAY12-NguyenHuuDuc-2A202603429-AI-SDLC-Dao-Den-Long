import argparse,json,sys
from .core import Game,validate_inputs,validate_scenario

def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument('--seed',type=int,required=True); p.add_argument('--night',type=int,required=True); p.add_argument('--scenario'); p.add_argument('--inputs'); p.add_argument('--ticks',type=int,required=True); p.add_argument('--out',required=True); p.add_argument('--snapshot-every',type=int,default=10); a=p.parse_args(argv)
 try:
  if a.night!=1 or a.ticks<0 or a.snapshot_every<=0: raise ValueError('night must be 1, ticks nonnegative, snapshot interval positive')
  scenario={}
  if a.scenario:
   with open(a.scenario,encoding='utf-8') as f: scenario=validate_scenario(json.load(f))
  frames=[]
  if a.inputs:
   with open(a.inputs,encoding='utf-8') as f: frames=validate_inputs(json.load(f))
  bytick=dict(frames); g=Game(a.seed,scenario)
  with open(a.out,'w',encoding='utf-8') as out:
   def emit(x): out.write(json.dumps(x,separators=(',',':'),ensure_ascii=False)+'\n')
   emit(g.snapshot())
   for _ in range(a.ticks):
    patch=bytick.get(g.tick)
    for e in g.step(patch): emit(e)
    if g.tick%a.snapshot_every==0: emit(g.snapshot())
    if g.state!='playing': break
   emit({'type':'end','ticks':g.tick,'state':g.state,'score':g.score})
  return 0
 except (OSError,ValueError,KeyError,TypeError, json.JSONDecodeError) as e:
  print('headless input error: '+str(e),file=sys.stderr); return 2
if __name__=='__main__': sys.exit(main())
