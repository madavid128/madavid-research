/*
  Expand/collapse groups of <details> elements.

  Markup:
    <div data-details-controls>
      <button data-details-action="expand">Expand all</button>
      <button data-details-action="collapse">Collapse all</button>
    </div>

  Scope:
  - Applies to <details> elements within the closest [data-directory-pane] or, if none,
    within the closest section.
*/

(() => {
  const closestScope = (root) =>
    root.closest("[data-directory-pane]") || root.closest("section") || document;

  const getDetails = (scope) =>
    [...scope.querySelectorAll("details")].filter((d) => !d.disabled);

  const setupOne = (wrap) => {
    if (wrap.__detailsBound) return;
    wrap.__detailsBound = true;

    const scope = closestScope(wrap);
    const expandBtn = wrap.querySelector("[data-details-action='expand']");
    const collapseBtn = wrap.querySelector("[data-details-action='collapse']");
    if (!expandBtn || !collapseBtn) return;

    expandBtn.addEventListener("click", () => {
      getDetails(scope).forEach((d) => (d.open = true));
    });

    collapseBtn.addEventListener("click", () => {
      getDetails(scope).forEach((d) => (d.open = false));
    });
  };

  const init = () => {
    document.querySelectorAll("[data-details-controls]").forEach(setupOne);
  };

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

