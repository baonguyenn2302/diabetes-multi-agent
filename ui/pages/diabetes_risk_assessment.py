"""Trang Đánh giá nguy cơ bệnh tiểu đường dựa trên 8 chỉ số sức khỏe định lượng.

Tên file: ui/pages/diabetes_risk_assessment.py
Chức năng: Sàng lọc nguy cơ, không chứa ô nhập câu hỏi tự do hay hội thoại.
"""
import os
import sys
from pathlib import Path
import requests
import streamlit as st

# Import module từ thư mục gốc của project
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.features import ALLOWED_CATEGORIES, VALUE_RANGES

API_URL = os.getenv("API_URL", "http://localhost:8000")
LEVEL_LABELS = {
    "high": "Mức cao",
    "medium": "Mức trung bình",
    "low": "Mức thấp",
    "review": "Cần xem xét"
}

st.set_page_config(
    page_title="Đánh giá nguy cơ tiểu đường | Diabetes MAS",
    layout="wide",
)

# Custom Light Theme CSS (Hạn chế tối đa icon, phong cách tối giản chuẩn y tế)
st.markdown("""
<style>
    .nav-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 16px;
        margin-bottom: 20px;
        border-bottom: 1px solid #e2e8f0;
    }
    .metric-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .tag-high { background-color: #fee2e2; color: #991b1b; }
    .tag-medium { background-color: #ffedd5; color: #9a3412; }
    .tag-low { background-color: #fef9c3; color: #854d0e; }
    .tag-review { background-color: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------ NAVIGATION BAR (NÚT BACK)
col_nav_left, col_nav_right = st.columns([1, 4])
with col_nav_left:
    if st.button("← Quay về Trang chủ", key="btn_back_home", use_container_width=True):
        st.switch_page("streamlit_app.py")

st.title("Đánh giá Nguy cơ Bệnh Tiểu đường")
st.caption("Chức năng: Sàng lọc định lượng dựa trên mô hình Deep Learning và Hệ luật lâm sàng ADA/WHO")
st.warning("Lưu ý y tế: Kết quả mang tính chất sàng lọc và hỗ trợ quyết định học tập, không thay thế chẩn đoán của bác sĩ.")

# ------------------------------------------------------------ FORM NHẬP SỐ LIỆU
with st.form("patient_assessment_form"):
    st.subheader("Nhập thông tin và chỉ số xét nghiệm")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Thông tin thể trạng và nhân khẩu**")
        gender = st.selectbox("Giới tính", ALLOWED_CATEGORIES["gender"])
        age = st.number_input("Tuổi", min_value=int(VALUE_RANGES["age"][0]),
                              max_value=int(VALUE_RANGES["age"][1]), value=45)
        bmi = st.number_input("Chỉ số BMI", float(VALUE_RANGES["bmi"][0]), float(VALUE_RANGES["bmi"][1]),
                              value=25.0, step=0.1, help="BMI = Cân nặng (kg) / [Chiều cao (m)]^2")
        smoking = st.selectbox("Tiền sử hút thuốc lá", ALLOWED_CATEGORIES["smoking_history"])

    with c2:
        st.markdown("**2. Chỉ số xét nghiệm và bệnh lý kèm theo**")
        hba1c = st.number_input("Chỉ số HbA1c (%)", float(VALUE_RANGES["HbA1c_level"][0]),
                                float(VALUE_RANGES["HbA1c_level"][1]), value=5.5, step=0.1,
                                help="Ngưỡng bình thường < 5.7%, tiền tiểu đường: 5.7 - 6.4%, tiểu đường >= 6.5%")
        glucose = st.number_input("Đường huyết lúc đói (mg/dL)", float(VALUE_RANGES["blood_glucose_level"][0]),
                                  float(VALUE_RANGES["blood_glucose_level"][1]), value=100.0, step=1.0,
                                  help="Ngưỡng bình thường < 100 mg/dL, tiền tiểu đường: 100 - 125 mg/dL, >= 126 mg/dL là ngưỡng chẩn đoán")
        ht = st.checkbox("Có tiền sử hoặc đang điều trị tăng huyết áp")
        hd = st.checkbox("Có tiền sử bệnh tim mạch (bạch vành, suy tim, nhồi máu cơ tim...)")

    submitted = st.form_submit_button("Phân tích nguy cơ", use_container_width=True)


def show_assessment_result(body: dict, current_features: dict):
    st.divider()
    status = body.get("status")
    if status == "ok":
        st.success("Phân tích hoàn tất thành công.")
    elif status == "partial":
        st.warning("Một số bước phân tích bị gián đoạn, kết quả là một phần đáng tin.")

    if body.get("needs_human_review"):
        st.error("Cảnh báo mâu thuẫn lâm sàng: Có sự không thống nhất giữa dự đoán mô hình và chỉ số xét nghiệm thực tế. Cần bác sĩ chuyên khoa xem xét trực tiếp.")

    pred = body.get("prediction")
    pred_label = pred["label"] if pred else "Chưa xác định"
    pred_score = pred["score"] if pred else 0.0

    # Metric tổng quan
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Dự đoán mô hình Deep Learning", pred_label)
    with m2:
        st.metric("Xác suất nguy cơ", f"{pred_score * 100:.1f}%")
    with m3:
        n_flags = len(body.get("rules", {}).get("flags", []))
        st.metric("Số cờ luật cảnh báo", f"{n_flags} cờ")

    # Nút chuyển ngữ cảnh sang trang Hỏi đáp y tế
    st.info("Gợi ý: Bạn có thắc mắc về kết quả xét nghiệm hoặc muốn tìm hiểu sâu hơn?")
    col_btn, _ = st.columns([1, 1])
    with col_btn:
        if st.button("Lưu kết quả và Chuyển sang Hỏi đáp y tế", key="link_to_chat", use_container_width=True):
            # Lưu ngữ cảnh đánh giá vào session_state
            st.session_state["patient_context"] = {
                "gender": current_features["gender"],
                "age": current_features["age"],
                "bmi": current_features["bmi"],
                "HbA1c_level": current_features["HbA1c_level"],
                "blood_glucose_level": current_features["blood_glucose_level"],
                "hypertension": current_features["hypertension"],
                "heart_disease": current_features["heart_disease"],
                "risk_label": pred_label,
                "score": pred_score,
                "needs_human_review": body.get("needs_human_review", False),
            }
            try:
                st.switch_page("pages/diabetes_chatbot.py")
            except Exception:
                st.success("Đã lưu hồ sơ chỉ số. Mời bạn chọn trang 'diabetes chatbot' trên menu điều hướng.")

    # Cờ luật
    if body.get("rules") and body["rules"].get("flags"):
        st.subheader("Cờ cảnh báo từ Hệ luật lâm sàng (Rule-based)")
        for f in body["rules"]["flags"]:
            lvl = f.get("level", "low")
            tag_class = f"tag-{lvl}" if lvl in ("high", "medium", "low", "review") else "tag-low"
            lvl_text = LEVEL_LABELS.get(lvl, lvl)
            st.markdown(
                f'<span class="badge-tag {tag_class}">[{f["id"]}] {lvl_text}</span> {f["text"]}',
                unsafe_allow_html=True
            )

    # Báo cáo chi tiết
    if body.get("report"):
        st.subheader("Báo cáo hỗ trợ quyết định chi tiết")
        st.markdown(body["report"])

    # Bằng chứng từ Knowledge Graph
    if body.get("evidence"):
        with st.expander("Bằng chứng y khoa từ Knowledge Graph (kèm nguồn)"):
            for e in body.get("evidence", []):
                title = e.get("source_title", "Tài liệu y tế")
                url = e.get("source_url")
                if url:
                    st.write(f"- {e.get('text')} — [{title}]({url})")
                else:
                    st.write(f"- {e.get('text')} — *{title}*")

    # Trace
    with st.expander("Nhật ký thực thi các bước (Trace)"):
        st.dataframe(body.get("trace", []))

    if body.get("errors"):
        with st.expander("Chi tiết lỗi phát sinh"):
            st.json(body["errors"])


if submitted:
    features = dict(
        gender=gender, age=float(age), hypertension=int(ht), heart_disease=int(hd),
        smoking_history=smoking, bmi=float(bmi), HbA1c_level=float(hba1c),
        blood_glucose_level=float(glucose)
    )
    with st.spinner("Đang điều phối các Agent phân tích dữ liệu..."):
        try:
            r = requests.post(f"{API_URL}/assess", json={"features": features}, timeout=120)
        except requests.RequestException as e:
            st.error(f"Không thể kết nối tới backend API tại {API_URL}. Vui lòng kiểm tra lệnh `uvicorn app.api:app`. ({e})")
            st.stop()

    try:
        body = r.json()
    except ValueError:
        body = {}

    if r.status_code == 200:
        show_assessment_result(body, features)
    elif body.get("status") == "validation_error":
        st.error("Dữ liệu đầu vào chưa hợp lệ:")
        for err in body.get("errors", []):
            st.write(f"- {err.get('error')}")
    else:
        st.error(f"Lỗi API ({r.status_code}): {body.get('detail', r.text)}")

with st.sidebar:
    st.header("Trạng thái hệ thống")
    if st.button("Kiểm tra Audit Log"):
        try:
            st.json(requests.get(f"{API_URL}/audit/summary", timeout=10).json())
        except Exception as e:
            st.error(f"Không thể lấy thống kê: {e}")
