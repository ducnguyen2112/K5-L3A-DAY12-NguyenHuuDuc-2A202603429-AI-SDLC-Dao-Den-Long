# Giả định Phase 1

- Hòn đảo là đĩa bán kính 30m, mép đảo bị chặn vì `fall_enabled=false`.
- 5 đèn đặt trên vòng tròn bán kính 20m; vị trí cụ thể được công khai qua tuning/JSONL.
- Đom đóm tự sinh cố định theo seed; scenario với `random_motes=false` thay thế toàn bộ danh sách.
- Bóng Mực tự sinh cố định theo seed; đèn sáng tạo safe radius 5m.
- Bị chạm mất một ngọn lửa, bất tử 2 giây sau hit và rơi 25% số đom đóm đang mang.
- Nhảy có vật lý cosmetic, không cần để hoàn thành màn; không có damage do rơi.
- Tương tác nạp dùng rising edge của nút `interact`; pulse dùng rising edge và cooldown.
