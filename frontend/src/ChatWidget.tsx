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
  embedded?: boolean;
  open: boolean;
  onToggle: () => void;
  onSourcesChange?: (sources: RetrievedChunk[]) => void;
  injectMessage?: string | null;
  onInjectConsumed?: () => void;
};

function TypingIndicator() {
  return (
    <div className="msg-row bot" aria-live="polite" aria-label="Assistant is typing">
      <span className="msg-avatar" aria-hidden="true">
        AI
      </span>
      <div className="bubble assistant typing">
        <span className="typing-dots">
          <i />
          <i />
          <i />
        </span>
      </div>
    </div>
  );
}

export function ChatWidget({
  embedded = false,
  open,
  onToggle,
  onSourcesChange,
  injectMessage,
  onInjectConsumed,
}: Props) {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sources, setSources] = useState<RetrievedChunk[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesRef = useRef<HTMLDivElement>(null);

  const historyForApi = useMemo(() => turns.slice(-12), [turns]);

  const awaitingReply =
    busy && (turns.length === 0 || turns[turns.length - 1]?.role === "user");

  useEffect(() => {
    onSourcesChange?.(sources);
  }, [sources, onSourcesChange]);

  useEffect(() => {
    const node = messagesRef.current;
    if (!node) {
      return;
    }
    node.scrollTop = node.scrollHeight;
  }, [turns, busy, sources, open]);

  useEffect(() => {
    if (!injectMessage?.trim()) {
      return;
    }
    void sendMessage(injectMessage);
    onInjectConsumed?.();
  }, [injectMessage]);

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

  if (!embedded && !open) {
    return (
      <button
        type="button"
        className="chat-fab"
        onClick={onToggle}
        aria-expanded={false}
        aria-label="Open chat"
      >
        Ask
      </button>
    );
  }

  const panelClass = embedded ? "chat-embedded" : "chat-panel";

  return (
    <section className={panelClass} aria-label="Customer chat">
      {!embedded ? (
        <button type="button" className="chat-close" onClick={onToggle} aria-label="Close chat">
          ×
        </button>
      ) : null}
      <div className="workspace-body chat-body">
        {turns.length === 0 ? (
          <div className="empty">
            <p>
              Ask about <strong>fees</strong>, <strong>hours</strong>, or{" "}
              <strong>services</strong>. Answers cite the published pages — Counter does not
              book or send mail.
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
            <div className={turn.role === "user" ? "bubble user" : "bubble assistant"}>
              {turn.role === "assistant" ? (
                <ReactMarkdown>{turn.content}</ReactMarkdown>
              ) : (
                turn.content
              )}
            </div>
          </div>
        ))}
        {awaitingReply ? <TypingIndicator /> : null}
        {error ? <p className="error banner">{error}</p> : null}
      </div>
      {!busy && turns.length < 6 ? (
        <div className="prompts">
          {SUGGESTIONS.map((item) => (
            <button
              key={item}
              type="button"
              className="prompt"
              disabled={busy}
              onClick={() => void sendMessage(item)}
            >
              {item}
              <span>From your site pages</span>
            </button>
          ))}
        </div>
      ) : null}
      <form className="composer" onSubmit={onSubmit}>
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask a question…"
          disabled={busy}
          maxLength={8000}
          aria-label="Your question"
          rows={2}
        />
        <button type="submit" className="send" disabled={busy || !draft.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
