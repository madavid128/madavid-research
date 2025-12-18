/*
  Simple client-side table sorting.
  Requires:
  - table[data-sort-table]
  - header buttons with [data-sort-key]
  - row <tr> cells store sortable data as data-<key> attributes
*/

(() => {
  const parseValue = (s) => String(s || "").trim().toLowerCase();
  const parseMaybeNumber = (s) => {
    const n = Number(String(s || "").replace(/[^\d.-]/g, ""));
    return Number.isFinite(n) ? n : null;
  };

  document.querySelectorAll("table[data-sort-table]").forEach((table) => {
    const tbody = table.querySelector("tbody");
    const rows = () => [...(tbody ? tbody.querySelectorAll("tr") : [])];
    if (!tbody) return;

    let state = { key: null, dir: "asc" };

    const sortBy = (key) => {
      const nextDir = state.key === key && state.dir === "asc" ? "desc" : "asc";
      state = { key, dir: nextDir };

      const sorted = rows().sort((a, b) => {
        const av = a.dataset[key] || "";
        const bv = b.dataset[key] || "";
        const an = parseMaybeNumber(av);
        const bn = parseMaybeNumber(bv);
        let cmp;
        if (an !== null && bn !== null) cmp = an - bn;
        else cmp = parseValue(av).localeCompare(parseValue(bv));
        return nextDir === "asc" ? cmp : -cmp;
      });

      sorted.forEach((r) => tbody.appendChild(r));
    };

    table.querySelectorAll("[data-sort-key]").forEach((btn) => {
      btn.addEventListener("click", () => sortBy(btn.dataset.sortKey));
    });
  });
})();

