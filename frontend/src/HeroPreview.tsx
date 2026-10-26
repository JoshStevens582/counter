/** Decorative hero mockup — site + chat widget in a browser frame. */
export function HeroPreview() {
  return (
    <div className="device-frame">
      <div className="device-bar">
        <span className="device-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span className="device-url">capetownphysio.co.za</span>
      </div>
      <div className="device-screen">
        <div className="mock-site">
          <div className="mock-nav" />
          <div className="mock-hero-line mock-hero-line-wide" />
          <div className="mock-hero-line" />
          <div className="mock-cards">
            <span />
            <span />
          </div>
        </div>
        <div className="mock-chat">
          <div className="mock-chat-head">Cape Town Physio</div>
          <div className="mock-chat-q">What does a session cost?</div>
          <div className="mock-chat-a">
            R650. <em>[1] Session fees</em>
          </div>
          <div className="mock-chat-src">Source on this site</div>
        </div>
      </div>
    </div>
  );
}
