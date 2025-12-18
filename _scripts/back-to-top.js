/*
  Back-to-top button.
  - Shows after scrolling down.
  - Smooth scroll unless user prefers reduced motion.
*/

(() => {
  const button = document.querySelector(".back-to-top");
  if (!button) return;

  const prefersReducedMotion =
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const showAfter = 600;

  const onScroll = () => {
    const y = window.scrollY || document.documentElement.scrollTop || 0;
    button.hidden = y < showAfter;
  };

  button.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: prefersReducedMotion ? "auto" : "smooth",
    });
  });

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("load", onScroll);
  onScroll();
})();

