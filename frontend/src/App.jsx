import { useEffect, useState } from 'react';
import { fetchHealth, fetchHistory, sendChat } from './api/chatApi';
import ChatWindow from './components/ChatWindow';
import HealthDataForm from './components/HealthDataForm';
import MessageInput from './components/MessageInput';
import SafetyBanner from './components/SafetyBanner';
import './App.css';

function createSessionId() {
  const stored = sessionStorage.getItem('diabetes_demo_session');
  if (stored && /^web-[a-f0-9-]{36}$/.test(stored)) return stored;
  const next = `web-${crypto.randomUUID()}`;
  sessionStorage.setItem('diabetes_demo_session', next);
  return next;
}

export default function App() {
  const [mode, setMode] = useState('knowledge');
  const [sessionId, setSessionId] = useState(createSessionId);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [health, setHealth] = useState('checking');

  useEffect(() => {
    let active = true;
    fetchHealth().then(data => { if (active) setHealth(data.status || 'unknown'); })
      .catch(() => { if (active) setHealth('offline'); });
    return () => { active = false; };
  }, []);

  async function send(message, healthData = null, userLabel = message) {
    if (loading) return;
    setMessages(prev => [...prev, { role: 'user', text: userLabel }]);
    setLoading(true);
    try {
      const response = await sendChat({ session_id: sessionId, message, health_data: healthData });
      setMessages(prev => [...prev, { role: 'assistant', response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', response: {
        status: 'error', answer: `Không thể liên hệ backend: ${error.message}`,
        warnings: ['Kiểm tra Flask tại cổng 5000 và trạng thái Ollama.'],
      } }]);
    } finally {
      setLoading(false);
    }
  }

  async function restoreHistory() {
    if (loading || historyLoading) return;
    setHistoryLoading(true);
    try {
      const data = await fetchHistory(sessionId, 50);
      const chronologic = [...(data.history || [])].reverse();
      setMessages(chronologic.flatMap((item) => [
        { id: `u-${item.execution_id}`, role: 'user', text: item.message },
        { id: `a-${item.execution_id}`, role: 'assistant', response: item },
      ]));
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', response: {
        status: 'error', answer: `Không thể tải lịch sử: ${error.message}`,
      } }]);
    } finally {
      setHistoryLoading(false);
    }
  }

  function newSession() {
    if (loading) return;
    const next = `web-${crypto.randomUUID()}`;
    sessionStorage.setItem('diabetes_demo_session', next);
    setSessionId(next);
    setMessages([]);
  }

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <p className="eyebrow">DIABETES AI · MULTI-AGENT DEMO</p>
          <h1>Trợ lý kiến thức đái tháo đường</h1>
          <p className="subtitle">Coordinator · Risk Assessment · Medical Knowledge · Medical Advisor</p>
        </div>
        <span className={`backend-status status-${health}`}>Backend: {health}</span>
      </header>
      <SafetyBanner />
      <section className="toolbar" aria-label="Chọn chế độ">
        <div className="mode-switch">
          <button className={mode === 'knowledge' ? 'active' : ''} onClick={() => setMode('knowledge')} disabled={loading}>Hỏi kiến thức</button>
          <button className={mode === 'risk' ? 'active' : ''} onClick={() => setMode('risk')} disabled={loading}>Đánh giá nguy cơ</button>
        </div>
        <div className="secondary-actions">
          <button onClick={restoreHistory} disabled={loading || historyLoading}>{historyLoading ? 'Đang tải...' : 'Tải lịch sử'}</button>
          <button onClick={newSession} disabled={loading}>Phiên mới</button>
        </div>
      </section>
      <p className="session-label">Session: <code>{sessionId}</code></p>
      <ChatWindow messages={messages} loading={loading} />
      <section className="input-panel">
        {mode === 'knowledge' ? (
          <MessageInput onSend={(text) => send(text)} disabled={loading} />
        ) : (
          <HealthDataForm disabled={loading} onSubmit={(features) =>
            send('Tôi muốn đánh giá nguy cơ tiểu đường', features, 'Đánh giá nguy cơ với bộ dữ liệu demo đã nhập')
          } />
        )}
      </section>
      <footer>Demo học thuật · Không dùng để chẩn đoán hoặc điều trị · Chỉ nhập dữ liệu giả lập</footer>
    </main>
  );
}
