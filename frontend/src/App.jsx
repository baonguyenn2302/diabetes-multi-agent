import { useState } from "react";
import { sendChat } from "./api/chatApi";
import ChatWindow from "./components/ChatWindow";
import HealthDataForm from "./components/HealthDataForm";
import MessageInput from "./components/MessageInput";
import SafetyBanner from "./components/SafetyBanner";

export default function App() {
  const [mode, setMode] = useState("knowledge");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function send(payload, userLabel) {
    setMessages((prev) => [...prev, { role: "user", text: userLabel }]);
    setLoading(true);
    try {
      const response = await sendChat(payload);
      setMessages((prev) => [...prev, { role: "assistant", response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          response: { status: "error", error: { message: err.message } },
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>Trợ lý Đái tháo đường (demo)</h1>
      <SafetyBanner />

      <nav>
        <button
          onClick={() => setMode("knowledge")}
          disabled={mode === "knowledge"}
        >
          Hỏi kiến thức
        </button>
        <button onClick={() => setMode("risk")} disabled={mode === "risk"}>
          Đánh giá nguy cơ
        </button>
      </nav>

      <ChatWindow messages={messages} loading={loading} />

      {mode === "knowledge" ? (
        <MessageInput
          onSend={(text) => send({ message: text }, text)}
          disabled={loading}
        />
      ) : (
        <HealthDataForm
          disabled={loading}
          onSubmit={(features) =>
            send({ features }, "Đánh giá nguy cơ với dữ liệu đã nhập")
          }
        />
      )}
    </div>
  );
}
