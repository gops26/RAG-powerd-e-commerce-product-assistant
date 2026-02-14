function ChatMessage({ role, content }) {
  return (
    <div className={`chat-message chat-message--${role}`}>
      <div className="chat-message-label">
        {role === "user" ? "👤 You" : "🤖 Assistant"}
      </div>
      <div className="chat-message-content">{content}</div>
    </div>
  );
}

export default ChatMessage;
