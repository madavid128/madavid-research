/*
  Open external links in a new tab.

  Rules:
  - Only affects http/https URLs that resolve to a different origin.
  - Skips links that already specify a target.
  - Adds rel="noopener noreferrer" for safety.
*/

(() => {
  const isHttpUrl = (href) => /^https?:\/\//i.test(href);

  const shouldMarkExternal = (anchor) => {
    if (anchor.hasAttribute("data-same-tab")) return false;
    if (anchor.classList?.contains("same-tab")) return false;

    const href = anchor.getAttribute("href");
    if (!href) return false;
    if (!isHttpUrl(href)) return false;
    if (anchor.hasAttribute("target")) return false;

    try {
      const url = new URL(href, window.location.href);
      return url.origin !== window.location.origin;
    } catch {
      return false;
    }
  };

  const apply = () => {
    document.querySelectorAll("a[href]").forEach((anchor) => {
      if (!shouldMarkExternal(anchor)) return;
      anchor.setAttribute("target", "_blank");

      const existingRel = anchor.getAttribute("rel") ?? "";
      const relParts = new Set(existingRel.split(/\s+/).filter(Boolean));
      relParts.add("noopener");
      relParts.add("noreferrer");
      anchor.setAttribute("rel", Array.from(relParts).join(" "));
    });
  };

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", apply, { once: true });
  } else {
    apply();
  }
})();
