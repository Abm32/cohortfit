import { useEffect, useRef, useState } from "react";

/**
 * Reveal-on-scroll helper. Returns a ref to attach and whether it has entered
 * the viewport at least once (we latch true so content never re-hides).
 */
export function useInView<T extends HTMLElement>(
  options: IntersectionObserverInit = { threshold: 0.2 },
): [React.RefObject<T>, boolean] {
  const ref = useRef<T>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || inView) return;
    if (typeof IntersectionObserver === "undefined") {
      setInView(true);
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
          break;
        }
      }
    }, options);
    observer.observe(node);
    return () => observer.disconnect();
  }, [inView, options]);

  return [ref, inView];
}
