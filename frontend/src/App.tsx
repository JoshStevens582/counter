import { useState } from "react";

import { ChatWidget } from "./ChatWidget";
import { HeroPreview } from "./HeroPreview";
import { PitchBanner } from "./PitchBanner";
import { PitchStrip } from "./PitchStrip";

const NAV = [
  { href: "#fees", label: "Fees" },
  { href: "#hours", label: "Hours" },
  { href: "#services", label: "Services" },
  { href: "#visit", label: "Visit us" },
];

export function App() {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="site">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <PitchBanner />
      <header className="topbar">
        <div className="wrap topbar-inner">
          <a className="brand" href="#top">
            <span className="brand-mark" aria-hidden="true" />
            <span>
              <strong>Cape Town Physio</strong>
              <span className="brand-tag">City Bowl</span>
            </span>
          </a>
          <nav className="nav" aria-label="Primary">
            {NAV.map((item) => (
              <a key={item.href} href={item.href}>
                {item.label}
              </a>
            ))}
          </nav>
          <button
            type="button"
            className="nav-chat"
            onClick={() => setChatOpen(true)}
          >
            Questions?
          </button>
        </div>
      </header>

      <section className="hero" id="top">
        <div className="wrap hero-grid">
          <div className="hero-copy">
            <p className="hero-kicker">Physiotherapy · Sports · Rehab</p>
            <h1>Move better. Recover with a team that knows your schedule.</h1>
            <p className="hero-lede">
              One-on-one sessions in the City Bowl. Clear fees, evening-friendly
              hours, and treatment plans built around your goals.
            </p>
            <div className="hero-actions">
              <a className="btn btn-primary" href="#visit">
                Find us
              </a>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => setChatOpen(true)}
              >
                Ask about fees &amp; hours
              </button>
            </div>
            <ul className="hero-trust">
              <li>Card &amp; EFT</li>
              <li>45-min initial assessment</li>
              <li>Sports &amp; post-op rehab</li>
            </ul>
          </div>
          <HeroPreview />
        </div>
      </section>

      <main id="main">
        <section className="wrap section" id="fees">
          <h2>Session fees</h2>
          <p className="section-intro">
            Transparent pricing before you arrive. Medical-aid codes are handled at
            reception.
          </p>
          <div className="card-grid">
            <article className="card card-featured">
              <p className="card-label">Standard session</p>
              <p className="card-price">
                R650 <span>/ visit</span>
              </p>
              <p>One-on-one physiotherapy with your treating therapist.</p>
            </article>
            <article className="card">
              <p className="card-label">Initial assessment</p>
              <p className="card-price">
                R650 <span>/ 45 min</span>
              </p>
              <p>Full assessment and plan for new patients.</p>
            </article>
          </div>
        </section>

        <section className="wrap section section-muted" id="hours">
          <h2>Opening hours</h2>
          <div className="hours-block">
            <p>
              <strong>Monday – Friday</strong>
              <br />
              Open during the day, <strong>closing at 5:00 PM</strong>
            </p>
            <p className="hours-note">Closed weekends and public holidays.</p>
          </div>
        </section>

        <section className="wrap section" id="services">
          <h2>What we treat</h2>
          <ul className="service-list">
            <li>
              <strong>Sports injury rehabilitation</strong>
              <span>Return-to-play plans and load management.</span>
            </li>
            <li>
              <strong>Neck, back &amp; shoulder</strong>
              <span>Hands-on care and home exercise programs.</span>
            </li>
            <li>
              <strong>Post-operative physiotherapy</strong>
              <span>Structured rehab after surgery.</span>
            </li>
          </ul>
        </section>

        <section className="wrap section visit" id="visit">
          <h2>Visit us</h2>
          <p>
            14 Long Street, Cape Town City Bowl
            <br />
            Reception: <a href="tel:+27210000000">021 000 0000</a>
          </p>
          <p className="fine">
            Need fees, hours, or services? Use the chat — answers come from this
            page, not guesswork.
          </p>
        </section>
      </main>

      <PitchStrip />

      <footer className="site-footer">
        <div className="wrap footer-inner">
          <p>© {new Date().getFullYear()} Cape Town Physio</p>
          <p className="fine">
            Sample site for{" "}
            <a
              href="https://customchatandautomation.co.za"
              target="_blank"
              rel="noreferrer"
            >
              Custom Chat &amp; Automation
            </a>{" "}
            — Counter website chat
          </p>
        </div>
      </footer>

      <ChatWidget open={chatOpen} onToggle={() => setChatOpen((value) => !value)} />
    </div>
  );
}
