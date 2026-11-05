// Dữ liệu mẫu theo format của Risk Assessment Agent và Medical Knowledge Agent.
// Cập nhật khi docs/agent_contracts.md của Người A được chốt.

export const riskSuccess = {
  session_id: "demo-1",
  task_id: "task-risk-1",
  agent: "risk_assessment_agent",
  status: "success",
  result: {
    prediction: 0,
    probability: 0.2134,
    threshold: 0.5,
    model_metrics: {
      test_roc_auc: 0.971,
      test_precision: 0.507,
      test_recall: 0.888,
      test_f1: 0.646,
    },
    trained_on: "2026-11-03",
    limitations: [
      "Dữ liệu huấn luyện không đại diện cho mọi nhóm dân cư, bao gồm người Việt Nam.",
      "Kết quả chỉ là ước tính tham khảo, không phải chẩn đoán y khoa.",
    ],
  },
  error: null,
};

export const riskNeedsInput = {
  session_id: "demo-2",
  task_id: "task-risk-2",
  agent: "risk_assessment_agent",
  status: "needs_input",
  result: {
    missing_fields: ["bmi", "HbA1c_level"],
    errors: {},
  },
  error: null,
};

export const riskInvalidInput = {
  session_id: "demo-3",
  task_id: "task-risk-3",
  agent: "risk_assessment_agent",
  status: "invalid_input",
  result: {},
  error: {
    code: "invalid_input",
    message: "Dữ liệu đầu vào không hợp lệ",
    fields: { age: "Hệ thống chỉ hỗ trợ người từ 18 tuổi trở lên" },
  },
};

export const knowledgeSuccess = {
  session_id: "demo-4",
  task_id: "task-kb-1",
  agent: "medical_knowledge_agent",
  status: "success",
  result: {
    sources: [
      {
        source_id: "who_diabetes_fact_sheet_2024-11-14",
        source_title: "Diabetes – Fact sheet (WHO)",
        publisher: "World Health Organization",
        date: "2024-11-14",
        url: "https://www.who.int/news-room/fact-sheets/detail/diabetes",
        section: "Symptoms",
        subsection: "",
        distance: 0.142,
        excerpt: "Symptoms of diabetes may occur suddenly...",
      },
    ],
    max_distance: 0.5,
    disclaimer:
      "Thông tin tham khảo từ tài liệu y khoa đã được nạp, không thay thế chẩn đoán hoặc tư vấn của bác sĩ.",
  },
  error: null,
};

export const knowledgeInsufficient = {
  session_id: "demo-5",
  task_id: "task-kb-2",
  agent: "medical_knowledge_agent",
  status: "insufficient_evidence",
  result: {
    message: "Không tìm thấy tài liệu đủ liên quan đến câu hỏi trong kho tri thức.",
    best_distance: 0.734,
    max_distance: 0.5,
    sources: [],
    disclaimer:
      "Thông tin tham khảo từ tài liệu y khoa đã được nạp, không thay thế chẩn đoán hoặc tư vấn của bác sĩ.",
  },
  error: null,
};

export const serviceError = {
  session_id: "demo-6",
  task_id: "task-err-1",
  agent: "medical_knowledge_agent",
  status: "error",
  result: {},
  error: {
    code: "knowledge_unavailable",
    message: "Kho tri thức rỗng",
  },
};