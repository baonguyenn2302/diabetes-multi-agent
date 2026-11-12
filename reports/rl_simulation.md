# Mô phỏng chính sách theo dõi (RL, chỉ mô phỏng)

> Môi trường giả lập. Xác suất chuyển trạng thái là giả định, không phải số liệu lâm sàng. Không áp dụng cho bệnh nhân thật.

## Chính sách học được

| Mức nguy cơ giả lập | Nội dung | Tái khám sau (tháng) |
|---|---|---|
| thấp | không có nội dung | 6 |
| trung bình | nội dung dinh dưỡng | 3 |
| cao | nội dung dinh dưỡng | 1 |

## So sánh chính sách (500 episode, cùng chuỗi ngẫu nhiên)

| Chính sách | Lợi ích trung bình (có chiết khấu) | Tỉ lệ bước ở nguy cơ cao | Nguy cơ cuối trung bình |
|---|---|---|---|
| Ngẫu nhiên | -8.9424 | 0.2652 | 0.756 |
| Cố định: 6 tháng, không nội dung | -14.1524 | 0.614 | 1.73 |
| Quy tắc đơn giản | -7.7009 | 0.1608 | 0.682 |
| Học được (Q-learning) | -7.7009 | 0.1608 | 0.682 |

Lợi ích cao hơn là tốt hơn. Chính sách học được chỉ có ý nghĩa trong môi trường giả lập này.
