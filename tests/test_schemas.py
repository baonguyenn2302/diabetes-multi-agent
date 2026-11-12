from app.schemas import AgentMessage, PatientRequest, ChatRequest, ChatResponse


def test_ok_message():
    m = AgentMessage.ok("req_1", "TestAgent", {"a": 1}, version="v1")
    assert m.status == "ok" and m.payload == {"a": 1} and m.error is None


def test_fail_message():
    m = AgentMessage.fail("req_1", "TestAgent", "boom")
    assert m.status == "error" and m.error == "boom" and m.payload == {}


def test_patient_request():
    r = PatientRequest(features={"Glucose": 120.0}, question="hi")
    assert r.features["Glucose"] == 120.0


def test_patient_request_accepts_text_categories():
    r = PatientRequest(features={"gender": "Female", "age": 40})
    assert r.features["gender"] == "Female" and r.features["age"] == 40


def test_chat_request_and_response():
    req = ChatRequest(question="tiểu đường là gì")
    assert req.question == "tiểu đường là gì"
    assert req.context is None

    res = ChatResponse(request_id="chat_123", answer="câu trả lời", has_patient_context=False)
    assert res.status == "ok"
    assert res.answer == "câu trả lời"

