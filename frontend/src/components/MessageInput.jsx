import { useState } from "react";

export default function MessageInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const value = text.trim();
    if (!value || disabled) return;
    onSend(value);
    setText("");
  }

  return (
    <form onSubmit={handleSubmit} className="message-input">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Nhập câu hỏi về đái tháo đường..."
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !text.trim()}>
        Gửi
      </button>
    </form>
  );
}
