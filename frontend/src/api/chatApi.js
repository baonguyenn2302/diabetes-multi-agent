import {
  riskSuccess,
  riskNeedsInput,
  knowledgeSuccess,
  knowledgeInsufficient,
  serviceError,
} from "../mocks/sampleResponses";

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

// Hình dạng payload này là tạm thời, sẽ chỉnh theo docs/agent_contracts.md.
// payload = { message: "câu hỏi" }            -> hỏi kiến thức
// payload = { features: { ...8 trường... } }  -> đánh giá nguy cơ
export async function sendChat(payload) {
  if (USE_MOCK) {
    return mockChat(payload);
  }
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Backend trả về HTTP ${res.status}`);
  }
  return res.json();
}

async function mockChat(payload) {
  // Giả lập độ trễ mạng để kiểm tra trạng thái loading
  await new Promise((resolve) => setTimeout(resolve, 400));

  if (payload.features) {
    const missing = Object.entries(payload.features)
      .filter(([, v]) => v === "" || v === null || v === undefined)
      .map(([k]) => k);
    if (missing.length > 0) {
      return { ...riskNeedsInput, result: { missing_fields: missing, errors: {} } };
    }
    return riskSuccess;
  }

  const text = (payload.message || "").toLowerCase();
  if (text.includes("lỗi")) {
    return serviceError;
  }
  const outOfScope = ["phở", "thời tiết", "bánh mì", "bake", "giá vàng"];
  if (outOfScope.some((kw) => text.includes(kw))) {
    return knowledgeInsufficient;
  }
  return knowledgeSuccess;
}