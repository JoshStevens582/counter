import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

import { streamChat } from "./api";
import type { ChatTurn, RetrievedChunk } from "./types";

const SUGGESTIONS = [
  "What does a session cost?",
  "What time do you close?",
  "Do you treat sports injuries?",
  "Book me Tuesday at 2",
];

type Props = {
  open: boolean;
  onToggle: () => void;
};

function TypingIndicator() {
  return (
    <div className="msg-row bot" aria-live="polite" aria-label="Assistant is typing">
      <span className="msg-avatar" aria-hidden="true">
        AI
      </span>
      <div className="bubble bot typing">
        <span className="typing-dots">
          <i />
          <i />
          <i />
        </span>
      </div>
    </div>
  );
}

export function ChatWidget({ open, onToggle }: Props) {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sources, setSources] = useState<RetrievedChunk[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesRef = useRef<HTMLDivElement>(null);

  const historyForApi = useMemo(() => turns.slice(-12), [turns]);

  const awaitingReply =
    busy &&
    (turns.length === 0 || turns[turns.length - 1]?.role === "user");

  useEffect(() => {
    const node = messagesRef.current;
    if (!node) {
      return;
    }
    node.scrollTop = node.scrollHeight;
  }, [turns, busy, sources, open]);

  async function sendMessage(text: string) {
    const cleaned = text.trim();
    if (!cleaned || busy) {
      return;
    }
    setError(null);
    setBusy(true);
    setDraft("");
    setTurns((prev) => [...prev, { role: "user", content: cleaned }]);
    let answer = "";
    try {
      await streamChat(cleaned, historyForApi, (event) => {
        if (event.type === "sources") {
          setSources(event.sources);
        }
        if (event.type === "token") {
          answer += event.text;
          setTurns((prev) => {
            const copy = [...prev];
            const last = copy[copy.length - 1];
            if (last?.role === "assistant") {
              copy[copy.length - 1] = { role: "assistant", content: answer };
              return copy;
            }
            return [...copy, { role: "assistant", content: answer }];
          });
        }
        if (event.type === "error") {
          setError(event.detail);
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void sendMessage(draft);
  }

  return (
    <>
      {!open ? (
        <button
          type="button"
          className="chat-fab"
          onClick={onToggle}
          aria-expanded={false}
          aria-label="Open chat with AI assistant"
        >
          <span className="chat-fab-icon" aria-hidden="true" />
          <span className="chat-fab-label">Ask AI</span>
        </button>
      ) : null}
      {open ? (
        <section className="chat-panel" aria-label="Website chat">
          <header className="chat-header">
            <span className="chat-header-avatar" aria-hidden="true">
              CP
            </span>
            <div className="chat-header-text">
              <strong>Cape Town Physio</strong>
              <p className="chat-ai-label">AI assistant · not a live receptionist</p>
              <p>Answers from published fees, hours &amp; services</p>
            </div>
            <button
              type="button"
              className="chat-close"
              onClick={onToggle}
              aria-label="Close chat"
            >
              ×
            </button>
          </header>
          <div className="chat-messages" ref={messagesRef}>
            {turns.length === 0 ? (
              <div className="chat-welcome">
                <p>
                  You&apos;re chatting with an <strong>AI assistant</strong>, not a
                  person. Ask about fees, hours, or services. Each answer shows
                  which page it came from.
                </p>
              </div>
            ) : null}
            {turns.map((turn, index) => (
              <div
                key={`${index}-${turn.role}-${turn.content.slice(0, 24)}`}
                className={`msg-row ${turn.role === "user" ? "user" : "bot"}`}
              >
                {turn.role === "assistant" ? (
                  <span className="msg-avatar" aria-hidden="true">
                    AI
                  </span>
                ) : null}
                <div className={turn.role === "user" ? "bubble user" : "bubble bot"}>
                  {turn.role === "assistant" ? (
                    <ReactMarkdown>{turn.content}</ReactMarkdown>
                  ) : (
                    turn.content
                  )}
                </div>
              </div>
            ))}
            {awaitingReply ? <TypingIndicator /> : null}
            {error ? <p className="chat-error">{error}</p> : null}
          </div>
          {sources.length > 0 ? (
            <aside className="chat-sources">
              <h3>Source on this site</h3>
              {sources.map((chunk) => (
                <article
                  key={`${chunk.document_id}-${chunk.chunk_index}`}
                  className={chunk.cited ? "source cited" : "source"}
                >
                  <header>
                    [{chunk.cite_n}] {chunk.document_title}
                    {chunk.cited ? " · cited in reply" : ""}
                  </header>
                  <p>
                    {chunk.text.slice(0, 220)}
                    {chunk.text.length > 220 ? "…" : ""}
                  </p>
                </article>
              ))}
            </aside>
          ) : null}
          {!busy && turns.length < 6 ? (
            <div className="chat-suggestions">
              <span className="chat-suggestions-label">Try asking</span>
              <div className="chat-suggestions-chips">
                {SUGGESTIONS.map((item) => (
                  <button
                    key={item}
                    type="button"
                    disabled={busy}
                    onClick={() => void sendMessage(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
          <form className="chat-form" onSubmit={onSubmit}>
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask a question…"
              disabled={busy}
              maxLength={8000}
              aria-label="Your question"
            />
            <button type="submit" disabled={busy || !draft.trim()} aria-label="Send">
              ↑
            </button>
          </form>
        </section>
      ) : null}
    </>
  );
}
