export async function sendChat({ sessionId, message, healthData = null }) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      health_data: healthData,
    }),
  });
  // Backend trả JSON có status cả khi lỗi, nên luôn đọc body
  const data = await res.json().catch(() => null);
  if (!data) {
    throw new Error(`Backend trả về HTTP ${res.status} không có JSON`);
  }
  return data;
}