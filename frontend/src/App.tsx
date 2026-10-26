import { useState } from "react";

import { ChatWidget } from "./ChatWidget";

export function App() {
  const [chatOpen, setChatOpen] = useState(true);

  return (
    <div className="site">
      <header className="site-header">
        <p className="eyebrow">Counter product demo — not a real clinic</p>
        <h1>Sample professional firm site</h1>
        <p className="lede">
          Stand-in content (fees, hours, services) shows how Counter works on your
          website. A paying client gets their own pages and branding.
        </p>
      </header>
      <main className="site-main">
        <section>
          <h2>Session fees</h2>
          <p>
            Standard one-on-one physiotherapy sessions are <strong>R650</strong>.
            Initial assessments are the same price for 45 minutes.
          </p>
        </section>
        <section>
          <h2>Opening hours</h2>
          <p>
            Monday to Friday, <strong>closing at 5:00 PM</strong>. Closed weekends and
            public holidays.
          </p>
        </section>
        <section>
          <h2>What we offer</h2>
          <ul>
            <li>Sports injury rehabilitation</li>
            <li>Neck, back, and shoulder treatment</li>
            <li>Post-operative physiotherapy</li>
          </ul>
        </section>
      </main>
      <footer className="site-footer">
        <p>
          Powered by Counter — Custom Chat and Automation demo. Answers come from the
          approved pages above, not from memory.
        </p>
      </footer>
      <ChatWidget open={chatOpen} onToggle={() => setChatOpen((value) => !value)} />
    </div>
  );
}
