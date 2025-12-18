/*
  Global on-site search (no Google dependency).
  - Opens with "/" or the header search button.
  - Searches a build-time index at /search.json.
*/

(() => {
  const dialog = document.querySelector("[data-global-search]");
  if (!dialog) return;

  const input = dialog.querySelector(".global-search-input");
  const resultsHost = dialog.querySelector("[data-global-search-results]");
  const closeBtn = dialog.querySelector("[data-global-search-close]");
  const filterButtons = [...dialog.querySelectorAll("[data-global-search-type]")];
  const openButtons = [...document.querySelectorAll("[data-global-search-open]")];
  const helpBtn = dialog.querySelector("[data-global-search-help]");
  const helpPanel = dialog.querySelector("#global-search-help");

  let index = null;
  let activeType = "all";
  let activeIndex = -1;
  let lastFocus = null;

  const normalize = (s) =>
    String(s || "")
      .toLowerCase()
      .replace(/[-_]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  const safeText = (s) => String(s || "").replace(/\s+/g, " ").trim();
  const escapeHtml = (s) =>
    String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

  const highlight = (text, queryParts) => {
    const raw = safeText(text);
    const escaped = escapeHtml(raw);
    if (!queryParts || !queryParts.length) return escaped;

    // Highlight each query part, longest-first, case-insensitive.
    const parts = [...new Set(queryParts)].sort((a, b) => b.length - a.length).filter(Boolean);
    let out = escaped;
    parts.forEach((p) => {
      const re = new RegExp(`(${p.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&")})`, "ig");
      out = out.replace(re, "<mark class=\"global-search-mark\">$1</mark>");
    });
    return out;
  };

  const getResultLinks = () =>
    resultsHost ? [...resultsHost.querySelectorAll("a.global-search-item")] : [];

  const setActiveItem = (nextIndex) => {
    const links = getResultLinks();
    if (!links.length) {
      activeIndex = -1;
      return;
    }
    const clamped = Math.max(0, Math.min(nextIndex, links.length - 1));
    activeIndex = clamped;
    links.forEach((a, idx) => {
      const on = idx === clamped;
      a.classList.toggle("is-active", on);
      a.setAttribute("aria-selected", on ? "true" : "false");
    });
    const active = links[clamped];
    if (active && typeof active.scrollIntoView === "function") {
      active.scrollIntoView({ block: "nearest" });
    }
  };

  const loadIndex = async () => {
    if (index) return index;
    try {
      const url = dialog.dataset.searchUrl || "/search.json";
      const resp = await fetch(url, { cache: "force-cache" });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      index = await resp.json();
      return index;
    } catch (err) {
      if (resultsHost) {
        resultsHost.innerHTML = `<div class="global-search-empty">Search index failed to load.</div>`;
      }
      throw err;
    }
  };

  const typeLabel = (t) => {
    const map = {
      publication: "Publication",
      project: "Project",
      team: "People",
      update: "Updates",
      page: "Page",
      post: "Blog",
      news: "News",
      picture: "Picture",
      art: "Art",
    };
    return map[t] || t;
  };

  const render = (items, query, queryParts = []) => {
    if (!resultsHost) return;
    const q = safeText(query);
    if (!q) {
      resultsHost.innerHTML = `
        <div class="global-search-empty">
          Start typing to search…<br>
          Try: <span class="global-search-example">cartilage</span>, <span class="global-search-example">tendon</span>, <span class="global-search-example">machine learning</span>, <span class="global-search-example">year:2023</span>
        </div>
      `;
      activeIndex = -1;
      return;
    }
    if (!items.length) {
      resultsHost.innerHTML = `<div class="global-search-empty">No results for “${q}”.</div>`;
      activeIndex = -1;
      return;
    }

    const top = items.slice(0, 20);
    const listHtml = top
      .map((item) => {
        const title = highlight(item.title, queryParts);
        const desc = highlight(item.description, queryParts);
        const badge = typeLabel(item.type);
        const meta = item.year ? `${item.year}` : item.date ? `${String(item.date).slice(0, 10)}` : "";
        const isExternal = /^https?:\/\//i.test(String(item.url || ""));
        const externalAttrs = isExternal ? ' target="_blank" rel="noopener noreferrer"' : "";
        return `
          <a class="global-search-item" href="${item.url}"${externalAttrs}>
            <span class="global-search-badge">${badge}</span>
            <span class="global-search-title">${title}</span>
            ${meta ? `<span class="global-search-item-meta">${meta}</span>` : ""}
            ${desc ? `<span class="global-search-desc">${desc}</span>` : ""}
          </a>
        `;
      })
      .join("");
    resultsHost.innerHTML = `
      <div class="global-search-count">Showing ${top.length} of ${items.length} results</div>
      <div class="global-search-list" role="list">${listHtml}</div>
    `;

    // Reset selection to the first item for keyboard navigation.
    setActiveItem(0);
  };

  const search = async (query) => {
    const parse = (raw) => {
      const out = { text: raw || "", yearFrom: null, yearTo: null, type: null, tag: null };
      let s = String(raw || "");

      const yearRe = /\byear:(\d{4})(?:-(\d{4}))?\b/i;
      const ym = s.match(yearRe);
      if (ym) {
        out.yearFrom = Number(ym[1]);
        out.yearTo = ym[2] ? Number(ym[2]) : Number(ym[1]);
        s = s.replace(yearRe, " ");
      }

      const typeRe = /\btype:([a-z_-]+)\b/i;
      const tm = s.match(typeRe);
      if (tm) {
        out.type = normalize(tm[1]).replace(/\s+/g, "");
        s = s.replace(typeRe, " ");
      }

      const tagQuotedRe = /\btag:(["'])(.*?)\1/i;
      const tq = s.match(tagQuotedRe);
      if (tq) {
        out.tag = normalize(tq[2]);
        s = s.replace(tagQuotedRe, " ");
      } else {
        const tagRe = /\btag:([^\s]+)\b/i;
        const t = s.match(tagRe);
        if (t) {
          out.tag = normalize(t[1]);
          s = s.replace(tagRe, " ");
        }
      }

      out.text = s;
      return out;
    };

    const parsed = parse(query);
    const q = normalize(parsed.text);
    if (!q && !parsed.yearFrom && !parsed.tag && !parsed.type) return render([], "");
    const data = await loadIndex();
    const parts = q.split(" ").filter(Boolean);

    const scored = data
      .filter((item) => {
        if (!item || !item.title || !item.url) return false;
        const typeFilter = parsed.type || activeType;
        if (typeFilter !== "all" && item.type !== typeFilter) return false;

        const hay = normalize(
          `${item.title} ${item.description || ""} ${item.tags || ""} ${item.id || ""} ${item.year || ""} ${item.date || ""}`,
        );
        const matchesText = parts.every((p) => hay.includes(p));
        if (!matchesText && parts.length) return false;

        if (parsed.tag) {
          const tags = normalize(item.tags || "");
          if (!tags.includes(parsed.tag)) return false;
        }

        if (parsed.yearFrom) {
          const y = Number(item.year || (item.date ? String(item.date).slice(0, 4) : ""));
          if (!Number.isFinite(y)) return false;
          if (y < parsed.yearFrom) return false;
          if (parsed.yearTo && y > parsed.yearTo) return false;
        }

        return true;
      })
      .map((item) => {
        const title = normalize(item.title);
        const tags = normalize(item.tags || "");
        const desc = normalize(item.description || "");
        const score = parts.reduce((acc, p) => {
          if (title.includes(p)) acc += 4;
          if (tags.includes(p)) acc += 2;
          if (desc.includes(p)) acc += 1;
          return acc;
        }, 0);
        return { item, score };
      })
      .sort((a, b) => b.score - a.score);

    render(
      scored.map((x) => x.item),
      query,
      parts.concat(
        (parsed.yearFrom ? [`year:${parsed.yearFrom}${parsed.yearTo && parsed.yearTo !== parsed.yearFrom ? `-${parsed.yearTo}` : ""}`] : []),
        (parsed.tag ? [`tag:${parsed.tag}`] : []),
        (parsed.type ? [`type:${parsed.type}`] : []),
      ),
    );
  };

  const setActiveType = (t) => {
    activeType = t;
    filterButtons.forEach((btn) => {
      const isActive = btn.dataset.globalSearchType === t;
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
    search(input.value);
  };

  const open = async () => {
    lastFocus = document.activeElement;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
    input.value = "";
    activeIndex = -1;
    render([], "");
    if (helpPanel) helpPanel.hidden = true;
    if (helpBtn) helpBtn.setAttribute("aria-expanded", "false");
    input.focus();
    try {
      await loadIndex();
    } catch {
      // ignore (message already rendered)
    }
  };

  const close = () => {
    if (typeof dialog.close === "function") dialog.close();
    else dialog.removeAttribute("open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
    lastFocus = null;
  };

  // Wire open buttons
  openButtons.forEach((btn) => btn.addEventListener("click", open));

  // Keyboard shortcut (/), avoid interfering with typing.
  window.addEventListener("keydown", (event) => {
    const target = event.target;
    const isTyping =
      target &&
      (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);

    if (!isTyping && event.key === "/") {
      event.preventDefault();
      open();
    }
    // Common shortcut: Ctrl/Cmd + K
    if (!isTyping && (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      open();
    }
    if (event.key === "Escape" && dialog.hasAttribute("open")) close();
  });

  // Close button
  if (closeBtn) closeBtn.addEventListener("click", close);

  // Help toggle
  if (helpBtn && helpPanel) {
    helpBtn.addEventListener("click", () => {
      const open = !helpPanel.hidden;
      helpPanel.hidden = open;
      helpBtn.setAttribute("aria-expanded", open ? "false" : "true");
    });
  }

  // Clicking outside the dialog closes (native behavior), but keep input.
  dialog.addEventListener("close", () => {
    activeType = "all";
    setActiveType("all");
    if (helpPanel) helpPanel.hidden = true;
    if (helpBtn) helpBtn.setAttribute("aria-expanded", "false");
  });

  // Filters
  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => setActiveType(btn.dataset.globalSearchType));
  });

  // Search input
  let timer = null;
  input.addEventListener("input", () => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => search(input.value), 120);
  });

  // Click-to-search examples (rendered when the query is empty).
  if (resultsHost) {
    resultsHost.addEventListener("click", (event) => {
      const el = event.target;
      const example = el && el.closest ? el.closest(".global-search-example") : null;
      if (!example) return;
      const text = safeText(example.textContent);
      if (!text) return;
      input.value = text;
      search(input.value);
      input.focus();
    });
  }

  // Keyboard navigation inside the search box.
  input.addEventListener("keydown", (event) => {
    if (!dialog.hasAttribute("open")) return;
    const links = getResultLinks();
    if (!links.length) return;

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveItem(activeIndex + 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveItem(activeIndex - 1);
    } else if (event.key === "Enter") {
      event.preventDefault();
      const idx = activeIndex >= 0 ? activeIndex : 0;
      const a = links[idx];
      if (a && a.href) {
        close();
        window.location.href = a.href;
      }
    }
  });
})();
