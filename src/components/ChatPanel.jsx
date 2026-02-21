import { useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import LoadingIndicator from "./LoadingIndicator";

function ChatPanel({ messages, onSend, isLoading }) {
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  function handleSubmit(e) {
    e.preventDefault();
    const value = inputRef.current.value.trim();
    if (!value || isLoading) return;
    inputRef.current.value = "";
    onSend(value);
  }

  return (
    <section className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-placeholder">
            Ask a question about any product to get started.
          </p>
        )}
        {messages.map((msg, i) => (
          <ChatMessage key={i} role={msg.role} content={msg.content} />
        ))}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          type="text"
          placeholder="Ask anything about any product..."
          disabled={isLoading}
          className="chat-input"
        />
        <button type="submit" disabled={isLoading} className="chat-send-btn">
          Send
        </button>
      </form>
    </section>
  );
}

export default ChatPanel;
