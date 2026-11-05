# Diabetes AI System --- Multi-Agent Demo

## Tài liệu đặc tả kiến trúc, phạm vi và lộ trình triển khai MVP trong 2--3 ngày

> **Mục đích tài liệu:** Đây là tài liệu nguồn để lập trình viên, AI
> coding assistant và các Agent đọc hiểu thống nhất mục tiêu, kiến trúc,
> trách nhiệm, công nghệ, luồng xử lý và tiêu chí hoàn thành demo.
>
> **Ưu tiên:** Hoàn thành một demo Multi-Agent chạy được, dễ quan sát và
> dễ thuyết trình. Không mở rộng tính năng ngoài phạm vi MVP nếu chưa
> hoàn thành luồng chính.

------------------------------------------------------------------------

## 1. Tổng quan dự án

### 1.1. Bài toán

Xây dựng hệ thống hỗ trợ hỏi đáp và cung cấp thông tin tham khảo về bệnh
tiểu đường. Người dùng có thể:

-   Đặt câu hỏi liên quan đến bệnh tiểu đường.
-   Cung cấp thông tin sức khỏe hoặc các chỉ số đầu vào.
-   Yêu cầu hệ thống ước tính nguy cơ dựa trên mô hình Deep Learning đã
    có (nếu dữ liệu đầu vào phù hợp).
-   Yêu cầu giải thích thông tin dựa trên kho tri thức.
-   Nhận câu trả lời tổng hợp, có nêu giới hạn và khuyến nghị an toàn.

Hệ thống là công cụ hỗ trợ thông tin, **không chẩn đoán bệnh, không thay
thế bác sĩ và không được khẳng định người dùng mắc/không mắc bệnh chỉ từ
dự đoán của mô hình**.

### 1.2. Mục tiêu demo môn Hệ đa Agent

Demo cần thể hiện rõ:

1.  Có nhiều Agent với vai trò và trách nhiệm riêng.
2.  Mỗi Agent có thể nhận nhiệm vụ, xử lý và trả kết quả theo một cấu
    trúc thống nhất.
3.  Các Agent giao tiếp thông qua Coordinator.
4.  Coordinator quyết định Agent nào cần được gọi dựa trên yêu cầu, thay
    vì luôn chạy một chuỗi cố định.
5.  Coordinator tổng hợp kết quả, xử lý lỗi hoặc kết quả thiếu và tạo
    phản hồi cuối.
6.  Giao diện hiển thị được tiến trình hoạt động của từng Agent để giảng
    viên quan sát.

**Không được chỉ chia một pipeline cố định thành nhiều hàm rồi gọi đó là
Multi-Agent.** Trong phạm vi demo, mức tự chủ có thể giới hạn bằng luật
và LLM; cần thể hiện được phân công nhiệm vụ, giao tiếp, phối hợp và lựa
chọn nhánh xử lý.

------------------------------------------------------------------------

## 2. Công nghệ đã thống nhất

Ưu tiên giữ công nghệ hiện có, không thay framework hoặc viết lại mô
hình nếu không cần thiết.

  -----------------------------------------------------------------------
  Thành phần              Công nghệ               Vai trò
  ----------------------- ----------------------- -----------------------
  Backend                 Python + Flask          API và tích hợp các
                                                  thành phần

  Frontend                React                   Giao diện chat và theo
                                                  dõi hoạt động Agent

  LLM                     Ollama chạy local       Phân tích yêu cầu,
                                                  reasoning có giới hạn,
                                                  tạo phản hồi

  Deep Learning           Keras                   Tái sử dụng mô hình dự
                                                  đoán tiểu đường hiện có

  Vector database         ChromaDB                Lưu và truy xuất tài
                                                  liệu bằng embedding

  Graph database          Neo4j                   Lưu và truy vấn quan hệ
                                                  tri thức

  Database ứng dụng       SQLite                  Lưu dữ liệu ứng
                                                  dụng/lịch sử cần thiết

  Dataset huấn luyện      CSV                     Dữ liệu phục vụ huấn
                                                  luyện/đánh giá mô hình

  Reinforcement Learning  Q-learning bằng NumPy   Hướng mở rộng; không
                                                  thuộc MVP 2--3 ngày

  Thử nghiệm AI           Jupyter Notebook        Thử nghiệm, phân tích
                                                  dữ liệu/mô hình

  IDE                     VS Code                 Môi trường phát triển
  -----------------------------------------------------------------------

### 2.1. Quy tắc công nghệ

-   Không gọi API LLM bên ngoài. LLM phải chạy qua Ollama local.
-   Không huấn luyện lại Deep Learning model trong giai đoạn demo nếu đã
    có model hoạt động.
-   Không thay Keras bằng PyTorch chỉ để triển khai demo. Tái sử dụng
    đúng framework của model hiện có.
-   Không bắt buộc dùng LangChain, CrewAI, AutoGen hoặc framework
    orchestration khác. Có thể viết Coordinator và Agent bằng Python
    thuần để dễ hiểu, dễ debug và kiểm soát luồng.
-   ChromaDB và Neo4j chỉ cần được tích hợp ở mức truy vấn hoạt động
    được; không dành thời gian xây dựng kho tri thức quy mô lớn trong
    MVP.
-   Q-learning không được đưa vào luồng quyết định chính trong 2--3
    ngày. Chỉ bổ sung sau khi MVP chạy ổn định và có định nghĩa rõ
    state, action, reward.

------------------------------------------------------------------------

## 3. Kiến trúc Multi-Agent đã chốt

### 3.1. Mô hình tổng thể

**Tên kiến trúc:** LLM-based Multi-Agent System with Coordinator
Architecture.

Thành phần:

-   **1 Coordinator Agent:** điều phối toàn bộ phiên làm việc.
-   **3 Specialized Agents:** mỗi Agent có một nhiệm vụ chuyên biệt.
-   **Shared tools/data services:** các công cụ và kho dữ liệu mà Agent
    được phép truy cập.
-   **Flask API:** cung cấp giao diện giao tiếp giữa React và hệ thống
    Agent.

``` mermaid
flowchart TD
    U[User / React UI] --> API[Flask API]
    API --> C[Coordinator Agent]

    C <-->|Task / Result| R[Risk Assessment Agent]
    C <-->|Task / Result| K[Medical Knowledge Agent]
    C <-->|Task / Result| S[Medical Advisor Agent]

    R --> M[Existing Keras Diabetes Model]
    K --> V[ChromaDB]
    K --> G[Neo4j]
    S --> L[Ollama Local LLM]
    C --> L

    C --> OUT[Final Response]
    OUT --> API
    API --> U
```

### 3.2. Coordinator Agent

**Vai trò:** đầu mối tiếp nhận yêu cầu, phân tích mục tiêu, quyết định
Agent phù hợp, quản lý kết quả và tổng hợp câu trả lời.

Trách nhiệm:

1.  Nhận câu hỏi từ người dùng.
2.  Xác định loại yêu cầu: hỏi kiến thức, hỏi triệu chứng, đánh giá nguy
    cơ, hoặc yêu cầu kết hợp.
3.  Tạo kế hoạch nhiệm vụ ngắn gọn.
4.  Chọn một hoặc nhiều Specialized Agent cần thiết.
5.  Gửi nhiệm vụ có cấu trúc cho Agent.
6.  Nhận và kiểm tra kết quả.
7.  Nếu thiếu dữ liệu, yêu cầu người dùng bổ sung hoặc gọi Agent phù
    hợp; không tự bịa dữ liệu.
8.  Tổng hợp câu trả lời cuối cùng.
9.  Ghi lại các sự kiện trạng thái để frontend hiển thị.

**Quy tắc lựa chọn Agent tối thiểu:**

  -----------------------------------------------------------------------
  Loại yêu cầu                        Agent được gọi
  ----------------------------------- -----------------------------------
  Hỏi kiến thức về tiểu đường         Medical Knowledge Agent

  Hỏi triệu chứng/yếu tố nguy cơ      Medical Knowledge Agent; có thể gọi
                                      Medical Advisor Agent

  Yêu cầu ước tính nguy cơ và đã có   Risk Assessment Agent + Medical
  đủ dữ liệu                          Knowledge Agent + Medical Advisor
                                      Agent

  Yêu cầu đánh giá nguy cơ nhưng      Coordinator yêu cầu bổ sung; chưa
  thiếu dữ liệu                       gọi model

  Câu hỏi ngoài phạm vi               Coordinator từ chối lịch sự hoặc
                                      thông báo giới hạn
  -----------------------------------------------------------------------

Coordinator có thể dùng LLM qua Ollama để phân tích ý định/lập kế hoạch,
nhưng phải kiểm tra kết quả bằng rule/allowlist. Không cho LLM tự ý gọi
hàm tùy ý.

### 3.3. Risk Assessment Agent

**Mục tiêu:** thực hiện dự đoán nguy cơ dựa trên model Keras hiện có.

Trách nhiệm:

1.  Nhận dữ liệu đầu vào có cấu trúc.
2.  Kiểm tra các trường bắt buộc, kiểu dữ liệu và miền giá trị.
3.  Nếu thiếu hoặc không hợp lệ, trả trạng thái `needs_input` hoặc
    `invalid_input`.
4.  Tiền xử lý dữ liệu bằng đúng preprocessor đã dùng khi huấn luyện
    model.
5.  Gọi model Keras đã huấn luyện.
6.  Trả xác suất/nhãn dự đoán và thông tin giới hạn.
7.  Không tự diễn giải kết quả thành chẩn đoán y khoa.

Quy tắc:

-   Không tự điền giá trị còn thiếu.
-   Không tự tạo dữ liệu sức khỏe.
-   Không dùng model nếu thiếu trường bắt buộc.
-   Không thay đổi thứ tự/cách mã hóa feature so với lúc huấn luyện.
-   Tên feature, đơn vị và ngưỡng phải lấy từ metadata/model pipeline
    hiện có; không tự suy đoán.

### 3.4. Medical Knowledge Agent

**Mục tiêu:** tìm kiếm kiến thức liên quan từ kho tri thức của dự án.

Trách nhiệm:

1.  Nhận câu hỏi hoặc chủ đề cần tìm.
2.  Truy vấn ChromaDB để tìm các đoạn tài liệu liên quan.
3.  Khi cần quan hệ giữa thực thể, truy vấn Neo4j.
4.  Trả các đoạn thông tin, nguồn/tên tài liệu và độ liên quan nếu có.
5.  Nếu không tìm thấy nguồn đủ phù hợp, báo rõ `insufficient_evidence`.

Quy tắc:

-   Không bịa nguồn, tên tài liệu hoặc nội dung trích dẫn.
-   Phân biệt dữ liệu truy xuất được với suy luận.
-   Không biến kết quả tìm kiếm thành kết luận chẩn đoán.
-   Trong MVP, nếu một trong hai database chưa sẵn sàng, Agent phải báo
    trạng thái rõ ràng; không giả vờ đã truy vấn thành công.

### 3.5. Medical Advisor Agent

**Mục tiêu:** rà soát tính an toàn, đầy đủ và nhất quán của nội dung tư
vấn trước khi trả cho người dùng.

Trách nhiệm:

1.  Nhận câu hỏi gốc và kết quả từ các Agent khác.
2.  Kiểm tra có thiếu dữ liệu quan trọng hay không.
3.  Kiểm tra câu trả lời có khẳng định quá mức hoặc biến dự đoán thành
    chẩn đoán hay không.
4.  Đề xuất hỏi thêm thông tin nếu cần.
5.  Nhắc người dùng tìm tư vấn y tế phù hợp khi có dấu hiệu đáng lo
    ngại.
6.  Trả kết quả kiểm tra và các cảnh báo cho Coordinator.

Medical Advisor Agent không được tự tạo ra dữ liệu khám nghiệm, kết quả
xét nghiệm hoặc nguồn y khoa.

------------------------------------------------------------------------

## 4. Cơ chế giao tiếp giữa các Agent

### 4.1. Nguyên tắc

-   Coordinator là đầu mối điều phối.
-   Specialized Agent không tự gọi lẫn nhau trong MVP; chúng gửi kết quả
    về Coordinator.
-   Mỗi Agent có input/output contract rõ ràng.
-   Dùng Python function call và dictionary/JSON nội bộ để truyền
    message. Không cần message broker trong demo.
-   Mỗi lần thực thi nên có `session_id`, `task_id`, `agent_name`,
    `status` để theo dõi.

### 4.2. Message format đề xuất

``` json
{
  "session_id": "session-example",
  "task_id": "task-example",
  "from": "coordinator",
  "to": "risk_assessment_agent",
  "task": "estimate_diabetes_risk",
  "input": {
    "features": {}
  },
  "status": "pending"
}
```

Kết quả Agent:

``` json
{
  "session_id": "session-example",
  "task_id": "task-example",
  "agent": "risk_assessment_agent",
  "status": "success",
  "result": {
    "prediction": null,
    "probability": null,
    "limitations": []
  },
  "error": null
}
```

Các `status` nên thống nhất:

-   `pending`: đang chờ.
-   `running`: đang thực hiện.
-   `success`: hoàn thành.
-   `needs_input`: cần người dùng bổ sung dữ liệu.
-   `insufficient_evidence`: không đủ bằng chứng.
-   `invalid_input`: dữ liệu không hợp lệ.
-   `error`: lỗi kỹ thuật.

Các giá trị `null` trong ví dụ chỉ là placeholder, không phải kết quả dự
đoán thực tế.

------------------------------------------------------------------------

## 5. Luồng demo bắt buộc

### 5.1. Kịch bản A --- Hỏi kiến thức

Người dùng: "Tiểu đường type 2 là gì?"

Luồng kỳ vọng:

1.  React gửi câu hỏi tới Flask.
2.  Coordinator xác định đây là câu hỏi kiến thức.
3.  Coordinator chỉ gọi Medical Knowledge Agent.
4.  Medical Knowledge Agent truy vấn ChromaDB; truy vấn Neo4j nếu cần
    quan hệ.
5.  Agent trả nội dung và nguồn tìm được.
6.  Coordinator tạo câu trả lời cuối.
7.  React hiển thị câu trả lời và trạng thái hoạt động.

Mục đích: chứng minh Coordinator có thể chỉ chọn Agent cần thiết, không
gọi tất cả Agent theo một pipeline cố định.

### 5.2. Kịch bản B --- Đánh giá nguy cơ

Người dùng: "Tôi muốn đánh giá nguy cơ tiểu đường."

Luồng kỳ vọng:

1.  Coordinator xác định cần đánh giá nguy cơ.
2.  Coordinator kiểm tra dữ liệu đầu vào đã đủ chưa.
3.  Nếu thiếu dữ liệu, hệ thống yêu cầu bổ sung; không gọi model với dữ
    liệu tự bịa.
4.  Khi dữ liệu hợp lệ, Coordinator gọi Risk Assessment Agent.
5.  Coordinator có thể gọi Medical Knowledge Agent để lấy thông tin giải
    thích liên quan.
6.  Coordinator gửi kết quả cho Medical Advisor Agent rà soát.
7.  Coordinator tổng hợp câu trả lời, nêu rõ đây chỉ là ước tính tham
    khảo.

Mục đích: chứng minh nhiều Agent phối hợp để hoàn thành một mục tiêu.

### 5.3. Kịch bản C --- Câu hỏi kết hợp

Người dùng: "Tôi thường khát nước và đi tiểu nhiều. Những dấu hiệu này
có liên quan đến tiểu đường không, và tôi cần làm gì?"

Luồng kỳ vọng:

1.  Coordinator xác định câu hỏi về triệu chứng và hướng dẫn.
2.  Gọi Medical Knowledge Agent để tìm thông tin.
3.  Gọi Medical Advisor Agent để rà soát lời khuyên an toàn.
4.  Không tự động gọi Risk Assessment Agent nếu người dùng chưa cung cấp
    dữ liệu cần thiết cho mô hình.
5.  Coordinator tổng hợp câu trả lời, nêu giới hạn và khuyến nghị phù
    hợp.

------------------------------------------------------------------------

## 6. Thiết kế backend và frontend tối thiểu

### 6.1. Backend Flask

Các endpoint đề xuất:

  -----------------------------------------------------------------------
  Endpoint                Method                  Mục đích
  ----------------------- ----------------------- -----------------------
  `/api/chat`             POST                    Nhận câu hỏi và chạy
                                                  Coordinator

  `/api/agents/status`    GET hoặc dữ liệu trả về Trạng thái các Agent
                          trong response          

  `/api/health`           GET                     Kiểm tra backend và các
                                                  dịch vụ phụ thuộc
  -----------------------------------------------------------------------

Request `/api/chat`:

``` json
{
  "session_id": "session-example",
  "message": "Tiểu đường type 2 là gì?",
  "health_data": null
}
```

Response đề xuất:

``` json
{
  "session_id": "session-example",
  "answer": "Nội dung trả lời cuối cùng...",
  "agent_trace": [
    {
      "agent": "coordinator",
      "status": "success",
      "message": "Đã xác định đây là câu hỏi kiến thức."
    },
    {
      "agent": "medical_knowledge_agent",
      "status": "success",
      "message": "Đã truy xuất tài liệu liên quan."
    }
  ],
  "sources": [],
  "warnings": []
}
```

Đây là hợp đồng API gợi ý. Điều chỉnh tên trường theo codebase hiện tại
nếu đã có quy ước khác; không tạo API trùng lặp không cần thiết.

### 6.2. Frontend React

MVP chỉ cần một màn hình chat:

-   Ô nhập câu hỏi.
-   Nút gửi.
-   Khu vực hiển thị câu trả lời.
-   Khu vực Agent Activity/Execution Trace.
-   Trạng thái từng Agent: pending/running/success/error.
-   Khu vực nguồn tham khảo.
-   Cảnh báo rằng hệ thống không thay thế chẩn đoán y khoa.

Không cần làm dashboard phức tạp, animation hoặc giao diện nhiều trang
trong giai đoạn này.

### 6.3. Hiển thị hoạt động Agent

Ví dụ:

``` text
Coordinator Agent
  ✓ Phân tích yêu cầu
  ✓ Chọn Medical Knowledge Agent

Medical Knowledge Agent
  ✓ Truy vấn ChromaDB
  ✓ Tổng hợp tài liệu

Medical Advisor Agent
  ✓ Kiểm tra nội dung

Coordinator Agent
  ✓ Tổng hợp phản hồi
```

Trace phải phản ánh hoạt động thực tế. Không tạo log giả chỉ để giao
diện trông giống Multi-Agent.

------------------------------------------------------------------------

## 7. Cấu trúc thư mục chuẩn

Cấu trúc dưới đây giữ nguyên công nghệ đã thống nhất ở mục 2 và bám theo
kiến trúc ở mục 3. Nguyên tắc tổ chức: **mỗi thư mục hoặc file có đúng một
người sở hữu**, ranh giới tách theo trách nhiệm (điều phối/backend với
dữ liệu, mô hình, tri thức và giao diện). Nhờ đó hai người làm song song
mà không sửa chung file, và khi merge không phát sinh xung đột.

``` text
diabetes-multi-agent/
├── README.md                      # Hướng dẫn cài đặt và chạy (A)
├── requirements.txt               # Khai báo đủ dependency ngay Ngày 1 (A)
├── .env.example                   # Khai báo đủ biến cấu hình ngay Ngày 1 (A)
├── .gitignore                     # Bỏ qua .env, data lớn, db, node_modules
│
├── backend/
│   ├── app.py                     # Flask app factory, đăng ký route, CORS (A)
│   ├── config.py                  # Đọc biến môi trường, không hard-code (A)
│   │
│   ├── routes/                    # Chỉ nhận request, gọi Coordinator (A)
│   │   ├── __init__.py
│   │   ├── chat.py                # POST /api/chat
│   │   ├── agents.py              # GET /api/agents/status
│   │   └── health.py              # GET /api/health
│   │
│   ├── agents/                    # Toàn bộ Agent
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Interface chung: run(task) -> result (A)
│   │   ├── registry.py            # Ánh xạ tên Agent -> class (A)
│   │   ├── coordinator.py         # Phân loại, chọn Agent, tổng hợp (A)
│   │   ├── medical_advisor_agent.py    # Rà soát an toàn nội dung (A)
│   │   ├── risk_assessment_agent.py    # Gọi model Keras (B)
│   │   └── medical_knowledge_agent.py  # Truy vấn ChromaDB/Neo4j (B)
│   │
│   ├── services/                  # Kết nối hạ tầng, không chứa logic Agent
│   │   ├── __init__.py
│   │   ├── ollama_service.py      # Gọi LLM local, timeout, lỗi có kiểm soát (A)
│   │   ├── sqlite_service.py      # Lưu lịch sử phiên và trace (A)
│   │   ├── model_service.py       # Load Keras, preprocessor, metadata (B)
│   │   ├── chroma_service.py      # Kết nối và truy vấn ChromaDB (B)
│   │   └── neo4j_service.py       # Kết nối và truy vấn Neo4j (B)
│   │
│   ├── validators/                # Kiểm tra dữ liệu đầu vào sức khỏe (B)
│   │   ├── __init__.py
│   │   └── health_input.py
│   │
│   ├── schemas/                   # Hợp đồng dữ liệu giữa các thành phần (A, khóa Ngày 1)
│   │   ├── __init__.py
│   │   └── agent_messages.py      # Task, Result, status, error
│   │
│   ├── prompts/                   # Prompt tách khỏi code để dễ chỉnh
│   │   ├── coordinator_prompt.txt       (A)
│   │   ├── advisor_prompt.txt           (A)
│   │   └── knowledge_prompt.txt         (B)
│   │
│   └── tests/
│       ├── test_coordinator.py    # Dùng mock Agent, không cần B (A)
│       ├── test_api.py            # Kiểm tra contract API (A)
│       ├── test_advisor.py        # (A)
│       ├── test_risk_agent.py     # Chạy độc lập, không cần Coordinator (B)
│       └── test_knowledge_agent.py     # (B)
│
├── frontend/                      # React (B)
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── main.jsx               # Điểm vào ứng dụng
│       ├── App.jsx
│       ├── api/
│       │   └── chatApi.js         # Toàn bộ lời gọi HTTP tới Flask
│       ├── mocks/
│       │   └── sampleResponses.js # Dữ liệu giả theo đúng contract, dùng khi chưa có backend
│       ├── components/
│       │   ├── ChatWindow.jsx
│       │   ├── MessageInput.jsx
│       │   ├── HealthDataForm.jsx     # Nhập dữ liệu khi cần đánh giá nguy cơ
│       │   ├── AgentActivity.jsx      # Trace và trạng thái từng Agent
│       │   ├── SourceList.jsx
│       │   └── SafetyBanner.jsx       # Cảnh báo không thay thế chẩn đoán
│       └── styles/
│
├── data/                          # (B)
│   ├── raw/                       # CSV gốc để huấn luyện/đánh giá
│   ├── processed/                 # Dữ liệu sau tiền xử lý
│   ├── knowledge/                 # Tài liệu tiểu đường đưa vào ChromaDB
│   └── sample/                    # Dữ liệu demo nhỏ cho ba kịch bản
│
├── models/                        # (B) Model Keras và metadata đã có, không huấn luyện lại
│   ├── diabetes_mlp.keras
│   ├── preprocessor.pkl
│   └── model_metadata.json        # Tên feature, thứ tự, đơn vị, ngưỡng
│
├── scripts/                       # Công cụ chạy một lần hoặc kiểm tra hạ tầng
│   ├── check_services.py          # Kiểm tra Ollama, ChromaDB, Neo4j, model (A)
│   ├── ingest_knowledge.py        # Nạp tài liệu vào ChromaDB (B)
│   └── load_neo4j.py              # Nạp quan hệ tri thức vào Neo4j (B)
│
├── notebooks/                     # Thử nghiệm Jupyter, không là code chạy chính (B)
│
└── docs/
    ├── architecture.md            # Sơ đồ và mô tả kiến trúc (A)
    ├── agent_contracts.md         # Hợp đồng message và status, khóa Ngày 1 (A)
    ├── frontend.md                # Hướng dẫn chạy giao diện (B)
    ├── data_setup.md              # Cách chuẩn bị dữ liệu và model (B)
    └── demo_script.md             # Kịch bản thuyết trình ba tình huống (B)
```

### 7.1. Phân quyền sở hữu

  -----------------------------------------------------------------------
  Người                  Phạm vi chính                  Thư mục/file sở hữu
  ---------------------- ------------------------------ -----------------
  **Người A ---          Điều phối, giao tiếp Agent,    `backend/app.py`,
  Backend & Orchestration** API, LLM, kiểm soát an      `config.py`,
                         toàn                           `routes/`,
                                                        `agents/coordinator.py`,
                                                        `agents/base_agent.py`,
                                                        `agents/registry.py`,
                                                        `agents/medical_advisor_agent.py`,
                                                        `services/ollama_service.py`,
                                                        `services/sqlite_service.py`,
                                                        `schemas/`,
                                                        `prompts/coordinator_prompt.txt`,
                                                        `prompts/advisor_prompt.txt`,
                                                        `scripts/check_services.py`,
                                                        `requirements.txt`,
                                                        `.env.example`, `README.md`,
                                                        `docs/architecture.md`,
                                                        `docs/agent_contracts.md`,
                                                        test của A

  **Người B ---          Dữ liệu, mô hình, tri thức,    `agents/risk_assessment_agent.py`,
  ML, Knowledge & UI**   giao diện                      `agents/medical_knowledge_agent.py`,
                                                        `services/model_service.py`,
                                                        `services/chroma_service.py`,
                                                        `services/neo4j_service.py`,
                                                        `validators/`,
                                                        `prompts/knowledge_prompt.txt`,
                                                        `scripts/ingest_knowledge.py`,
                                                        `scripts/load_neo4j.py`,
                                                        `data/`, `models/`,
                                                        `notebooks/`, `frontend/`,
                                                        `docs/frontend.md`,
                                                        `docs/data_setup.md`,
                                                        `docs/demo_script.md`,
                                                        test của B
  -----------------------------------------------------------------------

### 7.2. File dùng chung và cách tránh xung đột

Các file dưới đây có thể ảnh hưởng cả hai người. Quy tắc: **khai báo đầy
đủ trong buổi sáng Ngày 1, sau đó khóa**. Chỉ được thêm trường mới, không
đổi tên, không xóa trường đã có.

-   `schemas/agent_messages.py` và `docs/agent_contracts.md`: chốt tên
    field, tên `status`, cấu trúc `result` và `error`. Người B đọc để viết
    Agent và frontend.
-   `requirements.txt`: Người B gửi danh sách thư viện (ví dụ `tensorflow`
    hoặc `keras`, `chromadb`, `neo4j`) trước 10:00 Ngày 1. Người A ghi vào
    file ngay trong buổi sáng, nhờ vậy về sau không ai sửa file này nữa.
-   `.env.example`: khai báo sẵn toàn bộ biến cấu hình của cả hai phía, kể
    cả `CHROMA_PATH`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`,
    `OLLAMA_MODEL`, `SQLITE_PATH`.
-   `agents/registry.py`: liệt kê sẵn năm Agent. Các file Agent đều được
    tạo dạng stub từ sáng Ngày 1, nên import không bao giờ lỗi dù người
    kia chưa xong.

### 7.3. Nguyên tắc giữ độc lập giữa hai phần

-   **Stub trước, code sau.** Mỗi Agent có file stub trả `status: "error"`
    kèm thông báo "chưa triển khai". Stub này không giả kết quả và chỉ là
    chỗ giữ vị trí; người sở hữu thay phần thân hàm sau.
-   **Người A test Coordinator bằng mock Agent.** Người B test Agent bằng
    script riêng hoặc pytest, không cần Flask hay Coordinator. Hai bên
    chỉ gặp nhau khi merge.
-   **Frontend làm việc với dữ liệu mock.** `mocks/sampleResponses.js` tuân
    theo đúng contract trong `docs/agent_contracts.md`, nên giao diện không
    cần backend chạy để phát triển.
-   **Tách nhánh theo người.** `feature/backend-orchestration` (A),
    `feature/knowledge-ml` (B), `feature/frontend-react` (B). Tất cả merge
    qua `develop`, `main` chỉ nhận bản đã kiểm thử ở cuối Ngày 3.
-   **Sửa file của người khác:** không tự sửa. Mở một PR nhỏ, báo người sở
    hữu, và chỉ merge khi họ đồng ý.

------------------------------------------------------------------------

## 8. Lộ trình hoàn thành trong 2--3 ngày (2 người)

### 8.0. Quy tắc làm việc chung

1.  Mỗi người chỉ commit vào thư mục của mình (mục 7.1).
2.  Mỗi sáng và trước mỗi lần merge, pull `develop` và rebase nhánh.
3.  Chỉ merge vào `develop` tại hai thời điểm cố định: **12:00** và
    **17:00** mỗi ngày. Các thời điểm khác chỉ làm việc trên nhánh.
4.  Contract (mục 7.2) khóa lúc 11:00 Ngày 1. Sau đó mọi thay đổi phải
    tương thích ngược.
5.  Không merge khi test của phần mình chưa pass.

### Ngày 1 --- Khung dự án, backend điều phối và Agent đầu tiên

**Mục tiêu cuối ngày:** Coordinator chạy được với Agent thật ở luồng hỏi
kiến thức. Agent Risk Assessment đã gọi được model Keras độc lập.

**Buổi sáng (cả hai, khoảng 08:30--11:00)**

-   [ ] Đọc repository hiện tại, liệt kê module, model, database có sẵn.
-   [ ] Kiểm tra Ollama (`ollama list`) và model đã tải.
-   [ ] Load thử model Keras, preprocessor và `model_metadata.json`; ghi
    lại tên feature, thứ tự và miền giá trị.
-   [ ] Thống nhất `docs/agent_contracts.md`, các status và field bắt buộc.
-   [ ] Người B gửi danh sách thư viện cho `requirements.txt` trước 10:00.
-   [ ] **Người A** push skeleton cấu trúc mục 7, các stub Agent,
    `requirements.txt`, `.env.example` và `schemas/` lên `develop` trước
    11:00.
-   [ ] Khóa contract lúc 11:00.

**Người A --- chiều Ngày 1**

-   [ ] Viết `base_agent.py`: interface `run(task) -> result`, hằng số
    status.
-   [ ] Viết `schemas/agent_messages.py`: kiểm tra task và result đúng
    contract.
-   [ ] Viết `registry.py` và `coordinator.py` với phân loại theo luật
    (từ khóa) và bảng chọn Agent ở mục 3.2. Chưa cần LLM.
-   [ ] Viết `ollama_service.py` với timeout và xử lý lỗi; `coordinator`
    chỉ dùng LLM để phân loại ý định khi luật không rõ, và kết quả vẫn qua
    allowlist.
-   [ ] Viết `routes/chat.py`, `app.py`, endpoint `/api/chat` dùng stub.
-   [ ] Viết `tests/test_coordinator.py` với mock Agent.

**Người B --- chiều Ngày 1**

-   [ ] Viết `services/model_service.py`: load model, preprocessor, metadata
    và hàm dự đoán.
-   [ ] Viết `validators/health_input.py`: kiểm tra trường bắt buộc, kiểu,
    miền giá trị theo metadata.
-   [ ] Hoàn thiện `risk_assessment_agent.py`: validate → `needs_input` hoặc
    `invalid_input` → tiền xử lý → predict → `success` kèm `limitations`.
-   [ ] Viết `scripts/ingest_knowledge.py` và `services/chroma_service.py`;
    nạp tài liệu trong `data/knowledge/`.
-   [ ] Hoàn thiện `medical_knowledge_agent.py`: truy vấn ChromaDB, trả
    nguồn; báo `insufficient_evidence` khi không đủ.
-   [ ] Stub `neo4j_service.py`: nếu chưa kết nối được thì trả trạng thái
    `unavailable` rõ ràng, không giả vờ đã truy vấn.
-   [ ] Viết `test_risk_agent.py` và `test_knowledge_agent.py` chạy độc lập
    (dữ liệu hợp lệ, thiếu trường, sai miền giá trị).

**Điểm đồng bộ 17:00 (merge)**

-   [ ] Người B merge `feature/knowledge-ml` vào `develop`.
-   [ ] Người A merge `feature/backend-orchestration` vào `develop`, rồi
    chạy kịch bản A qua `/api/chat` với Agent thật.

**Definition of Done ngày 1:**

-   Coordinator chọn được Agent theo loại yêu cầu (đã kiểm thử bằng mock).
-   Luồng hỏi kiến thức chạy từ `/api/chat` đến ChromaDB và trả nguồn.
-   Risk Assessment Agent chạy được với dữ liệu hợp lệ và xử lý đúng khi
    thiếu dữ liệu.
-   Lỗi hoặc thiếu dữ liệu không làm backend crash.

### Ngày 2 --- Điều phối nhiều Agent và giao diện React

**Mục tiêu cuối ngày:** Ba kịch bản chạy được qua API, người dùng thao tác
trên React và thấy hoạt động của từng Agent.

**Người A --- cả ngày**

-   [ ] Viết `medical_advisor_agent.py`: kiểm tra thiếu dữ liệu, câu khẳng
    định quá mức, biến dự đoán thành chẩn đoán, dấu hiệu cần gặp bác sĩ.
    Có thể dùng Ollama để rà soát, nhưng luôn kiểm tra đầu ra bằng luật.
-   [ ] Mở rộng Coordinator cho kịch bản B (Risk → Knowledge → Advisor) và
    kịch bản C (Knowledge → Advisor, không gọi Risk).
-   [ ] Khi thiếu dữ liệu, Coordinator trả danh sách trường cần bổ sung và
    không gọi model.
-   [ ] Viết `routes/agents.py` và `routes/health.py`; `health` kiểm tra
    Ollama, model, ChromaDB, Neo4j và trả trạng thái từng dịch vụ.
-   [ ] Ghi trace và lịch sử phiên vào SQLite qua `sqlite_service.py`.
-   [ ] Viết `test_advisor.py` và `test_api.py`.

**Người B --- cả ngày**

-   [ ] Viết `mocks/sampleResponses.js` theo đúng contract cho ba kịch bản
    và cả trường hợp thiếu dữ liệu, lỗi dịch vụ.
-   [ ] Xây `api/chatApi.js`, `App.jsx`, `ChatWindow.jsx`,
    `MessageInput.jsx`, `SafetyBanner.jsx`, chạy hoàn toàn với mock.
-   [ ] Viết `AgentActivity.jsx` hiển thị trạng thái pending, running,
    success, error theo trace thực tế; `SourceList.jsx` hiển thị nguồn.
-   [ ] Viết `HealthDataForm.jsx` cho kịch bản đánh giá nguy cơ.
-   [ ] Sau khi Người A báo `/api/chat` ổn định (khoảng 14:00), đổi cấu
    hình base URL và kiểm thử với backend thật.
-   [ ] Nếu môi trường cho phép, chạy `load_neo4j.py` và bật truy vấn Neo4j
    trong `medical_knowledge_agent.py`; nếu không, giữ trạng thái
    `unavailable` đã làm ngày 1.

**Điểm đồng bộ 12:00 và 17:00**

-   [ ] 12:00: Người B merge `feature/frontend-react` ở trạng thái chạy với
    mock vào `develop` để người A thấy giao diện.
-   [ ] 17:00: Người A merge `feature/backend-orchestration`. Cả hai kiểm
    thử kịch bản A, B, C trên giao diện thật.

**Definition of Done ngày 2:**

-   Demo được trên giao diện với ít nhất hai luồng có cách chọn Agent khác
    nhau.
-   Có một luồng nhiều Agent phối hợp (kịch bản B hoặc C).
-   Trace phản ánh đúng hoạt động thực tế.
-   Không có kết quả model giả hoặc nguồn trích dẫn giả.
-   Thiếu dữ liệu và lỗi dịch vụ hiển thị đúng trạng thái.

### Ngày 3 --- Ổn định, tài liệu và chuẩn bị thuyết trình

**Mục tiêu cuối ngày:** Demo ổn định, khởi động được theo hướng dẫn, và
mỗi người giải thích được phần mình phụ trách.

**Người A**

-   [ ] Kiểm tra timeout, exception và input không hợp lệ ở mọi route.
-   [ ] Kiểm tra Agent trả kết quả thiếu hoặc lỗi; Coordinator tổng hợp
    được phản hồi có cảnh báo.
-   [ ] Chuẩn hóa log và trạng thái Agent.
-   [ ] Viết `README.md`: cài đặt, chạy backend, chạy `check_services.py`.
-   [ ] Hoàn thiện `docs/architecture.md`.

**Người B**

-   [ ] Xử lý trạng thái loading, lỗi và trống trên giao diện.
-   [ ] Viết `docs/frontend.md` và `docs/data_setup.md`.
-   [ ] Chuẩn bị `data/sample/` cho ba kịch bản demo.
-   [ ] Viết `docs/demo_script.md` (kịch bản 3--5 phút).
-   [ ] Chụp ảnh hoặc quay video demo dự phòng.

**Cả hai (cuối ngày)**

-   [ ] Tập demo hai lần; tắt thử Ollama hoặc ChromaDB để kiểm tra phản hồi
    lỗi.
-   [ ] Ngày 3, 17:00: merge `develop` vào `main`, gắn tag `v1.0-demo`.

**Phân công thuyết trình:** Người A giải thích Coordinator, cách chọn Agent
và giao tiếp qua message contract. Người B giải thích các Agent chuyên môn
(model, RAG, Knowledge Graph) và giao diện trace.

**Definition of Done ngày 3:**

-   Có thể khởi động project theo `README.md`.
-   Ba kịch bản demo chạy được.
-   Giải thích được nhiệm vụ từng Agent và cách chúng giao tiếp.
-   Chỉ ra được Coordinator đã chọn Agent dựa trên loại yêu cầu.
-   Có phương án xử lý khi dịch vụ phụ thuộc không khả dụng.

### Phương án rút gọn nếu chỉ còn 2 ngày

Gộp Ngày 3 vào Ngày 2 và giữ nguyên thứ tự ưu tiên:

1.  Coordinator và Medical Knowledge Agent chạy được qua `/api/chat`.
2.  Risk Assessment Agent gọi được model có sẵn.
3.  Medical Advisor Agent kiểm tra đầu ra ở mức cơ bản.
4.  React hiển thị chat và trace.
5.  Kiểm thử hai kịch bản: hỏi kiến thức và đánh giá nguy cơ.

Nếu thời gian thiếu, giảm phạm vi giao diện và dữ liệu demo; **không bỏ
cơ chế điều phối và giao tiếp giữa các Agent** vì đó là trọng tâm bài tập.

------------------------------------------------------------------------

## 9. Tiêu chí nghiệm thu MVP

  Mã      Tiêu chí                                    Mức độ
  ------- ------------------------------------------- ----------------------------------
  AC-01   Có Coordinator Agent                        Bắt buộc
  AC-02   Có 3 Specialized Agent riêng biệt           Bắt buộc
  AC-03   Có message/input/output contract            Bắt buộc
  AC-04   Coordinator lựa chọn Agent theo yêu cầu     Bắt buộc
  AC-05   Có ít nhất một luồng phối hợp nhiều Agent   Bắt buộc
  AC-06   Tích hợp Ollama local                       Bắt buộc
  AC-07   Kết nối model Keras hiện có                 Mục tiêu MVP
  AC-08   Truy vấn ChromaDB                           Mục tiêu MVP
  AC-09   Truy vấn Neo4j                              Mục tiêu nếu môi trường sẵn sàng
  AC-10   React hiển thị chat và hoạt động Agent      Bắt buộc
  AC-11   Có xử lý thiếu dữ liệu và lỗi dịch vụ       Bắt buộc
  AC-12   Có cảnh báo không thay thế chẩn đoán        Bắt buộc
  AC-13   Tích hợp Q-learning                         Ngoài phạm vi
  AC-14   Multi-Agent framework bên ngoài             Không bắt buộc

------------------------------------------------------------------------

## 10. Các nguyên tắc bắt buộc cho AI Coding Assistant / Agent

Khi đọc tài liệu này và thực hiện công việc trong repository, hãy tuân
thủ:

1.  **Đọc code trước khi sửa.** Kiểm tra cấu trúc thư mục, dependency,
    file cấu hình, API, model và database hiện tại.
2.  **Không tự giả định repository.** Chỉ kết luận một
    module/model/database đã tồn tại sau khi kiểm tra file hoặc chạy
    thử.
3.  **Không viết lại phần đang hoạt động.** Tái sử dụng code và model có
    sẵn.
4.  **Không thay đổi stack đã thống nhất** nếu chưa có lý do kỹ thuật rõ
    ràng và chưa được người dùng chấp thuận.
5.  **Không gọi LLM bên ngoài.** Chỉ dùng Ollama local.
6.  **Không bịa kết quả.** Không tạo prediction, nguồn tài liệu, trạng
    thái truy vấn hoặc log hoạt động giả.
7.  **Không làm quá phạm vi.** Ưu tiên MVP chạy được trước tính năng
    nâng cao.
8.  **Giữ interface giữa các Agent nhất quán.** Mọi Agent phải có input,
    output, status và error rõ ràng.
9.  **Xử lý lỗi có kiểm soát.** Một Agent lỗi không được làm toàn bộ hệ
    thống sập nếu có thể trả trạng thái lỗi phù hợp.
10. **Không để LLM thực thi tùy ý.** Tool phải nằm trong allowlist và
    được gọi qua code có kiểm soát.
11. **Không đưa Q-learning vào MVP** trừ khi toàn bộ luồng Multi-Agent
    đã hoạt động và còn đủ thời gian.
12. **Sau mỗi thay đổi, chạy kiểm thử phù hợp** và báo rõ file đã sửa,
    chức năng đã hoàn thành, lệnh kiểm thử và lỗi còn tồn tại.

### Cách AI assistant nên bắt đầu

Trước khi code, hãy:

1.  Liệt kê cấu trúc repository.
2.  Xác định backend/frontend hiện tại.
3.  Xác định vị trí model Keras, preprocessor và metadata.
4.  Xác định cấu hình Ollama, ChromaDB, Neo4j và SQLite.
5.  Đối chiếu với kiến trúc trong tài liệu.
6.  Lập danh sách phần có thể tái sử dụng và phần còn thiếu.
7.  Đề xuất thứ tự chỉnh sửa ít rủi ro nhất.
8.  Chỉ bắt đầu sửa code sau khi đã hiểu luồng hiện tại; không tạo lại
    project từ đầu.

------------------------------------------------------------------------

## 11. Kịch bản thuyết trình ngắn

**Mở đầu:** Đây là hệ thống Multi-Agent hỗ trợ hỏi đáp và cung cấp thông
tin tham khảo về bệnh tiểu đường. Hệ thống có một Coordinator và ba
Agent chuyên biệt.

**Demo 1 --- Hỏi kiến thức:** Người dùng hỏi một câu về tiểu đường.
Coordinator chọn Medical Knowledge Agent để truy xuất thông tin và trả
lời.

**Demo 2 --- Đánh giá nguy cơ:** Người dùng cung cấp dữ liệu.
Coordinator gọi Risk Assessment Agent để sử dụng mô hình Deep Learning,
sau đó gọi Medical Knowledge Agent và Medical Advisor Agent để bổ sung,
rà soát trước khi tổng hợp.

**Demo 3 --- Quan sát phối hợp:** Mở Agent Activity để cho thấy nhiệm vụ
được giao, kết quả trả về và trạng thái từng Agent.

**Kết luận:** Hệ thống thể hiện phân công nhiệm vụ, giao tiếp, phối hợp
và điều phối giữa nhiều Agent; các công cụ ML, RAG và Knowledge Graph
cung cấp năng lực chuyên môn cho các Agent.

------------------------------------------------------------------------

## 12. Những điểm không được hiểu nhầm

-   DiabetesMLP/Keras model là mô hình dự đoán, **không phải một
    Agent**.
-   ChromaDB và Neo4j là cơ sở dữ liệu/công cụ truy xuất, **không phải
    Agent**.
-   Ollama là nền tảng chạy LLM local, **không tự động đồng nghĩa với AI
    Agent**.
-   Một hàm Python gọi model không tự động trở thành Agent. Agent cần có
    vai trò, nhiệm vụ, input/output và cơ chế ra quyết định hoặc thực
    hiện nhiệm vụ.
-   Coordinator là thành phần điều phối; không nhất thiết phải là một
    LLM riêng.
-   Ba Agent chuyên biệt có thể dùng chung một Ollama model nhưng phải
    có system prompt, công cụ và trách nhiệm riêng.
-   Multi-Agent không đồng nghĩa bắt buộc phải có Q-learning.
-   Demo ưu tiên sự phối hợp thực chất và khả năng giải thích, không ưu
    tiên số lượng Agent.

------------------------------------------------------------------------

## 13. Trạng thái quyết định

  -----------------------------------------------------------------------
  Nội dung                            Quyết định
  ----------------------------------- -----------------------------------
  Bài toán demo                       Hỏi đáp và hỗ trợ đánh giá nguy cơ
                                      tiểu đường

  Kiến trúc                           Coordinator + 3 Specialized Agents

  Coordinator                         Phân tích, lựa chọn, giao nhiệm vụ,
                                      tổng hợp

  Agent 1                             Risk Assessment Agent

  Agent 2                             Medical Knowledge Agent

  Agent 3                             Medical Advisor Agent

  LLM                                 Ollama local, không dùng API bên
                                      ngoài

  Deep Learning                       Tái sử dụng model Keras hiện có

  Vector DB                           ChromaDB

  Graph DB                            Neo4j

  Backend                             Python Flask

  Frontend                            React

  Database ứng dụng                   SQLite

  Q-learning                          Để ngoài MVP 2--3 ngày

  Thời hạn                            2 ngày cho MVP cốt lõi; ngày thứ 3
                                      để ổn định và chuẩn bị demo
  -----------------------------------------------------------------------

**Thứ tự ưu tiên cao nhất:** hiểu codebase hiện tại → Coordinator →
Agent contracts → Specialized Agents → tích hợp model/database → React
trace → kiểm thử và thuyết trình.
