# Diabetes Multi-Agent Decision Support (prototype học tập)

Hệ đa agent lai: Deep Learning + Knowledge Graph/RAG (Neo4j) + Rule-based + Explanation + Coordinator (+ RL tùy chọn).
Môn: Phát triển các hệ thống thông minh – PTIT.

> Prototype học tập, KHÔNG phải hệ thống chẩn đoán/điều trị đã kiểm chứng lâm sàng.

## Chạy nhanh
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
python scripts/check_env.py
pytest -v
```

## Tiến độ
- [x] Giai đoạn 0: khởi tạo project
- [x] Giai đoạn 1: DL Prediction Agent (huấn luyện Keras + agent)
- [x] Giai đoạn 2: Neo4j KB (kb/DB_diabet.cypher) + KG/RAG Agent

## Knowledge Graph
```bash
python scripts/build_kb.py     # (tùy chọn) sinh lại kb/DB_diabet.cypher từ dữ liệu trong scripts/build_kb.py
python scripts/load_kb.py      # nạp KB vào Neo4j
python scripts/check_neo4j.py  # kiểm tra kết nối + nội dung
python scripts/try_kb.py       # hỏi thử KG/RAG Agent
```
