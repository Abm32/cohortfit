import { FooterCTA } from "./FooterCTA";
import { HeroSection } from "./HeroSection";
import { LandingNav } from "./LandingNav";
import { PinnedDataSection } from "./PinnedDataSection";
import { PipelineSection } from "./PipelineSection";
import { ProofSection } from "./ProofSection";
import { ResultsSection } from "./ResultsSection";
import { WhoItsForSection } from "./WhoItsForSection";

export function LandingPage() {
  return (
    <div className="landing">
      <LandingNav />
      <HeroSection />
      <PipelineSection />
      <PinnedDataSection />
      <WhoItsForSection />
      <ProofSection />
      <ResultsSection />
      <FooterCTA />
    </div>
  );
}
