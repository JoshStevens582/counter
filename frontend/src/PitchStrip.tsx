const STEPS = [
  {
    title: "Your pages go in once",
    body: "Fees, hours, services — the content you already publish on the site.",
  },
  {
    title: "Visitors ask in chat",
    body: "No login. The widget sits on your site like any support bubble.",
  },
  {
    title: "Answer shows the source",
    body: "Counter retrieves first, then writes. The page used appears with [1] in the reply.",
  },
] as const;

export function PitchStrip() {
  return (
    <section className="pitch-strip" id="counter-product" aria-labelledby="pitch-title">
      <div className="wrap pitch-inner">
        <header className="pitch-header">
          <p className="pitch-eyebrow">Counter · website chat</p>
          <h2 id="pitch-title">How this works on your client&apos;s site</h2>
          <p className="pitch-lede">
            This page is a sample clinic. Counter is the engine behind the chat — same
            product you deliver at <strong>R35,000</strong>, with your client&apos;s
            branding and pages.
          </p>
        </header>
        <ol className="pitch-steps">
          {STEPS.map((step, index) => (
            <li key={step.title}>
              <span className="pitch-num">{String(index + 1).padStart(2, "0")}</span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
        <p className="pitch-foot">
          Visitors see that they are speaking with AI, not staff. Does not book or
          send mail. If the pages do not say it, Counter says it does not know.{" "}
          <a href="https://github.com/JoshStevens582/counter" target="_blank" rel="noreferrer">
            Code on GitHub
          </a>
        </p>
      </div>
    </section>
  );
}
