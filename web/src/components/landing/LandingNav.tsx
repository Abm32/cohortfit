import { Link } from "react-router-dom";

export function LandingNav() {
  return (
    <nav className="landing-nav">
      <Link to="/" className="landing-logo">
        <span className="landing-logo-mark">cf</span>
        cohortfit
      </Link>
      <div className="landing-nav-links">
        <a href="#pipeline">The pipeline</a>
        <a href="#audience">Who it&apos;s for</a>
        <a href="#findings">Findings</a>
        <a href="#method">Method</a>
        <a href="https://github.com/Abm32/cohortfit#readme" target="_blank" rel="noreferrer">
          Docs
        </a>
      </div>
      <Link to="/app" className="landing-btn landing-btn-primary">
        Run demo
      </Link>
    </nav>
  );
}
