# Đảo Đèn Lồng — Phase 1

Game 3D web nhỏ, chơi được trên macOS/Linux/Windows bằng Python 3.11+ và trình duyệt WebGL. Mục tiêu Đêm 1: điều khiển Mây, nhặt đom đóm, nạp đủ 5 Đèn Lồng Lớn và dùng ánh sáng xua Bóng Mực.

## Chạy (3 lệnh)

```sh
python3 -m compileall -q game
python3 server.py
# mở http://127.0.0.1:8000
```

Windows dùng `python` thay cho `python3`. Không cần Node/npm; Three.js đã được đóng gói tại `web/vendor/`.

## Điều khiển

- `W A S D` hoặc phím mũi tên: đi lại; kéo chuột: xoay camera.
- `Space`: nhảy (có tính vật lý trong lõi; không cần để thắng).
- `E`: nạp tất cả đom đóm đang mang vào đèn gần nhất.
- `F`: tỏa sáng, làm choáng và đẩy Bóng Mực (tốn 3 đom đóm).
- `P`: tạm dừng. Nút âm thanh bật tiếng chuông nhẹ khi nhặt/thắp đèn.

## Điểm và tuning

- Nhặt đom đóm: `+10`; thắp đèn: `+200`; làm choáng Bóng Mực: `+25`.
- Thời gian còn lại khi thắng: `+2/giây`; mỗi ngọn lửa còn lại: `+100`.
- Bắt đầu với 3 ngọn lửa; Bóng Mực chạm vào Mây mất 1 lửa và rơi 25% đom đóm đang mang.
- Đêm dài 300 giây, mỗi đèn cần 10 đom đóm, sức chứa 20. Đèn đã sáng tạo vùng an toàn bán kính 5m.
- `fall_enabled=false`: mép đảo được chặn, không có phạt rơi.
- `jump` là cơ chế di chuyển/hoạt ảnh và không tạo sự kiện riêng trong v1.0.

## Headless Test Contract v1.0

Lõi chạy cố định 60 tick/giây, không GPU, deterministic theo seed, scenario và inputs. Hợp đồng đầy đủ nằm ở [`game.contract.json`](game.contract.json).

```sh
python3 -m game.headless --seed 7 --night 1 --ticks 600 --out /tmp/dao.jsonl --snapshot-every 10
python3 -m game.headless --seed 7 --night 1 --scenario scenario.json --inputs inputs.json --ticks 1800 --out /tmp/dao.jsonl
```

Lỗi JSON/đầu vào trả mã 2; lỗi khác trả mã khác 0; thành công luôn có dòng `end` cuối cùng. `game/core.py` là nguồn luật dùng chung; `server.py` chỉ là adapter cho giao diện.

## Bằng chứng

- Chạy smoke contract: `python3 tests/test_contract.py`.
- Chạy toàn bộ kiểm thử: `python3 -m unittest discover -s tests -v`.
- Ghi chép kiểm thử thủ công và giả định: [`docs/proof/phase1.md`](docs/proof/phase1.md), [`docs/notes/assumptions.md`](docs/notes/assumptions.md).
- Nhật ký dùng AI: [`docs/notes/ai-log.md`](docs/notes/ai-log.md).

## Sáng tạo của tôi

Tôi thêm **cánh hoa ký ức** bay chậm trên đảo, lời thoại ngắn thay đổi sau mỗi đèn sáng, các lối đá cong, biển mây và âm thanh chuông bật tùy chọn. Đây là các lớp hiển thị/âm thanh; chúng không thêm thực thể khi headless và không thay đổi JSONL. Bằng chứng lõi vẫn đúng: test contract kiểm tra snapshot tick 0, tick cố định, nhặt/nạp/thắp/pulse, hit, thắng/thua, điểm và dòng `end`.

## Giả định chính

PRD không quy định vị trí cụ thể, tốc độ hay số lượng đom đóm nên các giá trị này được cố định trong `game.contract.json`. Đèn sáng là vùng an toàn; Bóng Mực không đi vào vùng này. Scenario thay thế danh sách mote/shade nhưng không phát sự kiện hay cộng điểm khi dựng.

## Harness AI

- [`AGENTS.md`](AGENTS.md): vai trò, phạm vi và nguyên tắc kiểm chứng.
- [` .claude/skills/`](.claude/skills/): thư mục dành cho skill nội bộ của bài nộp.
