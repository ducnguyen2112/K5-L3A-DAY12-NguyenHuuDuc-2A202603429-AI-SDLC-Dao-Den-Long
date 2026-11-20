# AGENTS.md — Đảo Đèn Lồng

## Mục tiêu
Xây dựng Phase 1 đúng PRD-0 và Test Contract v1.0, ưu tiên lõi deterministic trước giao diện.

## Phạm vi tác nhân
- `game/`: luật mô phỏng authoritative và CLI headless. Không sửa tuning để làm demo dễ hơn.
- `server.py`: adapter HTTP cục bộ, không được chứa luật riêng.
- `web/`: lớp trình bày Three.js. Không thêm thực thể làm thay đổi headless.
- `tests/`: kiểm tra contract, không phụ thuộc network hay GPU.
- `docs/`: giả định, nhật ký AI và bằng chứng chạy.

## Quy tắc
1. Input không tin cậy: validate scenario/inputs, không chạy code tải xuống.
2. Mọi tọa độ/distance gameplay dùng XZ, tick cố định 60Hz.
3. Cùng seed/scenario/inputs phải cho JSONL byte-identical.
4. Chạy `python3 -m unittest discover -s tests -v` trước khi bàn giao.
5. Khi thêm sáng tạo, tắt hoặc cô lập trong headless và cập nhật README.

## Lệnh kiểm chứng
```sh
python3 -m compileall -q game
python3 -m unittest discover -s tests -v
python3 -m game.headless --seed 7 --night 1 --ticks 120 --out /tmp/dao.jsonl
```
