# Phase 1 proof

## Automated evidence

Run from repository root:

```text
python -m unittest discover -s tests -v
Ran 8 tests in 0.874s
OK

python -m compileall -q game
```

The tests cover exact tick/event numbering, deterministic repeatability, movement normalization and camera yaw, pickup/capacity, deposit and win, pulse/stun/cooldown, hit/invulnerability/loss, dawn timeout, and invalid input exit code 2.

## Verification run (2026-11-20)

```text
python -m unittest discover -s tests -v
Ran 8 tests in 0.983s
OK
python -m compileall -q game
```

Live HTTP smoke against `python server.py --port 8765`:

```text
GET /api/state  -> snapshot with valid state/tuning JSON
POST /api/step {"input":{"move":[0,1]},"steps":2}
             -> snapshot advanced by 2 ticks, state playing, events 0
```

Determinism check: two runs with `--seed 99 --night 1 --ticks 240 --snapshot-every 15` compared with `cmp`; exit code `0` (byte-identical). Invalid inputs with duplicate frame ticks returned exit code `2` and stderr `headless input error: ticks must increase`.


Edge headless (1440×900): loaded the real server at port 8765, clicked Start, held W for 1.2 seconds. No JavaScript page errors were reported. HUD timer advanced to 04:58; a mote was picked and score increased. Screenshot inspected: [`gameplay.png`](gameplay.png), showing Mây, island, motes, shades and HUD. This is a smoke test, not evidence of a complete manual playthrough to victory.

## Manual smoke checklist (remaining full-playthrough checks)

1. Run `python3 server.py`, open `http://127.0.0.1:8000` in a WebGL browser.
2. Press **Thắp lên cuộc phiêu lưu**; confirm 3D island, Mây, five unlit lanterns and HUD appear.
3. Walk with WASD; confirm the camera follows and prompt appears near a lantern.
4. Walk through gold motes; confirm carried count and score rise.
5. Press E beside a lantern; confirm deposit event/visual light, warm glow and HUD dot changes.
6. Approach a purple Ink Shade; press F; confirm flash ring, push/stun and carried-light cost.
7. Repeat until all five lanterns are lit; confirm win overlay and replay button.

## Headless evidence shape

The CLI always emits snapshot tick 0, event lines at the resulting tick, periodic snapshots, and a final `end` line. The exact bytes are deterministic for the same seed/scenario/inputs. Frontend-only flowers, path stones, cloud sea and prose do not exist in the simulation.
