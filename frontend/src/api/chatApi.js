const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000').replace(/\/$/, '');

async function apiRequest(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000);
  try {
    const response = await fetch(`${BASE_URL}${path}`, { ...options, signal: controller.signal });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = typeof data?.error === 'string' ? data.error : data?.error?.message;
      throw new Error(detail || data?.answer || `Backend trả về HTTP ${response.status}`);
    }
    if (!data || typeof data !== 'object') throw new Error('Backend trả phản hồi JSON không hợp lệ');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Yêu cầu quá thời gian chờ (120 giây). Kiểm tra Ollama và Flask.', {
        cause: error,
      });
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export function sendChat({ session_id, message, health_data = null }) {
  return apiRequest('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ session_id, message, health_data }),
  });
}

export function fetchHistory(sessionId, limit = 20) {
  return apiRequest(`/api/history?session_id=${encodeURIComponent(sessionId)}&limit=${limit}`);
}

export function fetchHealth() {
  return apiRequest('/api/health');
}
