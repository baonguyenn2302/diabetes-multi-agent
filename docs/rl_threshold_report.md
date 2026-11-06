# Báo cáo Q-learning chọn ngưỡng khoảng cách

Thí nghiệm tách biệt. Không thay đổi MAX_DISTANCE tự động.

## Bảng Q (hàng: trạng thái, cột: ngưỡng)

| trạng thái | 0.35 | 0.40 | 0.45 | 0.50 | 0.55 | 0.60 |
|---|---|---|---|---|---|---|
| in_scope | 0.435 | 0.441 | 0.469 | 0.618 | 0.441 | 0.465 |
| out_of_scope | 0.999 | 1.000 | 0.999 | 1.000 | 0.032 | 0.492 |

## Ngưỡng học được theo trạng thái

- in_scope: 0.50
- out_of_scope: 0.50

## Phần thưởng trung bình trên tập kiểm tra (không dùng để học)

| ngưỡng | phần thưởng trung bình |
|---|---|
| 0.35 | 1.000 |
| 0.40 | 1.000 |
| 0.45 | 1.000 |
| 0.50 | 1.000 |
| 0.55 | 1.000 |
| 0.60 | 1.000 |

Ngưỡng tốt nhất trên tập kiểm tra: 0.35

Khuyến nghị: chỉ đổi MAX_DISTANCE nếu ngưỡng này cũng được xác nhận bằng bộ kiểm tra hồi quy (scripts/eval_knowledge.py).
