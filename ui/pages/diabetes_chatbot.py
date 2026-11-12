
"""
Trang Trợ lý vấn đáp y tế về bệnh tiểu đường (Messenger-style Chatbot).

Tên file: ui/pages/diabetes_chatbot.py
Bố cục:
  - Bot hiển thị ở BÊN TRÁI kèm icon ROBOT 🤖 (nền xám nhạt, bo góc tin nhắn đến).
  - Câu hỏi của người dùng hiển thị ở BÊN PHẢI kèm icon PERSON màu trắng ở lề ngoài cùng bên phải,
    bong bóng tin nhắn ôm sát chữ (không bị kéo giãn 100%).
  - Trình bày trực quan như một cửa sổ chat Messenger đích thực.
  - Không có các gợi ý chủ đề thừa thãi.
"""

import html
import os
import sys
import textwrap
from pathlib import Path

import requests
import streamlit as st


# Import module từ thư mục gốc của project
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

API_URL = os.getenv("API_URL", "http://localhost:8000")


st.set_page_config(
    page_title="Trợ lý vấn đáp tiểu đường | Diabetes MAS",
    layout="wide",
)


# Custom CSS phong cách Cửa sổ trò chuyện Messenger
st.markdown(
    textwrap.dedent("""
    <style>
        /* Nút back */
        .stButton > button {
            border-radius: 8px;
        }

        /* Khung chat message trợ lý */
        [data-testid="stChatMessage"] {
            border-radius: 14px;
            padding: 12px 16px;
            margin-bottom: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
        }
    </style>
    """),
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# NAVIGATION (NÚT BACK)
col_nav_left, _ = st.columns([1, 4])

with col_nav_left:
    if st.button(
        "← Quay về Trang chủ",
        key="btn_back_home",
        use_container_width=True,
    ):
        st.switch_page("streamlit_app.py")


# ------------------------------------------------------------
# HEADER BAR
col_title, col_status = st.columns([3, 1])

with col_title:
    st.subheader("Trợ lý Tri thức Y tế Tiểu đường")
    st.caption("Knowledge Graph RAG (ADA, WHO, Vinmec, Bộ Y tế)")

with col_status:
    st.markdown(
        '<div style="text-align: right; padding-top: 14px;">'
        '<span style="display:inline-block;width:10px;height:10px;'
        'background-color:#10b981;border-radius:50%;margin-right:6px;"></span>'
        '<span style="color:#10b981;font-weight:600;font-size:0.9rem;">'
        'Trực tuyến</span>'
        '</div>',
        unsafe_allow_html=True,
    )

st.divider()


# ------------------------------------------------------------
# QUẢN LÝ NGỮ CẢNH BỆNH NHÂN
patient_ctx = st.session_state.get("patient_context")

if patient_ctx:
    col_ctx_text, col_ctx_act = st.columns([4, 1])

    with col_ctx_text:
        st.success(
            f"**Đang liên kết hồ sơ từ Trang Đánh Giá:** "
            f"Tuổi: **{patient_ctx.get('age', '—')}** | "
            f"HbA1c: **{patient_ctx.get('HbA1c_level', '—')}%** | "
            f"Đường huyết: **{patient_ctx.get('blood_glucose_level', '—')} mg/dL** | "
            f"Đánh giá: **{patient_ctx.get('risk_label', 'Chưa rõ')}**"
        )

    with col_ctx_act:
        if st.button(
            "Ngắt liên kết hồ sơ",
            key="clear_ctx_btn",
            use_container_width=True,
        ):
            st.session_state["patient_context"] = None
            st.rerun()

else:
    st.info(
        "Chế độ: Hỏi đáp kiến thức y tế đại chúng — "
        "Bạn đang tra cứu kiến thức lý thuyết phổ quát. "
        "Hệ thống không lưu trữ hay áp đặt bất kỳ số liệu mặc định nào."
    )


# ------------------------------------------------------------
# KHỞI TẠO LỊCH SỬ CHAT
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": (
                "Xin chào, tôi là Trợ lý tri thức y tế về bệnh tiểu đường. "
                "Bạn có thể đặt câu hỏi về triệu chứng, ngưỡng xét nghiệm, "
                "chế độ dinh dưỡng, vận động hoặc các biến chứng liên quan."
            ),
            "evidence": [],
        }
    ]


def render_message(role: str, content: str, evidence: list = None):
    """
    Hiển thị tin nhắn chuẩn Messenger:
    - Bot ở BÊN TRÁI kèm icon Robot 🤖.
    - User ở BÊN PHẢI với bong bóng ôm sát chữ
      và icon Person màu trắng ở ngoài cùng bên phải.
    """

    if role == "user":
        # Người dùng: BÊN PHẢI, bong bóng ôm sát nội dung câu hỏi,
        # icon Person màu trắng ở lề ngoài cùng bên phải.

        safe_content = html.escape(content).replace("\n", "<br>")

        user_bubble_html = (
            '<div style="display: flex; justify-content: flex-end; '
            'align-items: flex-end; gap: 10px; margin: 14px 0; width: 100%;">'

            f'<div style="background-color: #0284c7; color: #ffffff; '
            f'padding: 10px 16px; border-radius: 18px 18px 4px 18px; '
            f'max-width: 72%; font-size: 0.95rem; line-height: 1.5; '
            f'word-wrap: break-word; '
            f'box-shadow: 0 1px 3px rgba(2,132,199,0.2);">'
            f'{safe_content}</div>'

            # User avatar - SVG Person màu trắng
            '<div style="width: 36px; height: 36px; min-width: 36px; '
            'border-radius: 50%; background-color: #0284c7; '
            'display: flex; align-items: center; justify-content: center; '
            'box-shadow: 0 1px 2px rgba(0,0,0,0.1); '
            'flex-shrink: 0;" title="Bạn (Người dùng)">'

            '<svg xmlns="http://www.w3.org/2000/svg" '
            'width="21" height="21" viewBox="0 0 24 24" '
            'fill="none" stroke="#ffffff" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'

            '<circle cx="12" cy="8" r="4"/>'
            '<path d="M5 21v-2a7 7 0 0 1 14 0v2"/>'

            '</svg>'
            '</div>'

            '</div>'
        )

        st.markdown(
            user_bubble_html,
            unsafe_allow_html=True,
        )

    else:
        # Trợ lý: BÊN TRÁI kèm icon Robot 🤖

        col_bot, _ = st.columns([5, 1])

        with col_bot:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(content)

                if evidence:
                    with st.expander("Nguồn trích dẫn từ Knowledge Graph"):
                        for ev in evidence:
                            title = ev.get("source_title", "Tài liệu y tế")
                            url = ev.get("source_url")

                            if url:
                                st.markdown(
                                    f"- {ev.get('text')} — [{title}]({url})"
                                )
                            else:
                                st.markdown(
                                    f"- {ev.get('text')} — *{title}*"
                                )


# ------------------------------------------------------------
# CỬA SỔ HIỂN THỊ TIN NHẮN
chat_container = st.container()

with chat_container:
    for msg in st.session_state["chat_messages"]:
        render_message(
            msg["role"],
            msg["content"],
            msg.get("evidence"),
        )


# ------------------------------------------------------------
# HỘP NHẬP TIN NHẮN
user_input = st.chat_input(
    "Nhập câu hỏi của bạn về bệnh tiểu đường..."
)

if user_input:

    # 1. Thêm tin nhắn của User vào lịch sử
    # và hiển thị BÊN PHẢI (icon Person màu trắng ở lề phải).

    st.session_state["chat_messages"].append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with chat_container:
        render_message("user", user_input)


    # 2. Gọi API /chat và hiển thị kết quả phản hồi của Bot
    # BÊN TRÁI (icon Robot 🤖).

    with chat_container:
        with st.spinner("Đang tra cứu tri thức y khoa..."):

            req_payload = {
                "question": user_input,
                "context": st.session_state.get("patient_context"),
            }

            try:
                resp = requests.post(
                    f"{API_URL}/chat",
                    json=req_payload,
                    timeout=60,
                )

                if resp.status_code == 200:
                    data = resp.json()

                    answer_text = data.get(
                        "answer",
                        "Không tìm thấy câu trả lời phù hợp.",
                    )

                    evidence_data = data.get("evidence", [])

                    render_message(
                        "assistant",
                        answer_text,
                        evidence_data,
                    )

                    st.session_state["chat_messages"].append(
                        {
                            "role": "assistant",
                            "content": answer_text,
                            "evidence": evidence_data,
                        }
                    )

                else:
                    err_msg = (
                        f"Lỗi từ hệ thống ({resp.status_code}): "
                        f"{resp.text}"
                    )

                    st.error(err_msg)
                    render_message("assistant", err_msg)

                    st.session_state["chat_messages"].append(
                        {
                            "role": "assistant",
                            "content": err_msg,
                        }
                    )

            except requests.RequestException as e:
                net_err = (
                    f"Không thể kết nối đến backend API "
                    f"tại {API_URL}: {e}"
                )

                st.error(net_err)
                render_message("assistant", net_err)

                st.session_state["chat_messages"].append(
                    {
                        "role": "assistant",
                        "content": net_err,
                    }
                )


# ------------------------------------------------------------
# SIDEBAR
with st.sidebar:

    st.header("Tùy chọn hội thoại")

    if st.button(
        "Xóa lịch sử trò chuyện",
        use_container_width=True,
    ):
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Lịch sử cuộc trò chuyện đã được làm mới. "
                    "Mời bạn đặt câu hỏi tiếp theo."
                ),
                "evidence": [],
            }
        ]

        st.rerun()

    st.divider()

    st.markdown("**Cơ sở tri thức tích hợp:**")

    st.markdown("- 52 thực thể y khoa chuyên sâu")
    st.markdown("- 67 quan hệ đồ thị Neo4j")
    st.markdown("- Trích dẫn từ ADA (2021-2026), WHO, Vinmec, Bộ Y tế")
