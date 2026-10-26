import { FormEvent, useMemo, useState } from "react";
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

export function ChatWidget({ open, onToggle }: Props) {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sources, setSources] = useState<RetrievedChunk[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const historyForApi = useMemo(
    () => turns.slice(-12),
    [turns],
  );

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
      <button
        type="button"
        className="chat-launcher"
        onClick={onToggle}
        aria-expanded={open}
      >
        {open ? "Close chat" : "Ask us anything"}
      </button>
      {open ? (
        <section className="chat-panel" aria-label="Counter customer chat">
          <header className="chat-header">
            <div>
              <strong>Ask the firm</strong>
              <p>Demo chat — answers from published pages only. No login.</p>
            </div>
          </header>
          <div className="chat-messages">
            {turns.length === 0 ? (
              <p className="chat-hint">
                Try a question about fees, hours, or what we offer.
              </p>
            ) : null}
            {turns.map((turn, index) => (
              <div
                key={`${index}-${turn.role}`}
                className={turn.role === "user" ? "bubble user" : "bubble bot"}
              >
                {turn.role === "assistant" ? (
                  <ReactMarkdown>{turn.content}</ReactMarkdown>
                ) : (
                  turn.content
                )}
              </div>
            ))}
            {busy ? <p className="chat-status">Thinking…</p> : null}
            {error ? <p className="chat-error">{error}</p> : null}
          </div>
          {sources.length > 0 ? (
            <aside className="chat-sources">
              <h3>Pages used</h3>
              {sources.map((chunk) => (
                <article
                  key={`${chunk.document_id}-${chunk.chunk_index}`}
                  className={chunk.cited ? "source cited" : "source"}
                >
                  <header>
                    [{chunk.cite_n}] {chunk.document_title}
                    {chunk.cited ? " · in answer" : ""}
                  </header>
                  <p>{chunk.text.slice(0, 220)}{chunk.text.length > 220 ? "…" : ""}</p>
                </article>
              ))}
            </aside>
          ) : null}
          <div className="chat-suggestions">
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
          <form className="chat-form" onSubmit={onSubmit}>
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Type your question…"
              disabled={busy}
              maxLength={8000}
            />
            <button type="submit" disabled={busy || !draft.trim()}>
              Send
            </button>
          </form>
        </section>
      ) : null}
    </>
  );
}
