/*
  Publications filter controls.
  - Uses search.js tokens: year:YYYY
  - Populates year dropdown from rendered citation elements.
*/

(() => {
  const root = document.querySelector("[data-publications-filters]");
  if (!root) return;

  const yearSelect = root.querySelector("[data-publications-year]");
  const typeSelect = root.querySelector("[data-publications-type]");
  const clearBtn = root.querySelector("[data-publications-clear]");

  const findSearchInput = () => {
    // Prefer the closest search box in the same section.
    const section = root.closest("section") || document;
    const input = section.querySelector(".search-box input");
    if (input) return input;
    return document.querySelector(".search-box input");
  };

  const stripYearTokens = (q) =>
    String(q || "")
      .replace(/\byear:\s*\d{4}(\s*-\s*\d{4})?\b/gi, "")
      .replace(/\s+/g, " ")
      .trim();

  const stripTypeTokens = (q) =>
    String(q || "")
      .replace(/\btype:\s*[a-z0-9_-]+\b/gi, "")
      .replace(/\s+/g, " ")
      .trim();

  const setYear = (year) => {
    const input = findSearchInput();
    if (!input) return;
    const base = stripYearTokens(input.value);
    input.value = year ? `${base ? `${base} ` : ""}year:${year}` : base;
    if (typeof window.onSearchInput === "function") window.onSearchInput(input);
  };

  const setType = (type) => {
    const input = findSearchInput();
    if (!input) return;
    const base = stripTypeTokens(input.value);
    input.value = type ? `${base ? `${base} ` : ""}type:${type}` : base;
    if (typeof window.onSearchInput === "function") window.onSearchInput(input);
  };

  const parseYear = (s) => {
    const y = Number(s);
    if (!Number.isFinite(y)) return null;
    if (y < 1900 || y > 2100) return null;
    return y;
  };

  const collectYears = () => {
    const counts = new Map();
    document.querySelectorAll(".citation-container[data-year]").forEach((el) => {
      const y = parseYear(el.dataset.year);
      if (!y) return;
      counts.set(y, (counts.get(y) || 0) + 1);
    });
    return counts;
  };

  const normalizeType = (s) =>
    String(s || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-");

  const collectTypes = () => {
    const counts = new Map();
    document.querySelectorAll(".citation-container[data-type]").forEach((el) => {
      const t = normalizeType(el.dataset.type);
      if (!t) return;
      counts.set(t, (counts.get(t) || 0) + 1);
    });
    return counts;
  };

  const init = () => {
    if (!yearSelect) return;
    const counts = collectYears();
    const years = [...counts.keys()].sort((a, b) => b - a);

    // reset options (keep "All")
    yearSelect.querySelectorAll("option:not([value=''])").forEach((o) => o.remove());
    years.forEach((y) => {
      const opt = document.createElement("option");
      opt.value = String(y);
      opt.textContent = `${y} (${counts.get(y)})`;
      yearSelect.appendChild(opt);
    });

    yearSelect.addEventListener("change", () => {
      const y = yearSelect.value ? parseYear(yearSelect.value) : null;
      setYear(y);
    });

    if (typeSelect) {
      const typeCounts = collectTypes();
      const types = [...typeCounts.keys()].sort((a, b) => a.localeCompare(b));
      typeSelect.querySelectorAll("option:not([value=''])").forEach((o) => o.remove());
      types.forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t;
        opt.textContent = `${t} (${typeCounts.get(t)})`;
        typeSelect.appendChild(opt);
      });
      typeSelect.addEventListener("change", () => {
        const t = typeSelect.value ? normalizeType(typeSelect.value) : null;
        setType(t);
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        yearSelect.value = "";
        if (typeSelect) typeSelect.value = "";
        setYear(null);
        setType(null);
      });
    }
  };

  window.addEventListener("load", init);
})();
