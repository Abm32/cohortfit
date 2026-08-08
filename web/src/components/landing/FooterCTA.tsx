import { Link } from "react-router-dom";

export function FooterCTA() {
  return (
    <footer className="landing-footer-cta">
      <h2>Run the demo audit on your protocol mix.</h2>
      <p>
        Load the pinned sample report or trigger a live offline audit on the demo protocol — same
        engine as the CLI, same JSON schema.
      </p>
      <div className="landing-footer-cta-actions">
        <Link to="/app" className="landing-btn landing-btn-primary">
          Run demo audit
        </Link>
        <a
          href="https://github.com/Abm32/cohortfit#readme"
          className="landing-btn landing-btn-secondary"
          target="_blank"
          rel="noreferrer"
        >
          Read the docs
        </a>
      </div>
      <div className="landing-footer-meta">
        <span>cohortfit — deterministic PGx feasibility auditing</span>
        <div className="landing-footer-links">
          <a href="https://github.com/Abm32/cohortfit" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <Link to="/app">Demo app</Link>
          <a href="#pipeline">The pipeline</a>
        </div>
      </div>
    </footer>
  );
}
