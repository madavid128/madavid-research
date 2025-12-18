/*
  Toggle directory views (cards vs table) with persistence.

  Markup:
  - wrapper: [data-directory] with optional data-directory-key and data-directory-default
  - buttons: [data-directory-view="<pane>"]
  - panes:   [data-directory-pane="<pane>"]

  Persistence:
  - Stores the last selected view in localStorage keyed by data-directory-key.
*/

(() => {
  document.querySelectorAll("[data-directory]").forEach((root) => {
    const buttons = [...root.querySelectorAll("[data-directory-view]")];
    const panes = [...root.querySelectorAll("[data-directory-pane]")];
    const storageKey = root.dataset.directoryKey || "directory-view";

    const setView = (view) => {
      root.dataset.directoryActive = view;
      buttons.forEach((b) => {
        const active = b.dataset.directoryView === view;
        b.setAttribute("aria-pressed", active ? "true" : "false");
      });
      panes.forEach((p) => {
        p.hidden = p.dataset.directoryPane !== view;
      });
      try {
        window.localStorage.setItem(storageKey, view);
      } catch {
        // ignore
      }

      // Notify listeners (e.g., Plotly maps that need a resize after being shown).
      try {
        window.dispatchEvent(new CustomEvent("directoryviewchange", { detail: { key: storageKey, view } }));
      } catch {
        // ignore
      }
    };

    const initial = (() => {
      try {
        return window.localStorage.getItem(storageKey);
      } catch {
        return null;
      }
    })();

    setView(initial || root.dataset.directoryDefault || "cards");

    buttons.forEach((b) =>
      b.addEventListener("click", () => setView(b.dataset.directoryView)),
    );
  });
})();
