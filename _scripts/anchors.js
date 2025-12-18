/*
  creates link next to each heading that links to that section.
*/

{
  const slugify = (text) =>
    String(text || "")
      .toLowerCase()
      .trim()
      .replace(/['"]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");

  const onLoad = () => {
    // for each heading
    const headings = document.querySelectorAll(
      "h2, h3, h4, h5, h6"
    );
    for (const heading of headings) {
      // Ensure every heading has a stable id so "What's on this page" can link to it.
      if (!heading.id) {
        const base = slugify(heading.textContent);
        if (base) {
          let id = base;
          let i = 2;
          while (document.getElementById(id)) {
            id = `${base}-${i++}`;
          }
          heading.id = id;
        }
      }

      // create anchor link
      const link = document.createElement("a");
      link.classList.add("icon", "fa-solid", "fa-link", "anchor");
      link.href = "#" + heading.id;
      link.setAttribute("aria-label", "link to this section");
      heading.append(link);

      // if first heading in the section, move id to parent section
      if (heading.matches("section > :first-child")) {
        heading.parentElement.id = heading.id;
        heading.removeAttribute("id");
      }
    }

    // Signal that heading IDs/anchors are ready (used by page-jumps.js).
    window.dispatchEvent(new CustomEvent("anchorsready"));
  };

  // scroll to target of url hash
  const scrollToTarget = () => {
    const id = window.location.hash.replace("#", "");
    const target = document.getElementById(id);

    if (!target) return;
    const header = document.querySelector("header");
    const offset = (() => {
      if (!header) return 0;
      const style = getComputedStyle(header);
      // Only offset when the header is acting like a sticky top bar.
      // On the home page, the header is a large hero and should not push anchor jumps down.
      const top = Number(String(style.top || "").replace("px", ""));
      const stickyTop = style.position === "sticky" && Number.isFinite(top);
      if (!stickyTop) return 0;
      const rect = header.getBoundingClientRect();
      const pinned = Math.abs(rect.top) < 1;
      return pinned ? Math.ceil(rect.height) : 0;
    })();
    const jumps = document.querySelector(".page-jumps.page-jumps--floating");
    const jumpsOffset = jumps ? Math.ceil(jumps.getBoundingClientRect().height || 0) + 18 : 0;
    const prefersReducedMotion =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({
      top: target.getBoundingClientRect().top + window.scrollY - offset - jumpsOffset,
      behavior: prefersReducedMotion ? "auto" : "smooth",
    });
  };

  // after page loads
  window.addEventListener("load", onLoad);
  window.addEventListener("load", scrollToTarget);
  window.addEventListener("tagsfetched", scrollToTarget);

  // when hash nav happens
  window.addEventListener("hashchange", scrollToTarget);
}
