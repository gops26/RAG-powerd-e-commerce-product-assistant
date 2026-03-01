import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import ContextPanel from "./components/ContextPanel";
import { sendMessage } from "./api/chat";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [context, setContext] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSend(question) {
    const updatedMessages = [...messages, { role: "user", content: question }];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const data = await sendMessage(question, messages);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer },
      ]);
      setContext(data.context);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}. Please try again.` },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Product RAG Recommender</h1>
        <p>Ask me about any product</p>
      </header>
      <main className="app-main">
        <ChatPanel messages={messages} onSend={handleSend} isLoading={isLoading} />
        <ContextPanel context={context} />
      </main>
    </div>
  );
}

export default App;
