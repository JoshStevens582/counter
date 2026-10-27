import { useEffect, useState } from "react";

import { fetchHealth, type HealthStatus } from "./api";
import { ChatWidget } from "./ChatWidget";
import type { RetrievedChunk } from "./types";

const PUBLISHED = [
  {
    title: "Session fees",
    body: "Standard one-on-one session R650. Initial assessment R650 for 45 minutes.",
  },
  {
    title: "Opening hours",
    body: "Monday–Friday, closing at 5:00 PM. Closed weekends and public holidays.",
  },
  {
    title: "Services",
    body: "Sports rehab, post-op, neck/back/shoulder, dry needling, home exercise programmes.",
  },
];

export function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [sources, setSources] = useState<RetrievedChunk[]>([]);
  const [injectMessage, setInjectMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  return (
    <div className="app">
      <aside className="panel sidebar">
        <div className="brand">
          <strong>COUNTER</strong>
          <span>Customer chat from your pages</span>
        </div>
        <p className="workspace-name">Cape Town Physio</p>
        <div className="health">
          <span
            className={`pill ${health === null ? "" : health.openai_configured ? "ok" : "warn"}`}
          >
            {health === null
              ? "Checking…"
              : health.openai_configured
                ? "OpenAI ready"
                : "API key missing"}
          </span>
          <span className="pill ok">{health?.page_count ?? "—"} pages</span>
          <span className="pill">{health?.chunk_count ?? "—"} chunks</span>
        </div>
        <p className="section-label">Try asking</p>
        <div className="stack">
          {[
            "What does a session cost?",
            "What time do you close?",
            "Do you treat sports injuries?",
          ].map((question) => (
            <button
              key={question}
              type="button"
              className="row"
              onClick={() => setInjectMessage(question)}
            >
              <span>
                {question}
                <small>Send to chat</small>
              </span>
            </button>
          ))}
        </div>
        <p className="suite-links">
          <a href="https://atlas.customchatandautomation.co.za" target="_blank" rel="noreferrer">
            Atlas
          </a>
          {" · "}
          <a href="https://agent.customchatandautomation.co.za" target="_blank" rel="noreferrer">
            Clerk
          </a>
        </p>
      </aside>

      <main className="panel main">
        <header className="chat-header">
          <h1>Cape Town Physio</h1>
          <p>City Bowl · grounded answers with page citations</p>
          <div className="pipeline">
            <div className="step active">
              <b>1. Ask</b>
              Patient or visitor question
            </div>
            <div className="step active">
              <b>2. Retrieve</b>
              Fees, hours, services
            </div>
            <div className="step">
              <b>3. Cite</b>
              Sources on the right
            </div>
          </div>
        </header>
        <ChatWidget
          embedded
          open
          onToggle={() => undefined}
          onSourcesChange={setSources}
          injectMessage={injectMessage}
          onInjectConsumed={() => setInjectMessage(null)}
        />
      </main>

      <aside className="panel sources">
        <p className="section-label">Sources for this reply</p>
        {sources.length === 0 ? (
          <p className="muted-copy">Chunks used in the answer appear here.</p>
        ) : (
          <div className="stack">
            {sources.map((chunk) => (
              <div
                key={`${chunk.document_id}-${chunk.chunk_index}`}
                className={`source-card ${chunk.cited ? "" : "unused"}`}
              >
                <header>
                  <strong>
                    [{chunk.cite_n}] {chunk.document_title}
                  </strong>
                  <span className="score">{chunk.distance.toFixed(3)}</span>
                </header>
                <p>
                  {chunk.text.slice(0, 220)}
                  {chunk.text.length > 220 ? "…" : ""}
                </p>
              </div>
            ))}
          </div>
        )}
        <p className="section-label">Published on this site</p>
        {PUBLISHED.map((page) => (
          <div key={page.title} className="source-card">
            <header>
              <strong>{page.title}</strong>
            </header>
            <p>{page.body}</p>
          </div>
        ))}
      </aside>
    </div>
  );
}
