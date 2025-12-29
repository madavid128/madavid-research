/*
  Auto-generate a "What's on this page" jump bar.

  - If a page already includes `.page-jumps` manually, do nothing.
  - Uses top-level headings (h2) and links to their IDs.
  - Works with anchors.js, which may move IDs from headings to parent <section>.
  - On desktop, the bar becomes a floating (fixed) chip row after you scroll past it.
*/

(() => {
  const setupActiveSection = (nav) => {
    if (!nav) return;
    if (nav.__activeReady) return;
    nav.__activeReady = true;

    const links = [...nav.querySelectorAll("a.page-jump")];
    const ids = links
      .map((a) => {
        const href = a.getAttribute("href") || "";
        if (!href.startsWith("#")) return "";
        try {
          return decodeURIComponent(href.slice(1));
        } catch {
          return href.slice(1);
        }
      })
      .filter(Boolean);

    const targets = ids
      .map((id) => document.getElementById(id))
      .filter(Boolean);

    if (!targets.length) return;

    const getPinnedHeaderHeight = () => {
      const header = document.querySelector("header");
      if (!header) return 0;
      const rect = header.getBoundingClientRect();
      const pinned = Math.abs(rect.top) < 1;
      return pinned ? Math.ceil(rect.height) : 0;
    };

    const setActive = (id) => {
      links.forEach((a) => {
        const href = a.getAttribute("href") || "";
        const match = href === `#${encodeURIComponent(id)}` || href === `#${id}`;
        a.classList.toggle("is-active", match);
        if (match) a.setAttribute("aria-current", "location");
        else a.removeAttribute("aria-current");
      });
    };

    const update = () => {
      const headerH = getPinnedHeaderHeight();
      const jumpH = nav.classList.contains("page-jumps--floating")
        ? Math.ceil(nav.getBoundingClientRect().height || 0) + 30
        : 30;
      // Add a small buffer so section detection doesn't "miss" after smooth scrolling.
      const topLine = headerH + jumpH + 24;
      let best = null;
      for (const el of targets) {
        const top = el.getBoundingClientRect().top;
        if (top <= topLine) best = el;
        else break;
      }
      if (best && best.id) setActive(best.id);
      else if (targets[0] && targets[0].id) setActive(targets[0].id);
    };

    let raf = null;
    const schedule = () => {
      if (raf) return;
      raf = window.requestAnimationFrame(() => {
        raf = null;
        update();
      });
    };

    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    window.addEventListener("load", schedule);
    schedule();

    links.forEach((a) => {
      a.addEventListener("click", () => {
        const href = a.getAttribute("href") || "";
        if (!href.startsWith("#")) return;
        const id = href.slice(1);
        try {
          setActive(decodeURIComponent(id));
        } catch {
          setActive(id);
        }
      });
    });
  };

  const setupFloating = (nav) => {
    if (!nav) return;
    if (nav.__floatingReady) return;
    nav.__floatingReady = true;

    // Placeholder keeps layout stable when the nav is moved to <body> for fixed positioning.
    const placeholder = document.createElement("div");
    placeholder.dataset.pageJumpsPlaceholder = "";
    placeholder.style.height = "0px";
    placeholder.style.margin = "0";
    placeholder.style.padding = "0";

    const homeParent = nav.parentNode;
    if (!homeParent) return;
    homeParent.insertBefore(placeholder, nav);

    const update = () => {
      const narrow =
        typeof window.matchMedia === "function" &&
        window.matchMedia("(max-width: 900px)").matches;

      // Offset the floating bar under the header *only while the header is actually pinned*.
      // This avoids the home page (big hero header) pushing the bar into the middle of the screen.
      const header = document.querySelector("header");
      const headerRect = header ? header.getBoundingClientRect() : null;
      const headerPinned = !!(headerRect && Math.abs(headerRect.top) < 1);
      const headerOffset = headerPinned ? Math.ceil(headerRect.height) : 0;

      const extraTop = narrow ? 10 : 12;
      nav.style.setProperty("--page-jumps-top", `${headerOffset + extraTop}px`);

      // Float when the bar would scroll under the header/top offset.
      const placeholderTop = placeholder.getBoundingClientRect().top;
      const shouldFloat = placeholderTop < headerOffset + extraTop;
      nav.classList.toggle("page-jumps--floating", shouldFloat);
      const navHeight = Math.ceil(nav.getBoundingClientRect().height || nav.scrollHeight || 0);
      placeholder.style.height = shouldFloat ? `${navHeight}px` : "0px";
      // On narrow screens, keep the bar compact (CSS already handles sizing).
      if (narrow) nav.classList.toggle("page-jumps--narrow", true);
      else nav.classList.remove("page-jumps--narrow");

      // Move the element to <body> when floating to avoid being constrained by any transformed ancestors.
      if (shouldFloat) {
        if (nav.parentNode !== document.body) document.body.appendChild(nav);
      } else {
        if (nav.parentNode === document.body) {
          // Restore to its original spot: right after placeholder.
          const next = placeholder.nextSibling;
          if (next) homeParent.insertBefore(nav, next);
          else homeParent.appendChild(nav);
        }
      }
    };

    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", () => window.requestAnimationFrame(update), { passive: true });
    window.addEventListener("load", update);
    update();
  };

  const build = () => {
    const main = document.querySelector("main");
    if (!main) return;
    const mode = (main.dataset.pageJumps || "on").toLowerCase();
    if (mode === "off" || mode === "false" || mode === "0") return;
    const existing = main.querySelector(".page-jumps");
    // If a manual jump bar exists and already has links, do nothing.
    // If it exists but is empty (e.g., Liquid rendered without links), populate it.
    if (existing) {
      const linksHost =
        existing.querySelector(".page-jumps-links") || existing;
      const hasLinks = linksHost.querySelectorAll("a.page-jump").length > 0;
      if (hasLinks) {
        setupFloating(existing);
        setupActiveSection(existing);
        return;
      }
    }

    // Use only main section headers to keep the jump bar concise.
    const headingSelector = "h2";

    const visibleText = (heading) => {
      const text = (heading && heading.textContent ? heading.textContent : "").trim();
      return text.replace(/\s+/g, " ").trim();
    };

    const resolveId = (heading) => {
      if (!heading) return "";
      if (heading.id) return heading.id;
      const section = heading.closest ? heading.closest("section[id]") : null;
      if (section && section.id) return section.id;
      return "";
    };

    const seen = new Set();
    const items = [];
    main.querySelectorAll(headingSelector).forEach((h) => {
      if (h.closest && h.closest(".page-jumps")) return;
      if (h.hasAttribute && h.hasAttribute("data-jump-ignore")) return;
      if (h.classList && h.classList.contains("jump-ignore")) return;
      const label = visibleText(h);
      if (!label) return;
      const id = resolveId(h);
      if (!id) return;
      if (seen.has(id)) return;
      seen.add(id);
      items.push({ id, label });
    });

    if (!items.length) return;

    const nav = existing || document.createElement("nav");
    nav.className = "page-jumps";
    nav.setAttribute("aria-label", "What's on this page");

    let title = nav.querySelector(".page-jumps-title");
    if (!title) {
      title = document.createElement("span");
      title.className = "page-jumps-title";
      title.textContent = "On this page";
      nav.appendChild(title);
    }

    let links = nav.querySelector(".page-jumps-links");
    if (!links) {
      links = document.createElement("div");
      links.className = "page-jumps-links";
      nav.appendChild(links);
    }
    links.innerHTML = "";

    items.forEach(({ id, label }) => {
      const a = document.createElement("a");
      a.className = "page-jump";
      a.href = `#${encodeURIComponent(id)}`;
      a.textContent = label;
      links.appendChild(a);
    });

    if (!existing) {
      const h1 = main.querySelector("h1");
      if (h1 && h1.parentNode) {
        h1.parentNode.insertBefore(nav, h1.nextSibling);
      } else {
        const firstSection = main.querySelector("section");
        if (firstSection) firstSection.insertBefore(nav, firstSection.firstChild);
        else main.insertBefore(nav, main.firstChild);
      }
    }

    setupFloating(nav);
    setupActiveSection(nav);
  };

  // Run after load so anchors.js has finalized IDs.
  window.addEventListener("anchorsready", build, { once: true });
  window.addEventListener("load", build);
})();
