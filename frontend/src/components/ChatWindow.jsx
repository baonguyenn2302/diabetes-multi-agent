import SourceList from './SourceList';
import AgentActivity from './AgentActivity';

function AssistantBody({ response }) {
  const status = response?.status || 'error';
  const errorMessage = typeof response?.error === 'string'
    ? response.error : response?.error?.message;
  const answer = response?.answer || (status === 'error' ? errorMessage : '') || 'Chưa có nội dung phản hồi.';
  const sources = Array.isArray(response?.sources) ? response.sources : [];
  const warnings = Array.isArray(response?.warnings) ? response.warnings : [];
  const missingFields = Array.isArray(response?.missing_fields) ? response.missing_fields : [];
  const trace = Array.isArray(response?.agent_trace) ? response.agent_trace : [];
  return (
    <div className="assistant-content">
      <span className={`status-tag status-${status}`}>{status}</span>
      <p className="answer-text">{answer}</p>
      {missingFields.length > 0 && <p className="help-text">Trường cần bổ sung: {missingFields.join(', ')}</p>}
      {warnings.length > 0 && (
        <div className="warnings" role="note">
          {warnings.map((w, i) => <p key={i}>{w}</p>)}
        </div>
      )}
      <SourceList sources={sources} />
      <AgentActivity events={trace} />
    </div>
  );
}

export default function ChatWindow({ messages, loading }) {
  return (
    <div className="chat-window" aria-live="polite">
      {messages.length === 0 && <p className="empty-chat">Chọn chế độ và đặt câu hỏi để bắt đầu demo.</p>}
      {messages.map((m, i) => (
        <div key={m.id || i} className={`message ${m.role}`}>
          {m.role === 'user' ? <p>{m.text}</p> : <AssistantBody response={m.response} />}
        </div>
      ))}
      {loading && <p className="loading">Đang xử lý qua hệ thống Agent...</p>}
    </div>
  );
}
