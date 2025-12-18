/*
  Small layout metrics for CSS:
  - Sets --header-height so sticky elements can avoid the fixed header.
*/

(() => {
  const setHeaderHeight = () => {
    const header = document.querySelector("header");
    if (!header) return;
    const rect = header.getBoundingClientRect();

    // Only treat the header as "blocking" content when it's pinned at the top
    // (i.e., sticky header state). This prevents the large home hero header from
    // pushing fixed UI (e.g., jump bar) down into the middle of the viewport.
    const pinned = Math.abs(rect.top) < 1;
    const height = pinned ? Math.ceil(rect.height) : 0;
    document.documentElement.style.setProperty("--header-height", `${height}px`);
  };

  window.addEventListener("load", setHeaderHeight);
  window.addEventListener(
    "scroll",
    () => window.requestAnimationFrame(setHeaderHeight),
    { passive: true },
  );
  window.addEventListener(
    "resize",
    () => window.requestAnimationFrame(setHeaderHeight),
    { passive: true },
  );

  setHeaderHeight();
})();
