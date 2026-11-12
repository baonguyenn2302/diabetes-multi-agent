"""Kiểm thử tự động giao diện người dùng (Streamlit AppTest).

Đảm bảo tất cả các trang UI:
- ui/streamlit_app.py (Trang chủ)
- ui/pages/diabetes_risk_assessment.py (Trang Đánh giá nguy cơ)
- ui/pages/diabetes_chatbot.py (Trang Chatbot Messenger)
được biên dịch, nạp và render thành công mà không phát sinh bất kỳ ngoại lệ (exception) hay lỗi cú pháp nào.
"""
import pytest
from pathlib import Path

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_home_page_renders_without_exceptions():
    at = AppTest.from_file(str(ROOT_DIR / "ui/streamlit_app.py"))
    at.run()
    assert not at.exception, f"Lỗi giao diện tại Trang chủ: {at.exception}"


def test_assessment_page_renders_without_exceptions():
    at = AppTest.from_file(str(ROOT_DIR / "ui/pages/diabetes_risk_assessment.py"))
    at.run()
    assert not at.exception, f"Lỗi giao diện tại Trang Đánh giá nguy cơ: {at.exception}"


def test_chatbot_page_renders_without_exceptions():
    at = AppTest.from_file(str(ROOT_DIR / "ui/pages/diabetes_chatbot.py"))
    at.run()
    assert not at.exception, f"Lỗi giao diện tại Trang Chatbot: {at.exception}"

