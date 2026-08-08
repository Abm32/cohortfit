import type { ReactNode } from "react";
import { useInView } from "../../hooks/useInView";

interface RevealProps {
  children: ReactNode;
  className?: string;
  /** Stagger delay in ms, applied via CSS custom property. */
  delay?: number;
  as?: "div" | "section" | "li" | "ul";
}

/**
 * Wraps children in a scroll-reveal container. Adds `.reveal` immediately and
 * `.is-visible` once the element scrolls into view.
 */
export function Reveal({ children, className = "", delay = 0, as = "div" }: RevealProps) {
  const [ref, inView] = useInView<HTMLDivElement>();
  const Tag = as as "div";
  return (
    <Tag
      ref={ref}
      className={`reveal ${inView ? "is-visible" : ""} ${className}`.trim()}
      style={delay ? ({ "--reveal-delay": `${delay}ms` } as React.CSSProperties) : undefined}
    >
      {children}
    </Tag>
  );
}
