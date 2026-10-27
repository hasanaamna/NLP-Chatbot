
import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  Bot, Send, Trash2, UserRound, Sparkles, Wifi, WifiOff,
} from "lucide-react";
import "./App.css";

type Message = {
  id: number;
  role: "bot" | "user";
  text: string;
};

const API_URL = "http://127.0.0.1:8000";

const suggestions = [
  "Hello!",
  "What can you do?",
  "Who are you?",
  "Thank you",
];

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "bot",
      text: "Hi! I'm your NLP Chatbot. Ask me something, and I'll do my best to help.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await fetch(`${API_URL}/health`);
        setConnected(response.ok);
      } catch {
        setConnected(false);
      }
    }

    void checkHealth();
    const interval = window.setInterval(() => void checkHealth(), 10000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(event?: FormEvent, suggestedText?: string) {
    event?.preventDefault();
    const text = (suggestedText ?? input).trim();

    if (!text || loading) return;

    setMessages((current) => [
      ...current,
      { id: Date.now(), role: "user", text },
    ]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data: { response: string; intent?: string } =
        await response.json();

      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "bot",
          text: data.response,
        },
      ]);
      setConnected(true);
    } catch {
      setConnected(false);
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "bot",
          text: "I couldn't reach the chatbot server. Please start the FastAPI backend at http://127.0.0.1:8000 and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function clearChat() {
    setMessages([
      {
        id: Date.now(),
        role: "bot",
        text: "Chat cleared! What would you like to talk about?",
      },
    ]);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Bot size={25} /></div>
          <div>
            <h1>NLP Chatbot</h1>
            <p>Machine learning assistant</p>
          </div>
        </div>

        <button className="new-chat" onClick={clearChat}>
          <Sparkles size={17} /> New conversation
        </button>

        <div className="sidebar-section">
          <span className="section-label">TRY ASKING</span>
          {suggestions.map((suggestion) => (
            <button
              className="suggestion"
              key={suggestion}
              onClick={() => void sendMessage(undefined, suggestion)}
              disabled={loading}
            >
              <span className="suggestion-dot" />
              {suggestion}
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="status-indicator">
            {connected ? <Wifi size={16} /> : <WifiOff size={16} />}
            <span>{connected ? "Backend connected" : "Backend disconnected"}</span>
          </div>
          <p>Powered by TF-IDF &amp; Logistic Regression</p>
        </div>
      </aside>

      <section className="chat-panel">
        <header className="topbar">
          <div className="assistant-profile">
            <div className="avatar"><Bot size={22} /></div>
            <div>
              <h2>Your AI Assistant</h2>
              <p>
                <span className={`online-dot ${connected ? "active" : ""}`} />
                {connected ? "Online and ready" : "Waiting for backend"}
              </p>
            </div>
          </div>
          <button className="clear-button" onClick={clearChat} title="Clear chat">
            <Trash2 size={17} /><span>Clear chat</span>
          </button>
        </header>

        <div className="messages-area">
          <div className="welcome-block">
            <div className="welcome-icon"><Sparkles size={23} /></div>
            <h2>A little conversation goes a long way.</h2>
            <p>Ask a question or choose a suggestion to get started.</p>
          </div>

          <div className="messages-list">
            {messages.map((message) => (
              <div className={`message-row ${message.role}`} key={message.id}>
                <div className="message-avatar">
                  {message.role === "bot"
                    ? <Bot size={18} />
                    : <UserRound size={18} />}
                </div>
                <div className="message-content">
                  <span className="message-author">
                    {message.role === "bot" ? "NLP Assistant" : "You"}
                  </span>
                  <div className="message-bubble">{message.text}</div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row bot">
                <div className="message-avatar"><Bot size={18} /></div>
                <div className="message-content">
                  <span className="message-author">NLP Assistant</span>
                  <div className="message-bubble typing">Thinking...</div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <div className="composer-wrap">
          {!connected && (
            <p className="connection-note">
              Start your FastAPI backend to enable chat responses.
            </p>
          )}
          <form
            className="composer"
            onSubmit={(event) => void sendMessage(event)}
          >
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Type your message here..."
              aria-label="Your message"
              maxLength={2000}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </form>
          <p className="composer-hint">
            Enter to send · Your chatbot runs locally
          </p>
        </div>
      </section>
    </main>
  );
}
