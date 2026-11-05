import SourceList from "./SourceList";

function AssistantBody({ response }) {
  const { status, result = {}, error } = response;

  if (status === "success" && result.sources) {
    return (
      <>
        <p>Tìm thấy {result.sources.length} nguồn liên quan:</p>
        <SourceList sources={result.sources} />
        <small>{result.disclaimer}</small>
      </>
    );
  }

  if (status === "success" && result.probability !== undefined) {
    return (
      <>
        <p>
          Kết quả ước tính của model: {(result.probability * 100).toFixed(1)}%
          (ngưỡng {result.threshold}).
        </p>
        <ul>
          {(result.limitations || []).map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
      </>
    );
  }

  if (status === "insufficient_evidence") {
    return <p>{result.message}</p>;
  }

  if (status === "needs_input") {
    return (
      <p>Cần bổ sung thông tin: {(result.missing_fields || []).join(", ")}</p>
    );
  }

  if (status === "invalid_input") {
    return <p>Dữ liệu không hợp lệ: {error?.message}</p>;
  }

  return (
    <p className="error">Đã xảy ra lỗi: {error?.message || "không xác định"}</p>
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
