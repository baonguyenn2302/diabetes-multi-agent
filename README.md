# Diabetes AI - Multi-Agent Demo

Ứng dụng demo hỏi đáp về bệnh tiểu đường, kết hợp hệ thống điều phối nhiều Agent, truy xuất tài liệu y khoa và mô hình ước tính nguy cơ. Dự án gồm backend Flask/Python và giao diện React/Vite.

> **Giới hạn y tế:** Đây là sản phẩm demo/tham khảo, không phải công cụ chẩn đoán hay tư vấn điều trị và không thay thế chuyên gia y tế. Chỉ dùng dữ liệu giả lập; không nhập thông tin sức khỏe cá nhân.

Xem [SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md) để biết kiến trúc, luồng xử lý, dữ liệu và hướng dẫn cho AI Agent hoặc người viết báo cáo.

## Chức năng

- Hỏi đáp kiến thức về tiểu đường với các đoạn trích và nguồn tham khảo.
- Điều phối yêu cầu qua Coordinator đến Agent truy xuất tri thức, ước tính nguy cơ và rà soát nội dung.
- Ước tính nguy cơ bằng Keras khi người dùng cung cấp đủ 8 trường đầu vào hợp lệ.
- Hiển thị Agent trace, nguồn, cảnh báo và các trường còn thiếu.
- Lưu lịch sử hội thoại và trace vào SQLite theo phiên.

## Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Backend/API | Python 3.13, Flask |
| Frontend | React 19, Vite 8 |
| LLM cục bộ | Ollama |
| Mô hình ước tính | Keras/TensorFlow |
| Truy xuất vector | ChromaDB, Sentence Transformers |
| Tri thức đồ thị | Neo4j (tùy chọn) |
| Lịch sử ứng dụng | SQLite |

## Yêu cầu

- Python 3.13 được khuyến nghị (metadata model ghi nhận model được huấn luyện với Python 3.13).
- Node.js 20.19+ hoặc 22.12+ và npm (theo yêu cầu Vite 8).
- Ollama cài và chạy local để phân loại một số câu hỏi/tổng hợp câu trả lời.
- Các artifact model trong `models/` nếu cần chạy chức năng ước tính nguy cơ.
- Neo4j chỉ cần nếu muốn dùng truy xuất tri thức đồ thị; ChromaDB được dùng cho truy xuất tài liệu.

## Cài đặt và chạy

### 1. Cấu hình môi trường

Từ thư mục gốc:

```bash
cp .env.example .env
```

Mở `.env` và điều chỉnh nếu cần. Backend tự đọc `.env` ở thư mục gốc, đồng thời ưu tiên các biến môi trường đã có trong shell. Không commit thông tin xác thực.

Các biến thường dùng:

| Biến | Mặc định / ý nghĩa |
|---|---|
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434`; chỉ cho phép Ollama trên localhost |
| `OLLAMA_MODEL` | `llama3.2:3b` |
| `OLLAMA_TIMEOUT` | `90` giây |
| `FRONTEND_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` |
| `CHROMA_PATH` | `./chroma_db` |
| `SQLITE_PATH` | `./data/chat_history.sqlite3` |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Để trống/tùy chọn nếu không dùng Neo4j |

Nếu cần Ollama, khởi chạy Ollama và tải model đã cấu hình, ví dụ:

```bash
ollama pull llama3.2:3b
```

### 2. Cài Python và khởi chạy backend

```bash
python -m venv .venv
```

Kích hoạt môi trường ảo (`source .venv/bin/activate` trên macOS/Linux hoặc `.venv\Scripts\Activate.ps1` trong PowerShell), sau đó:

```bash
python -m pip install -r requirements.txt
cd backend
python app.py
```

Backend chạy tại `http://127.0.0.1:5000`.

### 3. Khởi chạy frontend

Trong terminal khác, từ thư mục gốc:

```bash
cd frontend
npm ci
```

Tùy chọn: sao chép `frontend/.env.example` thành `frontend/.env.local` và đặt `VITE_API_BASE_URL` nếu backend không ở địa chỉ mặc định. Sau đó:

```bash
npm run dev
```

Mở địa chỉ Vite hiển thị (thường là `http://localhost:5173`).

### Nạp tài liệu vào ChromaDB

Chỉ cần thực hiện nếu kho ChromaDB chưa có dữ liệu. Từ thư mục gốc, khi các dependency Python đã được cài:

```bash
python backend/scripts/ingest_knowledge.py
```

Lệnh này thay thế toàn bộ collection `diabetes_knowledge`, chỉ nạp các tài liệu được cho phép trong script. Việc tạo embedding có thể cần tải model Sentence Transformers lần đầu.

## Kiểm tra

Unit/API tests:

```bash
python -m pytest backend/tests
```

Smoke test tích hợp cần backend, Ollama và các dịch vụ/dữ liệu liên quan đang hoạt động:

```bash
python test_step6_integration.py
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Kiểm tra tình trạng dịch vụ:

```text
GET http://127.0.0.1:5000/api/health
GET http://127.0.0.1:5000/api/health?deep=1
```

Kiểm tra sâu sẽ thử tải model và truy vấn ChromaDB; vì vậy có thể chậm hơn chế độ mặc định.

## API chính

| Method | Đường dẫn | Mục đích |
|---|---|---|
| `POST` | `/api/chat` | Gửi câu hỏi và tùy chọn dữ liệu sức khỏe |
| `GET` | `/api/history?session_id=<id>&limit=20` | Đọc lịch sử một phiên (`limit`: 1–100) |
| `GET` | `/api/agents/status?session_id=<id>` | Đọc trace thực thi gần nhất |
| `GET` | `/api/health` | Kiểm tra trạng thái các thành phần |

Ví dụ body cho `/api/chat`:

```json
{
  "session_id": "demo-session",
  "message": "Tôi muốn đánh giá nguy cơ tiểu đường",
  "health_data": null
}
```

Khi đánh giá nguy cơ, `health_data` cần có đủ các trường `gender`, `smoking_history`, `age`, `hypertension`, `heart_disease`, `bmi`, `HbA1c_level`, `blood_glucose_level`. Các giá trị phân loại, khoảng số và đơn vị được khai báo trong `models/model_metadata.json`. Backend trả `missing_fields` khi thiếu dữ liệu và không gọi model trong trường hợp đó.

## Cấu trúc repository

```text
backend/                 Flask API, Coordinator, Agents, services và tests
  agents/                Coordinator và các Agent chuyên biệt
  routes/                Các endpoint API
  services/              Ollama, ChromaDB, Neo4j, Keras, SQLite
  prompts/               Prompt phân loại và tổng hợp
  tests/                 Unit và API tests
  scripts/               Nạp tài liệu và nạp tri thức đồ thị
  validators/            Kiểm tra dữ liệu sức khỏe
frontend/                Giao diện React/Vite
models/                  Model và metadata
data/knowledge/           Tài liệu nguồn và dữ liệu đồ thị
data/raw/                 Dataset dùng cho model/kiểm thử
scripts/                  Script huấn luyện
```

## Lưu ý khi chạy trong checkout hiện tại

- `backend/services/model_service.py` cần `models/preprocessor.pkl` cùng model và metadata. File này hiện không có trong thư mục `models/` của checkout; chức năng dự đoán sẽ báo model không khả dụng cho đến khi artifact phù hợp được cung cấp.
- Nếu `/api/health` báo ChromaDB chưa có collection/đoạn tri thức, chạy lệnh nạp tài liệu ở trên.
- Neo4j là tùy chọn. Khi Neo4j chưa cấu hình/không kết nối được, các quan hệ triệu chứng được đọc từ `data/knowledge/graph/triples.csv`; nguồn được đánh dấu `graph_csv`, không giả nhận là Neo4j.
- Ollama chạy local. Khi không khả dụng, một số yêu cầu có thể không được phân loại; phần tổng hợp có thể rơi về trích đoạn nguồn.
- Xem [SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md) để biết đầy đủ luồng hệ thống và các giới hạn của demo.
