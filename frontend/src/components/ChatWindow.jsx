import AgentActivity from "./AgentActivity";
import SourceList from "./SourceList";

const STATUS_LABELS = {
  success: "Hoàn tất",
  needs_input: "Cần bổ sung thông tin",
  invalid_input: "Dữ liệu không hợp lệ",
  insufficient_evidence: "Chưa đủ nguồn tin cậy",
  error: "Lỗi",
};

// Backend trả error dạng chuỗi (400) hoặc không có error (503);
// frontend cũng tự tạo { message } khi fetch thất bại. Xử lý cả ba.
function errorText(error) {
  if (!error) return null;
  if (typeof error === "string") return error;
  return error.message || JSON.stringify(error);
}

function AssistantBody({ response }) {
  const {
    status,
    answer,
    sources,
    agent_trace,
    missing_fields,
    warnings,
    error,
  } = response;
  const err = errorText(error);

  return (
    <>
      {status && status !== "success" && (
        <p className={`status status-${status}`}>
          <small>{STATUS_LABELS[status] || status}</small>
        </p>
      )}
      {answer && <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p>}
      {err && <p className="error">{err}</p>}
      {missing_fields?.length > 0 && <p>Thiếu: {missing_fields.join(", ")}</p>}
      {warnings?.length > 0 && (
        <ul className="warnings">
          {warnings.map((w, i) => (
            <li key={i}>{w}</li>
          ))}
        </ul>
      )}
      <SourceList sources={sources} />
      <AgentActivity trace={agent_trace} />
    </>
  );
}

export default function ChatWindow({ messages, loading }) {
  return (
    <div className="chat-window">
      {messages.map((m, i) => (
        <div key={i} className={`message ${m.role}`}>
          {m.role === "user" ? (
            <p>{m.text}</p>
          ) : (
            <AssistantBody response={m.response} />
          )}
        </div>
      ))}
      {loading && <p className="loading">Đang xử lý...</p>}
    </div>
  );
}
