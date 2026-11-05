# Diabetes AI – React Frontend

Giao diện demo React + Vite kết nối Flask Coordinator API.

## Chạy trên Windows 11

Yêu cầu Node.js hỗ trợ Vite 8 (Node 20.19+ hoặc 22.12+). Backend Flask phải chạy ở http://127.0.0.1:5000.

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Mở địa chỉ được Vite hiển thị (thường http://localhost:5173).

## API

- `POST /api/chat` body `{ session_id, message, health_data }`; `health_data` bằng `null` khi hỏi kiến thức, hoặc object 8 feature khi đánh giá nguy cơ.
- `GET /api/history?session_id=...` đọc lịch sử đã lưu SQLite.
- `GET /api/health` kiểm tra backend.

Frontend hiển thị `answer`, `status`, `agent_trace`, `sources`, `warnings` và `missing_fields` của Coordinator response. Không sử dụng mock trong phiên bản tích hợp. Nút **Phiên mới** tạo session ID mới. Session ID được lưu trong sessionStorage, nên làm mới trang trong cùng tab vẫn truy xuất lại được lịch sử của phiên hiện tại. Dùng nút **Tải lịch sử** để hiển thị lại hội thoại; **Phiên mới** tạo mã mới.

Chỉ sử dụng dữ liệu giả lập, không nhập thông tin sức khỏe cá nhân.
