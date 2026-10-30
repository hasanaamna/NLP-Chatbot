import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Bot,
  Send,
  Plus,
  UserRound,
  Sparkles,
  Wifi,
  WifiOff,
  RotateCcw,
  Copy,
  Check,
} from "lucide-react";
import "./App.css";

type Message = {
  id: string;
  role: "assistant" | "user";
  text: string;
};

type ChatResponse = {
  conversation_id?: string;
  response?: string;
  model?: string;
  detail?: string;
};

const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const REQUEST_TIMEOUT = 60000;
const HEALTH_CHECK_INTERVAL = 15000;

const suggestions = [
  {
    title: "Explain a concept",
    prompt: "Explain artificial intelligence in simple words.",
    icon: "✦",
  },
  {
    title: "Help with code",
    prompt: "Help me write a Python function to check if a number is prime.",
    icon: "</>",
  },
  {
    title: "Learn something",
    prompt: "Teach me the basics of machine learning with an example.",
    icon: "↗",
  },
  {
    title: "Improve my writing",
    prompt: "Give me tips to make my writing clearer and more professional.",
    icon: "✎",
  },
];

const initialMessage: Message = {
  id: "welcome",
  role: "assistant",
  text: "Hi! I'm your AI assistant. Ask me a question, explore an idea, or work through a problem with me. What would you like to talk about?",
};

function createMessageId(): string {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function getErrorMessage(
  status: number,
  detail?: string,
): string {
  if (status === 429) {
    return (
      detail ||
      "The AI service has reached its usage limit. Please wait before trying again."
    );
  }

  if (status === 401 || status === 403) {
    return (
      detail ||
      "The AI service rejected the request. Please check the backend API configuration."
    );
  }

  if (status >= 500) {
    return (
      detail ||
      "The backend or AI service encountered an error. Please try again later."
    );
  }

  return detail || `The server returned HTTP ${status}.`;
}

function MarkdownMessage({ text }: { text: string }) {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children, ...props }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            >
              {children}
            </a>
          ),
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    initialMessage,
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);

  const [conversationId, setConversationId] = useState<
    string | null
  >(null);

  const [modelName, setModelName] = useState("Groq AI");
  const [error, setError] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(
    null,
  );

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const requestInProgressRef = useRef(false);

  // Check whether the FastAPI backend is available.
  useEffect(() => {
    let mounted = true;
    let healthController: AbortController | null = null;

    async function checkHealth() {
      healthController?.abort();

      const controller = new AbortController();
      healthController = controller;

      try {
        const response = await fetch(`${API_URL}/health`, {
          method: "GET",
          signal: controller.signal,
          cache: "no-store",
        });

        if (mounted && !controller.signal.aborted) {
          setConnected(response.ok);
        }
      } catch {
        if (mounted && !controller.signal.aborted) {
          setConnected(false);
        }
      }
    }

    void checkHealth();

    const interval = window.setInterval(() => {
      void checkHealth();
    }, HEALTH_CHECK_INTERVAL);

    return () => {
      mounted = false;
      healthController?.abort();
      window.clearInterval(interval);
    };
  }, []);

  // Scroll to the latest message when the conversation changes.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  // Send a message to the FastAPI backend.
  async function sendMessage(
    event?: FormEvent,
    suggestedText?: string,
  ) {
    event?.preventDefault();

    const text = (suggestedText ?? input).trim();

    if (!text || requestInProgressRef.current) {
      return;
    }

    requestInProgressRef.current = true;

    setError("");
    setInput("");
    setLoading(true);

    const userMessage: Message = {
      id: createMessageId(),
      role: "user",
      text,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    const controller = new AbortController();

    const timeoutId = window.setTimeout(() => {
      controller.abort();
    }, REQUEST_TIMEOUT);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controller.signal,
        body: JSON.stringify({
          message: text,
          ...(conversationId
            ? { conversation_id: conversationId }
            : {}),
        }),
      });

      let data: ChatResponse = {};

      try {
        data = (await response.json()) as ChatResponse;
      } catch {
        data = {};
      }

      if (!response.ok) {
        throw new Error(
          getErrorMessage(
            response.status,
            typeof data.detail === "string"
              ? data.detail
              : undefined,
          ),
        );
      }

      if (
        typeof data.response !== "string" ||
        !data.response.trim() ||
        typeof data.conversation_id !== "string" ||
        !data.conversation_id.trim()
      ) {
        throw new Error(
          "The backend returned an incomplete response. Please check the /chat API response format.",
        );
      }

      setConversationId(data.conversation_id);

      if (data.model) {
        setModelName(data.model);
      }

      const assistantMessage: Message = {
        id: createMessageId(),
        role: "assistant",
        text: data.response,
      };

      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);

      setConnected(true);
    } catch (err) {
      let message =
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again.";

      if (
        err instanceof DOMException &&
        err.name === "AbortError"
      ) {
        message =
          "The request timed out. Please check your backend and try again.";
      } else if (
        message.toLowerCase().includes("failed to fetch") ||
        message.toLowerCase().includes("networkerror") ||
        message.toLowerCase().includes("load failed")
      ) {
        message =
          "Unable to connect to the backend. Make sure FastAPI is running at " +
          API_URL;
        setConnected(false);
      }

      // Preserve the user's message so it can be sent again.
      setInput((current) => current || text);

      // Show the error only once in the error banner.
      setError(message);
    } finally {
      window.clearTimeout(timeoutId);

      requestInProgressRef.current = false;
      setLoading(false);

      window.setTimeout(() => {
        inputRef.current?.focus();
      }, 0);
    }
  }

  // Start a fresh conversation.
  function newConversation() {
    if (requestInProgressRef.current) {
      return;
    }

    setConversationId(null);

    setMessages([
      {
        ...initialMessage,
        id: createMessageId(),
        text: "New conversation started. What would you like to explore?",
      },
    ]);

    setInput("");
    setError("");
    setCopiedId(null);

    inputRef.current?.focus();
  }

  // Copy an assistant response.
  async function copyMessage(message: Message) {
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("Clipboard unavailable");
      }

      await navigator.clipboard.writeText(message.text);

      setCopiedId(message.id);

      window.setTimeout(() => {
        setCopiedId((current) =>
          current === message.id ? null : current,
        );
      }, 1600);
    } catch {
      setError(
        "Unable to copy the response. Check your browser's clipboard permissions.",
      );
    }
  }

  return (
    <main className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={23} />
          </div>

          <div className="brand-copy">
            <h1>AI Assistant</h1>
            <p>Your AI thinking partner</p>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={newConversation}
          disabled={loading}
        >
          <Plus size={18} />
          <span>New conversation</span>
        </button>

        <div className="sidebar-section">
          <span className="section-label">
            START WITH AN IDEA
          </span>

          {suggestions.map((suggestion) => (
            <button
              className="suggestion"
              key={suggestion.title}
              onClick={() =>
                void sendMessage(undefined, suggestion.prompt)
              }
              disabled={loading}
              title={suggestion.prompt}
            >
              <span className="suggestion-icon">
                {suggestion.icon}
              </span>

              <span>{suggestion.title}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-spacer" />

        <div className="sidebar-footer">
          <div className="status-indicator">
            {connected ? (
              <Wifi size={16} />
            ) : (
              <WifiOff size={16} />
            )}

            <span>
              {connected
                ? "Backend connected"
                : "Backend disconnected"}
            </span>

            <span
              className={`status-dot ${
                connected ? "active" : ""
              }`}
            />
          </div>

          <div className="provider-card">
            <span className="provider-mark">
              <Sparkles size={14} />
            </span>

            <div>
              <strong>{modelName}</strong>
              <p>AI response engine</p>
            </div>
          </div>

          <p className="privacy-note">
            Conversation context stays in memory while the
            backend is running.
          </p>
        </div>
      </aside>

      {/* Main chat panel */}
      <section className="chat-panel">
        <header className="topbar">
          <div className="assistant-profile">
            <div className="avatar">
              <Bot size={21} />
            </div>

            <div>
              <h2>AI Assistant</h2>

              <p>
                <span
                  className={`online-dot ${
                    connected ? "active" : ""
                  }`}
                />

                {connected
                  ? "Ready when you are"
                  : "Waiting for backend"}
              </p>
            </div>
          </div>

          <div className="topbar-actions">
            <span className="model-pill">
              <span />
              Groq-powered
            </span>

            <button
              className="clear-button"
              onClick={newConversation}
              disabled={loading}
              title="Start a fresh conversation"
            >
              <RotateCcw size={16} />
              <span>New chat</span>
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="messages-area">
          {messages.length === 1 &&
            messages[0].id === "welcome" && (
              <div className="welcome-block">
                <div className="welcome-orb">
                  <Sparkles size={26} />
                </div>

                <p className="eyebrow">
                  A LITTLE HELP GOES A LONG WAY
                </p>

                <h2>What’s on your mind?</h2>

                <p className="welcome-subtitle">
                  Ask a question, explore an idea, or turn a
                  challenge into a plan.
                </p>

                <div className="welcome-suggestions">
                  {suggestions.map((suggestion) => (
                    <button
                      key={suggestion.title}
                      className="welcome-suggestion"
                      onClick={() =>
                        void sendMessage(
                          undefined,
                          suggestion.prompt,
                        )
                      }
                      disabled={loading}
                    >
                      <span>{suggestion.icon}</span>
                      <strong>{suggestion.title}</strong>
                      <small>{suggestion.prompt}</small>
                    </button>
                  ))}
                </div>
              </div>
            )}

          <div className="messages-list">
            {messages.map((message) => (
              <div
                className={`message-row ${message.role}`}
                key={message.id}
              >
                <div
                  className={`message-avatar ${message.role}`}
                >
                  {message.role === "assistant" ? (
                    <Sparkles size={17} />
                  ) : (
                    <UserRound size={17} />
                  )}
                </div>

                <div className="message-content">
                  <div className="message-meta">
                    <span className="message-author">
                      {message.role === "assistant"
                        ? "AI Assistant"
                        : "You"}
                    </span>

                    {message.role === "assistant" &&
                      message.id !== "welcome" && (
                        <button
                          className="copy-button"
                          onClick={() =>
                            void copyMessage(message)
                          }
                          title="Copy response"
                          aria-label="Copy response"
                        >
                          {copiedId === message.id ? (
                            <Check size={14} />
                          ) : (
                            <Copy size={14} />
                          )}

                          <span>
                            {copiedId === message.id
                              ? "Copied"
                              : "Copy"}
                          </span>
                        </button>
                      )}
                  </div>

                  <div className="message-bubble">
                    {message.role === "assistant" ? (
                      <MarkdownMessage text={message.text} />
                    ) : (
                      <div className="user-message-text">
                        {message.text}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="message-row assistant">
                <div className="message-avatar assistant">
                  <Sparkles size={17} />
                </div>

                <div className="message-content">
                  <span className="message-author">
                    AI Assistant
                  </span>

                  <div className="message-bubble typing-bubble">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />

                    <span className="typing-label">
                      Thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        {/* Message composer */}
        <div className="composer-wrap">
          {!connected && (
            <p className="connection-note">
              Start the FastAPI backend at{" "}
              <code>127.0.0.1:8000</code> to chat.
            </p>
          )}

          {error && (
            <div className="error-banner" role="alert">
              <span>{error}</span>

              <button
                onClick={() => setError("")}
                aria-label="Dismiss error"
                title="Dismiss error"
              >
                ×
              </button>
            </div>
          )}

          <form
            className="composer"
            onSubmit={(event) => void sendMessage(event)}
          >
            <input
              ref={inputRef}
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              placeholder="Message your AI assistant..."
              aria-label="Your message"
              maxLength={8000}
              disabled={loading}
            />

            <span className="composer-divider" />

            <button
              type="submit"
              disabled={!input.trim() || loading}
              aria-label="Send message"
              title="Send message"
            >
              <Send size={17} />
            </button>
          </form>

          <p className="composer-hint">
            AI can make mistakes. Check important information.
            <span> · </span>
            Enter to send
          </p>
        </div>
      </section>
    </main>
  );
}