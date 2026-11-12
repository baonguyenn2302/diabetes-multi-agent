"""Giao diện Streamlit: gửi thông tin bệnh nhân tới API và hiển thị báo cáo.

Chạy (API phải đang chạy ở cổng 8000):
    streamlit run ui/streamlit_app.py
Đổi địa chỉ API bằng biến môi trường API_URL nếu cần.
"""
import os
import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.features import ALLOWED_CATEGORIES, VALUE_RANGES  # noqa: E402

API_URL = os.getenv("API_URL", "http://localhost:8000")
LEVEL_ICON = {"high": "🔴", "medium": "🟠", "low": "🟡", "review": "⚠️"}

st.set_page_config(page_title="Hỗ trợ quyết định tiểu đường", layout="wide")
st.title("Hỗ trợ quyết định tiểu đường")
st.warning("Prototype học tập. Kết quả **không phải chẩn đoán xác định** và không thay thế bác sĩ.")


with st.form("patient"):
    c1, c2 = st.columns(2)
    with c1:
        gender = st.selectbox("Giới tính", ALLOWED_CATEGORIES["gender"])
        age = st.number_input("Tuổi", min_value=int(VALUE_RANGES["age"][0]),
                              max_value=int(VALUE_RANGES["age"][1]), value=45)
        bmi = st.number_input("BMI", float(VALUE_RANGES["bmi"][0]), float(VALUE_RANGES["bmi"][1]),
                              value=25.0, step=0.1)
        smoking = st.selectbox("Tiền sử hút thuốc", ALLOWED_CATEGORIES["smoking_history"])
    with c2:
        hba1c = st.number_input("HbA1c (%)", float(VALUE_RANGES["HbA1c_level"][0]),
                                float(VALUE_RANGES["HbA1c_level"][1]), value=5.5, step=0.1)
        glucose = st.number_input("Đường huyết (mg/dL)", float(VALUE_RANGES["blood_glucose_level"][0]),
                                  float(VALUE_RANGES["blood_glucose_level"][1]), value=100.0, step=1.0)
        ht = st.checkbox("Có tăng huyết áp")
        hd = st.checkbox("Có bệnh tim mạch")
    question = st.text_input("Câu hỏi thêm (tùy chọn)", placeholder="Ví dụ: triệu chứng tiểu đường là gì?")
    submitted = st.form_submit_button("Phân tích")


def show_result(body: dict):
    status = body.get("status")
    if status == "ok":
        st.success("Phân tích hoàn tất.")
    elif status == "partial":
        st.warning("Một số bước bị lỗi, kết quả chỉ là một phần. Xem mục Lỗi bên dưới.")

    if body.get("needs_human_review"):
        st.error("Có mâu thuẫn giữa mô hình và xét nghiệm: cần chuyên gia y tế xem xét trước khi dùng kết quả.")

    pred = body.get("prediction")
    m1, m2 = st.columns(2)
    m1.metric("Dự đoán của mô hình", pred["label"] if pred else "Không có")
    m2.metric("Xác suất", f"{pred['score']:.2f}" if pred else "–")

    if body.get("rules"):
        st.subheader("Cờ luật")
        for f in body["rules"]["flags"]:
            st.write(f"{LEVEL_ICON.get(f['level'], '•')} **[{f['id']}]** {f['text']}")

    if body.get("report"):
        st.subheader("Báo cáo")
        st.markdown(body["report"])

    with st.expander("Bằng chứng từ KG (có nguồn)"):
        for e in body.get("evidence", []):
            st.write(f"- {e.get('text')}  \n  _{e.get('source_title')}_ {e.get('source_url') or ''}")

    with st.expander("Trace các bước xử lý"):
        st.dataframe(body.get("trace", []))

    if body.get("errors"):
        with st.expander("Lỗi"):
            st.json(body["errors"])


if submitted:
    features = dict(gender=gender, age=float(age), hypertension=int(ht), heart_disease=int(hd),
                    smoking_history=smoking, bmi=float(bmi), HbA1c_level=float(hba1c),
                    blood_glucose_level=float(glucose))
    try:
        r = requests.post(f"{API_URL}/assess", json={"features": features, "question": question or None},
                          timeout=120)
    except requests.RequestException as e:
        st.error(f"Không kết nối được API tại {API_URL}. Kiểm tra đã chạy `uvicorn app.api:app` chưa. ({e})")
        st.stop()

    try:
        body = r.json()
    except ValueError:
        body = {}

    if r.status_code == 200:
        show_result(body)
    elif body.get("status") == "validation_error":
        st.error("Dữ liệu chưa hợp lệ:")
        for e in body.get("errors", []):
            st.write(f"- {e.get('error')}")
    elif isinstance(body.get("detail"), list):          # lỗi kiểu dữ liệu do FastAPI báo
        st.error("Dữ liệu gửi lên không đúng định dạng.")
        st.json(body["detail"])
    else:
        st.error(f"Lỗi API ({r.status_code}): {body.get('detail', r.text)}")

with st.sidebar:
    st.header("Vận hành")
    if st.button("Xem thống kê"):
        try:
            st.json(requests.get(f"{API_URL}/audit/summary", timeout=10).json())
        except requests.RequestException as e:
            st.error(f"Không lấy được thống kê: {e}")
