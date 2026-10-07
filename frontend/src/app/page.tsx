"use client";

import {
  FormEvent,
  KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import ReactMarkdown from "react-markdown";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const API_URL = "http://127.0.0.1:8000";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm your Enterprise AI Assistant. Ask me anything about the organization, services, technology, or capabilities.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  // Keep the conversation scrolled to the newest message
  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // Focus input when page opens
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();

    const message = input.trim();

    if (!message || loading) {
      return;
    }

    const currentSessionId = sessionId ?? crypto.randomUUID();

    if (!sessionId) {
      setSessionId(currentSessionId);
    }

    // Add user message
    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: message,
      },
      {
        role: "assistant",
        content: "",
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          message,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to get a response from the server.");
      }

      if (!response.body) {
        throw new Error("The server did not return a response stream.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let assistantResponse = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, {
          stream: true,
        });

        assistantResponse += chunk;

        setMessages((current) => {
          const updated = [...current];
          const lastIndex = updated.length - 1;

          if (
            lastIndex >= 0 &&
            updated[lastIndex].role === "assistant"
          ) {
            updated[lastIndex] = {
              ...updated[lastIndex],
              content: assistantResponse,
            };
          }

          return updated;
        });
      }

      const finalChunk = decoder.decode();

      if (finalChunk) {
        assistantResponse += finalChunk;

        setMessages((current) => {
          const updated = [...current];
          const lastIndex = updated.length - 1;

          if (
            lastIndex >= 0 &&
            updated[lastIndex].role === "assistant"
          ) {
            updated[lastIndex] = {
              ...updated[lastIndex],
              content: assistantResponse,
            };
          }

          return updated;
        });
      }
    } catch {
      setMessages((current) => {
        const updated = [...current];
        const lastIndex = updated.length - 1;

        if (
          lastIndex >= 0 &&
          updated[lastIndex].role === "assistant"
        ) {
          updated[lastIndex] = {
            ...updated[lastIndex],
            content:
              "I'm sorry, but I couldn't connect to the chatbot service. Please make sure the FastAPI backend is running.",
          };
        }

        return updated;
      });
    } finally {
      setLoading(false);

      // Put the cursor back into the input
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    }
  }

  function handleInputKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      if (!loading && input.trim()) {
        event.currentTarget.form?.requestSubmit();
      }
    }
  }

  function clearConversation() {
    setSessionId(null);

    setMessages([
      {
        role: "assistant",
        content:
          "Hello! I'm your Enterprise AI Assistant. Ask me anything about the organization, services, technology, or capabilities.",
      },
    ]);

    setInput("");

    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  }

  return (
    <main className="h-screen overflow-hidden bg-slate-950 text-white">
      <div className="mx-auto flex h-full max-w-5xl flex-col px-4 py-5 sm:px-6">

        {/* Header */}
        <header className="shrink-0 border-b border-slate-800 pb-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">
                Enterprise AI Assistant
              </h1>

              <p className="mt-1 text-sm text-slate-400">
                Powered by Groq, OKF, FastAPI & PostgreSQL
              </p>
            </div>

            <button
              onClick={clearConversation}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
            >
              New Chat
            </button>
          </div>
        </header>

        {/* Chat area */}
        <section
          ref={messagesContainerRef}
          className="min-h-0 flex-1 overflow-y-auto py-6 pr-2"
        >
          <div className="space-y-5">

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "border border-slate-800 bg-slate-900 text-slate-200"
                  }`}
                >
                  {message.role === "assistant" ? (
                    <div className="max-w-none text-sm leading-6">
                      {message.content ? (
                        <ReactMarkdown>
                          {message.content}
                        </ReactMarkdown>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-slate-400">
                          <span>Thinking</span>
                          <span className="animate-pulse">
                            ...
                          </span>
                        </span>
                      )}
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap">
                      {message.content}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Input area */}
        <form
          onSubmit={sendMessage}
          className="shrink-0 border-t border-slate-800 pt-4"
        >
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleInputKeyDown}
              placeholder="Ask your question..."
              disabled={loading}
              rows={1}
              autoFocus
              className="
                flex-1
                resize-none
                rounded-xl
                border
                border-slate-700
                bg-slate-900
                px-4
                py-3
                text-sm
                text-white
                caret-white
                outline-none
                placeholder:text-slate-500
                focus:border-blue-500
                focus:ring-1
                focus:ring-blue-500
                disabled:opacity-50
              "
            />

            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="
                rounded-xl
                bg-blue-600
                px-6
                py-3
                text-sm
                font-medium
                transition
                hover:bg-blue-500
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>

          <p className="mt-2 text-center text-xs text-slate-600">
            Press Enter to send · Shift + Enter for a new line
          </p>
        </form>
      </div>
    </main>
  );
}