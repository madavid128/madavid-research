/*
  Tags/Index page.
  - Loads `/search.json` and builds a tag directory with counts + deep links.
  - Supports `?tag=<tag>` in the URL.

  Notes:
  - CSV cannot embed thumbnails; use `python tools/gallery_from_csv.py preview ...` instead.
*/

(() => {
  const host = document.querySelector("[data-tags-index]");
  if (!host) return;

  const url = host.dataset.searchUrl || "/search.json";

  const normalize = (s) =>
    String(s || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ");

  const normalizeTag = (s) =>
    normalize(s)
      .replace(/[-_]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  const splitTags = (raw) => {
    if (!raw) return [];
    if (Array.isArray(raw)) return raw.map((t) => String(t)).map(normalizeTag).filter(Boolean);
    const s = String(raw);
    return s
      .split(/[;,]+/g)
      .map((t) => normalizeTag(t))
      .filter(Boolean);
  };

  const typeLabel = (t) => {
    const map = {
      publication: "Publications",
      project: "Projects",
      team: "People",
      update: "Updates",
      page: "Pages",
      post: "Blog",
      news: "News",
      picture: "Pictures",
      art: "Scientific art",
    };
    return map[t] || String(t || "Other");
  };

  const escapeHtml = (s) =>
    String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

  const getTagParam = () => {
    const u = new URL(window.location.href);
    const t = u.searchParams.get("tag");
    return t ? normalizeTag(t) : "";
  };

  const setTagParam = (tag) => {
    const u = new URL(window.location.href);
    if (!tag) u.searchParams.delete("tag");
    else u.searchParams.set("tag", tag);
    window.history.replaceState(null, "", u);
  };

  const renderShell = () => {
    host.innerHTML = `
      <div class="tags-index-controls">
        <label class="tags-index-search">
          <span class="sr-only">Filter tags</span>
          <input type="text" placeholder="Filter tags… (e.g., machine learning)" data-tags-filter>
        </label>
        <div class="tags-index-types" role="group" aria-label="Content types">
          <label><input type="checkbox" checked data-tags-type="publication"> Publications</label>
          <label><input type="checkbox" checked data-tags-type="project"> Projects</label>
          <label><input type="checkbox" checked data-tags-type="update"> Updates</label>
          <label><input type="checkbox" checked data-tags-type="picture"> Pictures</label>
          <label><input type="checkbox" checked data-tags-type="art"> Art</label>
          <label><input type="checkbox" checked data-tags-type="page"> Pages</label>
          <label><input type="checkbox" checked data-tags-type="team"> People</label>
        </div>
      </div>

      <div class="tags-index-grid">
        <div class="tags-index-panel">
          <div class="tags-index-panel-title">Tags</div>
          <div class="tags-index-tags" data-tags-list aria-live="polite"></div>
        </div>
        <div class="tags-index-panel">
          <div class="tags-index-panel-title">Matches</div>
          <div class="tags-index-results" data-tags-results aria-live="polite"></div>
        </div>
      </div>
    `;
  };

  const buildIndex = (items) => {
    // tag -> { display, total, types: {type: count}, items: [...] }
    const tagMap = new Map();

    (items || []).forEach((item) => {
      const tags = splitTags(item.tags);
      if (!tags.length) return;
      const type = String(item.type || "other");
      tags.forEach((tag) => {
        if (!tagMap.has(tag)) {
          tagMap.set(tag, { tag, display: tag, total: 0, types: {}, items: [] });
        }
        const entry = tagMap.get(tag);
        entry.total += 1;
        entry.types[type] = (entry.types[type] || 0) + 1;
        entry.items.push(item);
      });
    });

    return tagMap;
  };

  const sortByCountThenName = (a, b) => {
    if (b.total !== a.total) return b.total - a.total;
    return a.display.localeCompare(b.display);
  };

  const renderTags = (tagMap, { filterText, enabledTypes, activeTag }) => {
    const list = host.querySelector("[data-tags-list]");
    if (!list) return;

    const ft = normalizeTag(filterText);
    const tags = [...tagMap.values()]
      .filter((t) => (ft ? t.display.includes(ft) : true))
      .map((t) => {
        const visibleCount = Object.entries(t.types).reduce((acc, [type, count]) => {
          if (!enabledTypes.has(type)) return acc;
          return acc + count;
        }, 0);
        return { ...t, visibleCount };
      })
      .filter((t) => t.visibleCount > 0)
      .sort((a, b) => (b.visibleCount !== a.visibleCount ? b.visibleCount - a.visibleCount : sortByCountThenName(a, b)));

    if (!tags.length) {
      list.innerHTML = `<div class="tags-index-empty">No tags match your filters.</div>`;
      return;
    }

    list.innerHTML = tags
      .map((t) => {
        const isActive = activeTag && t.tag === activeTag;
        const tooltip = Object.entries(t.types)
          .filter(([type]) => enabledTypes.has(type))
          .sort((a, b) => b[1] - a[1])
          .map(([type, count]) => `${typeLabel(type)}: ${count}`)
          .join(" · ");
        return `
          <button type="button" class="tags-index-tag" data-tag="${escapeHtml(t.tag)}" ${
            isActive ? 'data-active="true"' : ""
          } data-tooltip="${escapeHtml(tooltip)}">
            <span class="tags-index-tag-name">${escapeHtml(t.display)}</span>
            <span class="tags-index-tag-count">${t.visibleCount}</span>
          </button>
        `;
      })
      .join("");
  };

  const groupItemsByType = (items) => {
    const groups = new Map();
    (items || []).forEach((it) => {
      const type = String(it.type || "other");
      if (!groups.has(type)) groups.set(type, []);
      groups.get(type).push(it);
    });
    // Sort groups by label
    return [...groups.entries()].sort((a, b) => typeLabel(a[0]).localeCompare(typeLabel(b[0])));
  };

  const renderResults = (tagMap, { enabledTypes, activeTag }) => {
    const results = host.querySelector("[data-tags-results]");
    if (!results) return;

    if (!activeTag) {
      results.innerHTML = `<div class="tags-index-empty">Select a tag to see matching items.</div>`;
      return;
    }

    const entry = tagMap.get(activeTag);
    if (!entry) {
      results.innerHTML = `<div class="tags-index-empty">Unknown tag.</div>`;
      return;
    }

    const filteredItems = entry.items.filter((it) => enabledTypes.has(String(it.type || "")));
    if (!filteredItems.length) {
      results.innerHTML = `<div class="tags-index-empty">No matching items for the current type filters.</div>`;
      return;
    }

    const groups = groupItemsByType(filteredItems);
    const html = groups
      .map(([type, items]) => {
        const label = typeLabel(type);
        const list = items
          .slice()
          .sort((a, b) => String(a.title || "").localeCompare(String(b.title || "")))
          .slice(0, 30)
          .map((it) => {
            const isExternal = /^https?:\/\//i.test(String(it.url || ""));
            const extAttrs = isExternal ? ' target="_blank" rel="noopener noreferrer"' : "";
            const desc = it.description ? `<div class="tags-index-item-desc">${escapeHtml(it.description)}</div>` : "";
            return `
              <li class="tags-index-item">
                <a href="${escapeHtml(it.url)}"${extAttrs}>${escapeHtml(it.title)}</a>
                ${desc}
              </li>
            `;
          })
          .join("");
        return `
          <div class="tags-index-group">
            <div class="tags-index-group-title">${escapeHtml(label)} <span class="tags-index-group-count">(${items.length})</span></div>
            <ul class="tags-index-items">${list}</ul>
          </div>
        `;
      })
      .join("");

    results.innerHTML = `
      <div class="tags-index-active">
        <div class="tags-index-active-title">Tag: <span class="tags-index-active-tag">${escapeHtml(activeTag)}</span></div>
        <button type="button" class="button" data-style="bare" data-tags-clear>Clear</button>
      </div>
      ${html}
    `;
  };

  const enabledTypesFromUi = () => {
    const enabled = new Set();
    host.querySelectorAll("input[data-tags-type]").forEach((input) => {
      if (input.checked) enabled.add(String(input.dataset.tagsType || ""));
    });
    return enabled;
  };

  const main = async () => {
    renderShell();

    const filterInput = host.querySelector("[data-tags-filter]");
    const typeInputs = [...host.querySelectorAll("input[data-tags-type]")];

    let activeTag = getTagParam();
    let filterText = "";
    let enabledTypes = enabledTypesFromUi();

    const resp = await fetch(url, { cache: "force-cache" });
    const items = await resp.json();
    const tagMap = buildIndex(items);

    const rerender = () => {
      enabledTypes = enabledTypesFromUi();
      renderTags(tagMap, { filterText, enabledTypes, activeTag });
      renderResults(tagMap, { enabledTypes, activeTag });
    };

    host.addEventListener("click", (e) => {
      const btn = e.target && e.target.closest ? e.target.closest("button[data-tag]") : null;
      if (btn) {
        activeTag = normalizeTag(btn.dataset.tag || "");
        setTagParam(activeTag);
        rerender();
        return;
      }
      const clear = e.target && e.target.closest ? e.target.closest("[data-tags-clear]") : null;
      if (clear) {
        activeTag = "";
        setTagParam("");
        rerender();
      }
    });

    if (filterInput) {
      filterInput.addEventListener("input", () => {
        filterText = String(filterInput.value || "");
        rerender();
      });
    }

    typeInputs.forEach((input) => {
      input.addEventListener("change", () => rerender());
    });

    rerender();
  };

  main().catch(() => {
    host.innerHTML = `<div class="tags-index-empty">Failed to load tag index.</div>`;
  });
})();

