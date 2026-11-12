"""Trang chủ / Cổng điều hướng: Hệ đa agent hỗ trợ quyết định & vấn đáp bệnh tiểu đường.

Chạy:
    streamlit run ui/streamlit_app.py
"""
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Diabetes MAS | Hệ Đa Agent Tiểu Đường",
    layout="wide",
)

# Custom Light Theme CSS (Hạn chế tối đa icon, phong cách tối giản)
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 24px 0 16px 0;
    }
    .portal-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1 style="color: #0f172a; margin-bottom: 8px;">Hệ Đa Agent Hỗ Trợ Quyết Định & Vấn Đáp Tiểu Đường</h1>
    <p style="color: #64748b; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
        Giải pháp tích hợp Học sâu (Deep Learning), Cơ sở tri thức đồ thị (Neo4j Knowledge Graph) 
        và Hệ luật lâm sàng (Rule-based) theo khuyến cáo ADA/WHO.
    </p>
</div>
""", unsafe_allow_html=True)

st.warning("Tuyên bố trách nhiệm: Đây là hệ thống hỗ trợ học tập và nghiên cứu (ISD - PTIT). "
           "Mọi kết quả và khuyến nghị không thay thế chẩn đoán hoặc chỉ định điều trị của bác sĩ.")

st.write("")

# ------------------------------------------------------------ 2 LỰA CHỌN PHÂN NÁNH CHÍNH
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="portal-card">
        <div>
            <h2 style="color: #0284c7; margin-top: 0;">1. Đánh giá Nguy cơ Cá nhân</h2>
            <p style="color: #334155; line-height: 1.6;">
                Dành cho người muốn sàng lọc nguy cơ mắc bệnh tiểu đường dựa trên <b>8 chỉ số sức khỏe định lượng</b>:
                Tuổi, BMI, HbA1c, Đường huyết, Tăng huyết áp, Tiền sử tim mạch, Hút thuốc.
            </p>
            <ul style="color: #475569; line-height: 1.6;">
                <li>Dự đoán xác suất từ mạng nơ-ron Deep Learning (Keras).</li>
                <li>Rà soát cờ cảnh báo theo tiêu chuẩn lâm sàng (ADA/WHO).</li>
                <li>Phát hiện mâu thuẫn cần chuyên gia y tế thẩm định.</li>
                <li>Giao diện thuần số liệu, không chứa ô nhập câu hỏi thừa.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Đi đến Trang Đánh giá nguy cơ", key="btn_to_assess", use_container_width=True):
        try:
            st.switch_page("pages/diabetes_risk_assessment.py")
        except Exception:
            st.info("Hãy chọn trang 'diabetes risk assessment' trên menu điều hướng bên trái.")

with col2:
    st.markdown("""
    <div class="portal-card">
        <div>
            <h2 style="color: #0d9488; margin-top: 0;">2. Trợ lý Vấn đáp Y tế (Chatbot)</h2>
            <p style="color: #334155; line-height: 1.6;">
                Cửa sổ hội thoại tương tác chuyên sâu dạng Messenger, phục vụ tra cứu mọi thắc mắc về bệnh đái tháo đường:
                triệu chứng, chẩn đoán, chế độ dinh dưỡng, vận động và phòng ngừa biến chứng.
            </p>
            <ul style="color: #475569; line-height: 1.6;">
                <li>Tra cứu Knowledge Graph Neo4j (52 thực thể, 67 quan hệ).</li>
                <li>Mọi câu trả lời đều có trích dẫn nguồn y khoa uy tín.</li>
                <li>Độc lập hoàn toàn, không bị gán ép số liệu mặc định.</li>
                <li>Hỗ trợ liên kết hồ sơ chỉ khi người dùng chủ động yêu cầu.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Đi đến Trang Hỏi đáp y tế", key="btn_to_chat", use_container_width=True):
        try:
            st.switch_page("pages/diabetes_chatbot.py")
        except Exception:
            st.info("Hãy chọn trang 'diabetes chatbot' trên menu điều hướng bên trái.")

st.divider()

# ------------------------------------------------------------ TỔNG QUAN KIẾN TRÚC ĐA AGENT
st.subheader("Kiến trúc Hệ Đa Agent (Multi-Agent System)")

a1, a2, a3, a4, a5 = st.columns(5)
with a1:
    st.markdown("**1. Data Agent**")
    st.caption("Kiểm định & chuẩn hóa 8 trường dữ liệu bệnh nhân")
with a2:
    st.markdown("**2. DL Agent**")
    st.caption("Dự đoán xác suất nguy cơ (MLP Keras, AUC 0.975)")
with a3:
    st.markdown("**3. Rule Agent**")
    st.caption("Áp dụng ngưỡng ADA/WHO & kiểm tra mâu thuẫn")
with a4:
    st.markdown("**4. KG/RAG Agent**")
    st.caption("Truy vấn tri thức & bằng chứng có nguồn (Neo4j)")
with a5:
    st.markdown("**5. Coordinator**")
    st.caption("Điều phối linh hoạt theo luồng Đánh giá hoặc Chat")

# ------------------------------------------------------------ SIDEBAR
with st.sidebar:
    st.header("Vận hành hệ thống")
    try:
        health_res = requests.get(f"{API_URL}/health", timeout=5).json()
        if health_res.get("status") == "ok":
            st.success("API Service: Hoạt động bình thường")
        else:
            st.warning("API Service: Phản hồi bất thường")
    except Exception:
        st.error("API Service: Chưa khởi động (cần chạy `uvicorn app.api:app`)")

    if st.button("Xem thống kê Audit log"):
        try:
            st.json(requests.get(f"{API_URL}/audit/summary", timeout=5).json())
        except Exception as e:
            st.error(f"Lỗi: {e}")
