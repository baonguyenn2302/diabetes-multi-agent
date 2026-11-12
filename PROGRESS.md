# Tiến độ dự án: Hệ đa agent hỗ trợ quyết định tiểu đường

**Môn:** Phát triển các hệ thống thông minh – PTIT
**Cập nhật lần cuối:** Giai đoạn 11 (báo cáo và demo) hoàn thành, chờ người làm xác nhận

> Quy ước: mỗi khi hoàn thành một giai đoạn và được xác nhận bằng kết quả test, thêm mục vào **Nhật ký**, đổi trạng thái trong **Tổng quan** và ghi số test. Chỉ sang giai đoạn tiếp theo khi test đạt và người làm xác nhận.

---

## 1. Tổng quan

| # | Giai đoạn | Trạng thái | Số test passed (tích lũy) |
|---|---|---|---|
| 0 | Khởi tạo project | ✅ Hoàn thành | 3 |
| 1 | DL Prediction Agent (huấn luyện Keras + agent) | ✅ Hoàn thành | 10 |
| 2 | Neo4j Knowledge Graph + KG/RAG Agent | ✅ Hoàn thành | 31 |
| 3 | Patient Data Agent | ✅ Hoàn thành, đã xác nhận | 64 |
| 4 | Rule-Based Agent | ✅ Hoàn thành, đã xác nhận | 64 |
| 5 | Coordinator Agent | ✅ Hoàn thành, đã xác nhận | 87 |
| 6 | Explanation Agent (template) | ✅ Hoàn thành, đã xác nhận | 108 |
| 7 | Monitoring / Audit Agent | ✅ Hoàn thành, đã xác nhận | 123 |
| 8 | API (FastAPI) và giao diện (Streamlit) | ✅ Hoàn thành, đã xác nhận | 133 |
| 9 | Kiểm thử và đánh giá toàn hệ thống | ✅ Hoàn thành, đã chạy trên máy (số liệu đã nhận) | 157 |
| 10 | RL Agent trong mô phỏng (tùy chọn) | ✅ Hoàn thành, đã chạy trên máy | 157 |
| 11 | Báo cáo và demo | ✅ Hoàn thành, chờ xác nhận | 157 |

**Chú thích:** ✅ hoàn thành · ⬜ chưa làm

---

## 2. Nhật ký

### Giai đoạn 0: Khởi tạo project ✅
- Cấu trúc thư mục, môi trường ảo, `AgentMessage` (theo mục 6.1 của tài liệu kiến trúc), `.env`, `scripts/check_env.py`.
- Nguyên tắc: agent không ném lỗi ra ngoài mà trả `status="error"` (failure awareness).

### Giai đoạn 1: DL Prediction Agent ✅
- **Dữ liệu:** 100.000 dòng, sau khi bỏ 3.854 dòng trùng còn 96.146 dòng; tỉ lệ dương tính 8,82%.
- **Đặc trưng (8 cột):** gender, age, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level. Nhãn: `diabetes` (nhị phân).
- **Mô hình:** Dense(64) → Dropout → Dense(32) → Dropout → Dense(1, sigmoid); chia 70/15/15, seed 42.
- **Kết quả trên tập test:** accuracy 0,970 · precision 0,933 · recall 0,712 · F1 0,807 · ROC-AUC 0,975 · ngưỡng 0,85 (chọn trên validation).
- **Ghi chú cho báo cáo:**
  - Dataset **không có nhãn loại 1 / loại 2**, nên model chỉ dự đoán có/không tiểu đường.
  - Ngưỡng 0,85 làm recall chỉ khoảng 0,71, bỏ sót khoảng 29% ca dương tính. Lý do hệ thống cần Rule Agent và cờ "cần chuyên gia xem xét".

### Giai đoạn 2: Neo4j Knowledge Graph + KG/RAG Agent ✅
- **KG trên Neo4j Aura:** 52 thực thể, 67 quan hệ, 19 nguồn (WHO, ADA 2021/2023/2026, Vinmec, Long Châu, Pharmacity, VnExpress, Tâm Anh). Nội dung diễn đạt lại, không chép nguyên văn.
- **Ngưỡng có cấu trúc trong KG:** HbA1c ≥ 6,5%; FPG ≥ 126 mg/dL; OGTT 2 giờ ≥ 200 mg/dL; random ≥ 200 mg/dL (có triệu chứng); tiền tiểu đường: HbA1c 5,7–6,4%, FPG 100–125 mg/dL, OGTT 140–199 mg/dL.
- **Kiểm thử:** 31 passed, gồm 2 test với Neo4j thật.
- **Hạn chế:** tri thức chưa được chuyên gia thẩm định. Sửa tay file `.cypher` sẽ làm test "file up to date" báo lỗi; hãy sửa `scripts/build_kb.py` rồi chạy lại.

### Giai đoạn 3: Patient Data Agent ✅
- **Mục tiêu:** kiểm tra và chuẩn hóa đầu vào trước khi đưa vào các agent khác.
- **Kiểm tra:** đủ 8 feature; số thực hữu hạn (không nhận NaN/inf); khoảng hợp lý (`VALUE_RANGES`); nhị phân chỉ 0 hoặc 1 (không nhận bool); categorical thuộc danh sách cho phép, không phân biệt hoa thường và được chuẩn hóa về đúng dạng dataset; số viết dấu phẩy (`5,8`) được chấp nhận.
- **Đầu ra:** lỗi gộp trong `error`, chi tiết từng lỗi trong `payload["errors"]`. Trường lạ được bỏ qua và liệt kê trong `ignored_fields`.
- **File:** `app/agents/data_agent.py`, `tests/test_data_agent.py` (13 test).
- **Sửa lỗi kèm theo:** `PatientRequest.features` trước đây khai báo `dict[str, float]` nên từ chối giá trị chữ như "Female". Đã đổi thành `dict[str, Any]`, có test kèm theo.

### Giai đoạn 4: Rule-Based Agent ✅
- **Ngưỡng đọc từ KG**, không hard-code: `RuleBasedAgent.from_runner(kg.query)` đọc quan hệ DIAGNOSES và INDICATES từ Neo4j. Nếu thiếu ngưỡng, agent trả lỗi rõ ràng và yêu cầu chạy lại `load_kb.py`.
- **Luật xét nghiệm:**
  - R01 HbA1c ≥ 6,5% (mức cao)
  - R02 HbA1c trong khoảng tiền tiểu đường, gồm cả khoảng 6,4–6,5% (mức trung bình)
  - R03 đường huyết ≥ 200 (cao)
  - R04 đường huyết 126–199 (trung bình, ghi chú cần làm rõ thời điểm đo)
  - R05 đường huyết 100–125 (thấp)
- **Yếu tố nguy cơ:** R06 tuổi ≥ 45; R07 BMI ≥ 30; R08 tăng huyết áp; R09 bệnh tim mạch; R10 hút thuốc (cờ tư vấn).
- **Mâu thuẫn với model (cần chuyên gia xem xét):**
  - C01: model dự đoán nguy cơ thấp nhưng xét nghiệm vượt ngưỡng chẩn đoán.
  - C02: model dự đoán nguy cơ cao nhưng HbA1c và đường huyết đều bình thường (yêu cầu cả hai giá trị có mặt).
- **Ghi chú:**
  - Tuổi 45 và BMI 30 không có trong KG nên khai báo trong `rule_agent.py`. Nếu muốn đưa vào KG, bổ sung vào `build_kb.py` và chạy lại.
  - Cột `blood_glucose_level` không rõ đo lúc đói hay ngẫu nhiên, nên cờ đường huyết luôn kèm ghi chú cần làm rõ.
  - Không có luật nào đưa ra thuốc hay liều dùng (có test kiểm tra).
- **File:** `app/agents/rule_agent.py`, `tests/test_rule_agent.py` (18 test), `tests/test_rule_agent_real.py` (1 test Neo4j thật).
- **Kiểm thử:** 64 passed tích lũy (trong đó sandbox đã chạy 54 test không cần TensorFlow, sklearn và Neo4j; phần còn lại cần chạy trên máy bạn).

### Giai đoạn 5: Coordinator Agent ✅ (đã xác nhận: 87 passed, try_coordinator chạy đúng 3 ca)
- **Mục tiêu:** điều phối các agent theo đúng 12 bước của mục 5.3 tài liệu kiến trúc.
- **Luồng:** Data → (dừng nếu lỗi) → DL → Rule → KG/RAG → Explain (nếu có) → Monitor (nếu có) → trả kết quả.
- **Quy tắc xử lý lỗi:**
  - Data lỗi: dừng, trả `status = "validation_error"`, không gọi model.
  - DL lỗi: Rule vẫn chạy với `prediction = None`, trả `status = "partial"`.
  - KG hoặc Rule lỗi: các phần còn lại vẫn trả về, `status = "partial"`.
  - Mọi exception trong agent đều được bắt và ghi vào `trace` và `errors`. Coordinator không ném lỗi ra ngoài `handle()`.
  - Lỗi của Monitor không làm hỏng kết quả.
- **Kết quả trả về:** `request_id`, `status` (ok / partial / validation_error / error), `prediction`, `rules`, `evidence`, `report`, `needs_human_review`, `errors`, `trace`. Giữ tách biệt prediction, rules và evidence theo mục 4.2.
- **Giao diện mong đợi cho các giai đoạn sau:**
  - Explainer: `run(request_id, outputs)` với `outputs = {"prediction", "rules", "knowledge"}` (là AgentMessage), trả `payload["report"]`.
  - Monitor: `record(request_id, trace, outcome)`.
- **File:** `app/coordinator.py`, `scripts/try_coordinator.py`, `tests/test_coordinator.py` (17 test với agent giả), `tests/test_coordinator_integration.py` (5 test với luồng thật, DL giả), `tests/test_coordinator_real.py` (1 test với model và Neo4j thật).
- **Kiểm thử:** sandbox chạy 76 test không cần TensorFlow, sklearn và Neo4j, đều đạt. Tổng số test trên máy người làm dự kiến 87 (64 cũ + 23 mới).
- **Ghi chú:** `build_default_coordinator()` nạp model thật và KB từ Neo4j. Khi chạy `scripts/try_coordinator.py`, nếu bước Rule trả lỗi "Thiếu ngưỡng" thì KB chưa được nạp.

### Giai đoạn 6: Explanation Agent (template) ✅ (đã xác nhận: 108 passed)
- Báo cáo 6 mục, sinh từ template, luôn kèm nguồn và ghi rõ không phải chẩn đoán xác định.
- File: `app/agents/explanation_agent.py`, `app/sources.py`, các test liên quan.

### Giai đoạn 7: Monitoring / Audit Agent ✅ (đã xác nhận: 123 passed)
- Ghi log từng request vào `logs/audit.jsonl` (không ghi giá trị đặc trưng bệnh nhân), có thống kê theo request và theo agent.
- Sau khi xác nhận, phát hiện test luồng thật ghi vào log thật. Đã sửa: test dùng thư mục tạm.

### Giai đoạn 8: API và giao diện ✅ (đã xác nhận: 133 passed)
- API FastAPI (`/assess`, `/health`, `/audit/summary`), giao diện Streamlit, lớp service tách riêng.
- Sau khi xác nhận, đã khôi phục project từ zip. Model huấn luyện lại cho đúng các chỉ số cũ (ROC-AUC 0,9749). KB trên Neo4j có 52 thực thể.

### Giai đoạn 9: Đánh giá toàn hệ thống ✅ (đã chạy trên máy: 146 passed)
- `evaluate_system.py` chạy thành công: số tính lại khớp với model card; ablation có kết quả; 30/30 ca nhất quán giữa Coordinator và batch; toàn bộ 30 ca trả trạng thái ok.

### Giai đoạn 10 đã chạy trên máy ✅
- `pytest -v`: 157 passed. `run_simulation.py` cho đúng bảng như sandbox (chính sách học được = quy tắc đơn giản, cùng tốt hơn ngẫu nhiên).

### Giai đoạn 11: Báo cáo và demo ✅ (chờ xác nhận)
- **Báo cáo:** `BAO_CAO.md`, theo cấu trúc tài liệu kiến trúc, dựa trên `reports/evaluation.md` và `reports/rl_simulation.md`.
- **Kịch bản demo 5 phút:** `KICH_BAN_DEMO.md`.
- **Phát hiện quan trọng từ đánh giá:** kết hợp DL với lớp Rule theo kiểu "DL dương hoặc luật cảnh báo" tăng recall từ 0,712 lên 0,811 nhưng làm precision giảm từ 0,933 xuống 0,246 (3.088 báo động thêm trên ca không có bệnh). Báo cáo nêu rõ điều này và đề xuất vai trò của Rule là cờ cần xem xét, không ghi đè quyết định của DL.
- **Thêm script:** `scripts/show_test_case.py <idx>` in dữ liệu của một ca trong tập test và kết quả hệ thống, dùng cho demo ca mâu thuẫn.
- **Kiểm thử:** script mới chưa chạy được trong sandbox (cần TensorFlow và Neo4j). Chạy thử bằng `python scripts/show_test_case.py 4547` trên máy bạn.

---

## 3. Việc cần người làm xác nhận

- [ ] Đặt lại mật khẩu Neo4j Aura và cập nhật `.env` (sẽ làm khi hoàn thành project).
- [x] Đã chạy `pytest -v` và đạt 64 passed, 0 skipped (giai đoạn 3–4).
- [x] Đã xác nhận Giai đoạn 3 và 4.
- [x] Chạy `pytest -v` đạt 87 passed và `python scripts/try_coordinator.py` đúng 3 ca.
- [x] Xác nhận Giai đoạn 5.
- [x] Chạy `pytest -v` đạt 108 passed và `python scripts/try_coordinator.py` in được báo cáo (giai đoạn 6).
- [x] Xác nhận Giai đoạn 6.
- [x] Chạy `pytest -v` đạt 123 passed (giai đoạn 7).
- [x] Xác nhận Giai đoạn 7.
- [x] Khôi phục project và chạy lại `pytest -v` đạt 133 passed.
- [ ] Chạy API và giao diện, gửi thử hai ca nguy cơ thấp và cao (tùy chọn, đã kiểm thử bằng TestClient).
- [x] Xác nhận Giai đoạn 8.
- [x] Chạy `python scripts/evaluate_system.py` (khớp model card, 30/30 nhất quán).
- [ ] Gửi tôi nội dung `reports/evaluation.md` để đưa số liệu vào báo cáo.
- [x] `pytest -v` đạt 146 passed.
- [x] Xác nhận Giai đoạn 9.
- [x] Chạy `python scripts/run_simulation.py` và `pytest -v` đạt 157 passed.
- [x] Xác nhận Giai đoạn 10.
- [ ] Xác nhận Giai đoạn 11 và quyết định cách trình bày kết quả Rule (xem BAO_CAO.md mục 6).
- [x] Chọn cách làm Explanation Agent (Giai đoạn 6): template.
- [ ] Quyết định Explanation Agent (Giai đoạn 6) dùng template hay LLM (LLM cần API key).

---

## 4. Cấu trúc thư mục hiện tại

```
diabetes-mas/
├── app/
│   ├── config.py, schemas.py, features.py, text_utils.py, kb_utils.py, sources.py
│   ├── coordinator.py, service.py, api.py, evaluation.py
│   └── agents/ (dl_agent.py, kg_rag_agent.py, data_agent.py, rule_agent.py, explanation_agent.py, monitoring_agent.py)
├── kb/DB_diabet.cypher
├── models/   (model.keras, preprocessor.joblib, model_meta.json, model_card.md)
├── data/     (diabetes_prediction_dataset.csv)
├── scripts/  (train_model, build_kb, load_kb, check_neo4j, try_kb, try_predict, try_coordinator, audit_summary, evaluate_system, run_simulation, show_test_case, check_env)
├── tests/    (157 test)
├── reports/  (evaluation.md, evaluation.json – tạo khi chạy đánh giá)
├── logs/     (audit.jsonl – tạo khi chạy)
├── sim/      (followup_env.py, rl_train.py – chỉ mô phỏng)
├── ui/       (streamlit_app.py)
└── pytest.ini, conftest.py, requirements.txt, .env.example, README.md, PROGRESS.md
```
