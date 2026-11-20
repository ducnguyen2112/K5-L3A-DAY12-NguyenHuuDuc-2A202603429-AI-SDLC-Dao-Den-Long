"""Contract regression tests; run without third party packages."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from game.core import Game, TUNING


def empty(**kw):
    return dict(random_motes=False, random_shades=False, motes=[], shades=[], **kw)


class ContractTests(unittest.TestCase):
    def test_tick_and_move(self):
        g = Game(1, empty())
        self.assertEqual(g.snapshot()['tick'], 0)
        for _ in range(60):
            g.step({'move': [0, 1]})
        self.assertAlmostEqual(g.snapshot()['player']['pos'][2], TUNING['player_speed'], places=3)
        self.assertAlmostEqual(g.snapshot()['time_left_s'], TUNING['night1_duration_s']-1)

    def test_camera_and_normalization(self):
        g = Game(1, empty())
        for _ in range(60):
            g.step({'move':[0, 1], 'cam_yaw_deg':90})
        self.assertAlmostEqual(g.snapshot()['player']['pos'][0], TUNING['player_speed'], places=3)
        g = Game(1, empty())
        for _ in range(60):
            g.step({'move':[1,1]})
        p = g.snapshot()['player']['pos']
        self.assertAlmostEqual((p[0]**2+p[2]**2)**.5, TUNING['player_speed'], places=2)

    def test_pickup_capacity_and_event(self):
        n = TUNING['carry_capacity']
        g=Game(1,dict(random_motes=False,random_shades=False,motes=[[0,0,0]]*(n+2),shades=[]))
        events=g.step({})
        self.assertEqual(g.snapshot()['player']['carried'], n)
        self.assertEqual(sum(e['name']=='mote_picked' for e in events), n)
        self.assertTrue(all(e['tick']==1 for e in events))

    def test_deposit_rising_edge_and_win(self):
        cost=TUNING['lantern_cost']
        lanterns=[{'id':f'L{i}','lit':True} for i in range(2,6)]
        lanterns.append({'id':'L1','pos':[0,0,0]})
        g=Game(1,empty(player={'carried':cost},lanterns=lanterns))
        self.assertEqual(g.snapshot()['score'],0)
        events=g.step({'interact':True})
        self.assertEqual(g.state,'won')
        self.assertIn('lantern_lit',[e['name'] for e in events])
        self.assertIn('game_over',[e['name'] for e in events])

    def test_pulse_and_cost(self):
        g=Game(1,dict(random_motes=False,random_shades=False,motes=[],shades=[{'id':'ink','pos':[2,0,0]}],player={'carried':10}))
        events=g.step({'pulse':True})
        self.assertEqual(g.snapshot()['player']['carried'],10-TUNING['pulse_cost'])
        self.assertEqual(g.snapshot()['shades'][0]['state'],'stunned')
        self.assertIn('ink', next(e for e in events if e['name']=='pulse')['data']['stunned_ids'])
        self.assertNotIn('pulse',[e['name'] for e in g.step({'pulse':True})])

    def test_hit_invulnerability_loss(self):
        scenario=dict(random_motes=False,random_shades=False,motes=[],shades=[{'pos':[0,0,0]}],player={'flames':1})
        g=Game(1,scenario)
        events=g.step({})
        self.assertEqual(g.state,'lost')
        self.assertEqual(next(e for e in events if e['name']=='game_over')['data']['reason'],'no_flames')
        scenario['player']={'flames':3}
        g=Game(1,scenario)
        g.step({})
        for _ in range(20): g.step({})
        self.assertEqual(g.snapshot()['player']['flames'],2)

    def test_dawn(self):
        g=Game(1,empty(time_left_s=1/60))
        self.assertEqual(g.step({})[-1]['data']['reason'],'dawn')
        self.assertEqual(g.state,'lost')

    def test_cli_deterministic_and_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out.jsonl'
            cmd=[sys.executable,'-m','game.headless','--seed','11','--night','1','--ticks','120','--out',str(out)]
            subprocess.run(cmd,cwd=ROOT,check=True)
            first=out.read_bytes()
            subprocess.run(cmd,cwd=ROOT,check=True)
            self.assertEqual(first,out.read_bytes())
            lines=[json.loads(x) for x in first.splitlines()]
            self.assertEqual(lines[0]['tick'],0)
            self.assertEqual(lines[-1]['type'],'end')
            self.assertEqual(lines[-1]['ticks'],120)
            bad=Path(d)/'bad.json'
            bad.write_text('{"frames":[{"tick":2},{"tick":2}]}')
            result=subprocess.run(cmd+['--inputs',str(bad)],cwd=ROOT,capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertTrue(result.stderr)

if __name__=='__main__':
    unittest.main(verbosity=2)
