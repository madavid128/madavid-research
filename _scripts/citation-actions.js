/*
  Citation actions:
  - Copy formatted citation text
  - Download BibTeX

  Data source:
    <script type="application/json" class="citation-actions-data">{...}</script>
*/

(() => {
  const readData = (root) => {
    const el = root.querySelector(".citation-actions-data");
    if (!el) return null;
    try {
      return JSON.parse(el.textContent || "{}");
    } catch {
      return null;
    }
  };

  const copyText = async (text) => {
    const value = String(text || "").trim();
    if (!value) return false;
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        await navigator.clipboard.writeText(value);
        return true;
      }
    } catch {
      // fall back
    }

    try {
      const ta = document.createElement("textarea");
      ta.value = value;
      ta.setAttribute("readonly", "readonly");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      return true;
    } catch {
      return false;
    }
  };

  const downloadText = (text, filename) => {
    const value = String(text || "");
    if (!value) return;
    const safe = String(filename || "citation.bib").replace(/[^\w.\-]+/g, "_");
    const blob = new Blob([value], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = safe;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const setupOne = (root) => {
    const data = readData(root);
    if (!data) return;

    root.querySelectorAll("[data-citation-action]").forEach((btn) => {
      if (btn.__citationActionBound) return;
      btn.__citationActionBound = true;
      btn.addEventListener("click", async () => {
        const action = btn.dataset.citationAction;
        if (action === "copy") {
          const ok = await copyText(data.text);
          btn.setAttribute("data-tooltip", ok ? "Copied!" : "Copy failed");
          window.setTimeout(() => btn.setAttribute("data-tooltip", "Copy citation"), 1200);
        } else if (action === "bib") {
          downloadText(data.bib, data.filename);
        }
      });
    });
  };

  const init = () => {
    document
      .querySelectorAll("[data-has-citation-actions='true']")
      .forEach(setupOne);
  };

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
