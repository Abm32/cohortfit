/**
 * Lightweight 2D mascots for the metabolism narrative. Pure inline SVG so they
 * cost nothing at runtime; motion is CSS (see landing.css .char-*).
 */

export function PillChar({ className = "" }: { className?: string }) {
  return (
    <svg
      className={`char char-pill ${className}`.trim()}
      viewBox="0 0 120 120"
      role="img"
      aria-label="Fluoropyrimidine capsule"
    >
      <g className="char-bob">
        <g transform="rotate(-25 60 60)">
          <rect x="30" y="42" width="60" height="36" rx="18" fill="#f8f7f2" stroke="#1b4332" strokeWidth="3" />
          <path d="M60 42 h30 a18 18 0 0 1 0 36 h-30 z" fill="#40916c" />
          <circle className="char-eye" cx="46" cy="58" r="3.4" fill="#1a1a18" />
          <circle className="char-eye" cx="58" cy="58" r="3.4" fill="#1a1a18" />
          <path d="M45 66 q7 6 14 0" stroke="#1a1a18" strokeWidth="2.4" fill="none" strokeLinecap="round" />
          <circle cx="98" cy="60" r="3" fill="#74c69d" />
        </g>
      </g>
    </svg>
  );
}

export function EnzymeChar({ variant = "healthy", className = "" }: { variant?: "healthy" | "broken"; className?: string }) {
  const broken = variant === "broken";
  return (
    <svg
      className={`char char-enzyme ${broken ? "char-enzyme-broken" : ""} ${className}`.trim()}
      viewBox="0 0 120 120"
      role="img"
      aria-label={broken ? "DPYD enzyme, reduced function" : "DPYD enzyme, normal function"}
    >
      <g className="char-bob">
        <path
          d="M60 16 C30 16 16 40 16 62 C16 92 40 106 60 106 C74 106 82 96 82 88 C82 80 74 76 66 76 C60 76 56 72 56 64 C56 56 60 52 66 52 C74 52 82 48 82 40 C82 30 74 16 60 16 Z"
          fill={broken ? "#c98a2b" : "#1b4332"}
        />
        <circle className="char-eye" cx="44" cy="52" r="4.6" fill="#f8f7f2" />
        <circle className="char-eye" cx="60" cy="52" r="4.6" fill="#f8f7f2" />
        <circle cx="44" cy="52" r="2.2" fill="#1a1a18" />
        <circle cx="60" cy="52" r="2.2" fill="#1a1a18" />
        {broken ? (
          <path d="M42 70 q10 -6 20 0" stroke="#1a1a18" strokeWidth="2.6" fill="none" strokeLinecap="round" />
        ) : (
          <path d="M42 68 q10 8 20 0" stroke="#1a1a18" strokeWidth="2.6" fill="none" strokeLinecap="round" />
        )}
        <circle className="char-active-site" cx="80" cy="64" r="7" fill={broken ? "#7a5216" : "#74c69d"} />
      </g>
    </svg>
  );
}

/** The story strip: drug meets enzyme; a broken enzyme lets the drug accumulate. */
export function MetabolismStrip() {
  return (
    <div className="metab-strip" aria-hidden="false">
      <div className="metab-node">
        <PillChar />
        <span className="metab-caption">Fluoropyrimidine dose</span>
      </div>
      <div className="metab-arrow">
        <span className="metab-arrow-line" />
        <span className="metab-arrow-head">→</span>
      </div>
      <div className="metab-node">
        <EnzymeChar variant="healthy" />
        <span className="metab-caption">DPYD clears it — Normal</span>
      </div>
      <div className="metab-arrow metab-arrow-danger">
        <span className="metab-arrow-line" />
        <span className="metab-arrow-head">→</span>
      </div>
      <div className="metab-node">
        <EnzymeChar variant="broken" />
        <span className="metab-caption">Reduced DPYD — drug accumulates</span>
      </div>
    </div>
  );
}
