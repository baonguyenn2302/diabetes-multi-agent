import { useState } from "react";
import { sendChat } from "./api/chatApi";
import ChatWindow from "./components/ChatWindow";
import HealthDataForm from "./components/HealthDataForm";
import MessageInput from "./components/MessageInput";
import SafetyBanner from "./components/SafetyBanner";

const RISK_MESSAGE = "Tôi muốn đánh giá nguy cơ tiểu đường";

export default function App() {
  const [mode, setMode] = useState("knowledge");
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function send({ message, healthData, label }) {
    setMessages((prev) => [...prev, { role: "user", text: label }]);
    setLoading(true);
    try {
      const response = await sendChat({ sessionId, message, healthData });
      setMessages((prev) => [...prev, { role: "assistant", response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", response: { error: { message: err.message } } },
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
          disabled={loading}
          onSend={(text) =>
            send({ message: text, healthData: null, label: text })
          }
        />
      ) : (
        <HealthDataForm
          disabled={loading}
          onSubmit={(features) =>
            send({
              message: RISK_MESSAGE,
              healthData: features,
              label: "Đánh giá nguy cơ với dữ liệu đã nhập",
            })
          }
        />
      )}
    </div>
  );
}
