# Đánh giá hệ thống hỗ trợ quyết định tiểu đường

> Prototype học tập. Số liệu dưới đây phục vụ đánh giá kỹ thuật, không phải bằng chứng lâm sàng.

## 1. Mô hình DL trên tập test

Số ca test: 14422 · ngưỡng quyết định: 0.85

| Metric | Tính lại | Ghi trong model card | Khớp |
|---|---|---|---|
| accuracy | 0.97 | 0.97 | ✓ |
| precision | 0.933 | 0.933 | ✓ |
| recall | 0.7115 | 0.7115 | ✓ |
| f1 | 0.8073 | 0.8073 | ✓ |
| roc_auc | 0.9749 | 0.9749 | ✓ |

## 2. So sánh cấu hình (ablation)

| Cấu hình | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| DL một mình | 905 | 65 | 367 | 0.933 | 0.7115 | 0.8073 |
| DL + Rule | 1031 | 3153 | 241 | 0.2464 | 0.8105 | 0.3779 |

- Số ca dương tính mà DL bỏ sót nhưng lớp Rule cảnh báo (được cứu): **126**.
- Số báo động thêm trên ca không có bệnh: **3088**.
- Độ tăng recall: **+0.099**.
- Số ca có cờ cần chuyên gia xem xét (mâu thuẫn model và luật): **3214**.

## 3. Ca thử có nhãn (lấy ngẫu nhiên từ tập test, cố định seed)

**TP: Đúng: model phát hiện được** (5 ca)

| Ca (chỉ số trong test) | Nhãn thật | Score DL | Dự đoán | Cảnh báo luật |
|---|---|---|---|---|
| 10555 | 1 | 0.997 | 1 | có |
| 1977 | 1 | 1.0 | 1 | có |
| 425 | 1 | 1.0 | 1 | có |
| 12234 | 1 | 1.0 | 1 | có |
| 4579 | 1 | 1.0 | 1 | có |

**FN: Bỏ sót: model dự đoán thấp nhưng bệnh nhân có bệnh** (5 ca)

| Ca (chỉ số trong test) | Nhãn thật | Score DL | Dự đoán | Cảnh báo luật |
|---|---|---|---|---|
| 4743 | 1 | 0.6317 | 0 | không |
| 4547 | 1 | 0.2877 | 0 | có |
| 2791 | 1 | 0.4852 | 0 | có |
| 2072 | 1 | 0.647 | 0 | không |
| 13522 | 1 | 0.6145 | 0 | không |

**FP: Báo động nhầm: model dự đoán cao nhưng không có bệnh** (5 ca)

| Ca (chỉ số trong test) | Nhãn thật | Score DL | Dự đoán | Cảnh báo luật |
|---|---|---|---|---|
| 2130 | 0 | 0.8828 | 1 | không |
| 12338 | 0 | 0.8511 | 1 | có |
| 632 | 0 | 0.8811 | 1 | có |
| 621 | 0 | 0.8605 | 1 | có |
| 5458 | 0 | 0.8963 | 1 | có |

**TN: Đúng: model dự đoán thấp và không có bệnh** (5 ca)

| Ca (chỉ số trong test) | Nhãn thật | Score DL | Dự đoán | Cảnh báo luật |
|---|---|---|---|---|
| 4205 | 0 | 0.1014 | 0 | không |
| 9120 | 0 | 0.1973 | 0 | có |
| 10863 | 0 | 0.0 | 0 | không |
| 478 | 0 | 0.0 | 0 | không |
| 10142 | 0 | 0.0 | 0 | không |

## 4. Độ trễ

Số request đo: 30 · tổng thời gian trung bình 181.8 ms, p50 151 ms, p95 228 ms.

| Agent | Trung bình (ms) | p95 (ms) |
|---|---|---|
| data | 0.0 | 0 |
| dl | 45.1 | 56 |
| rule | 0.0 | 0 |
| kg | 136.8 | 187 |
| explain | 0.0 | 0 |

Kiểm tra nhất quán: 30/30 ca cho cùng dự đoán khi đi qua toàn bộ Coordinator và khi chạy batch trực tiếp.

Trạng thái các request đo: ok: 30

## 5. Độ phủ nguồn của bằng chứng KG

| Câu hỏi | Số bằng chứng | Có nguồn |
|---|---|---|
| Triệu chứng của tiểu đường là gì? | 9 | 9 |
| Chỉ số HbA1c bao nhiêu thì bị tiền tiểu đường? | 9 | 9 |
| Ngưỡng HbA1c để chẩn đoán tiểu đường | 10 | 10 |
| Những ai dễ bị tiểu đường type 2? | 9 | 9 |
| Tiền tiểu đường là gì và có nguy hiểm không? | 10 | 10 |
| Biến chứng của tiểu đường nguy hiểm không? | 9 | 9 |
| Tôi nên ăn uống và vận động thế nào để phòng bệnh? | 2 | 2 |
| Xét nghiệm đường huyết lúc đói bao nhiêu thì cao? | 4 | 4 |
| Người cao tuổi cần lưu ý gì về biến chứng tiểu đường? | 10 | 10 |
| Tiểu đường thai kỳ có ảnh hưởng gì không? | 10 | 10 |

Tổng: 82/82 bằng chứng có nguồn (100%).

## 6. Hạn chế cần nêu trong báo cáo

- Dataset là dữ liệu công khai, không có nhãn loại 1 và loại 2, và không ghi thời điểm đo đường huyết.
- Lớp Rule chỉ bắt các ca có xét nghiệm vượt ngưỡng. Nó không thay thế model và không đo được ca model dự đoán sai theo hướng khác.
- Lớp KG không thay đổi dự đoán. Vai trò của nó là gắn bằng chứng có nguồn cho báo cáo.
- Ngưỡng tuổi 45 và BMI 30 chưa có trong KG. Tri thức chưa được chuyên gia thẩm định.
- Thời gian đo phụ thuộc đường truyền tới Neo4j Aura và máy chạy thử, nên chỉ so sánh tương đối.
