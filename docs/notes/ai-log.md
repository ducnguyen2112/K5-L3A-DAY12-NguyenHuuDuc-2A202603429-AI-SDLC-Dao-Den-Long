# Nhật ký dùng AI

- 2026-11-20: Đọc PRD-0 và Test Contract v1.0; chọn Python stdlib cho simulation/headless và web Three.js vì không phụ thuộc GPU/Node ở chế độ kiểm thử.
- 2026-11-20: Tách lõi authoritative khỏi adapter HTTP; thêm seed, scenario, inputs, JSONL end bắt buộc.
- 2026-11-20: Thêm một ý tưởng nhỏ ở frontend (cánh hoa ký ức) sau khi khóa tuning lõi; ghi rõ không ảnh hưởng headless.
- 2026-11-20: Viết test deterministic, tick 60Hz, chuyển động/camera, pickup/deposit/win, pulse, hit/loss, dawn và lỗi inputs.
- 2026-11-20: Việc còn cần xác nhận trong môi trường bàn giao: chạy browser smoke với Chrome/Edge; nếu WebGL bị chặn, headless vẫn là nguồn bằng chứng chính.

AI không được xem là bằng chứng thực thi: các lệnh test và ảnh/chụp màn hình phải được chạy lại từ workspace này.
