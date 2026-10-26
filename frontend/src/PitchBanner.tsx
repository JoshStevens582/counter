import { useEffect, useState } from "react";

const STORAGE_KEY = "counter-pitch-banner-dismissed";

export function PitchBanner() {
  const [hidden, setHidden] = useState(true);

  useEffect(() => {
    setHidden(window.localStorage.getItem(STORAGE_KEY) === "1");
  }, []);

  function dismiss() {
    window.localStorage.setItem(STORAGE_KEY, "1");
    setHidden(true);
  }

  if (hidden) {
    return null;
  }

  return (
    <div className="pitch-banner" role="note">
      <div className="wrap pitch-banner-inner">
        <p>
          <strong>Counter showcase</strong> — sample client site.{" "}
          <a href="#counter-product">How the product works</a>
        </p>
        <button type="button" className="pitch-banner-close" onClick={dismiss}>
          Dismiss
        </button>
      </div>
    </div>
  );
}
