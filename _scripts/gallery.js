/*
  Lightweight lightbox for the masonry gallery.
  - Click an item to open in a <dialog>
  - Esc / click close to dismiss
  - Uses data attributes emitted by `_includes/gallery.html`
*/
{
  const init = () => {
    const dialog = document.querySelector("[data-gallery-lightbox]");
    if (!dialog) return;

    const img = dialog.querySelector("[data-gallery-img]");
    const meta = dialog.querySelector("[data-gallery-meta]");
    const closeBtn = dialog.querySelector("[data-gallery-close]");
    let galleryItems = [];
    let galleryIndex = -1;

    // Best-effort download deterrence:
    // - Disables right-click and drag-to-save within gallery + lightbox.
    // - This cannot prevent screenshots or determined downloading.
    const shouldBlock = (eventTarget) => {
      if (!eventTarget) return false;
      return Boolean(eventTarget.closest("[data-gallery], [data-gallery-lightbox]"));
    };

    document.addEventListener("contextmenu", (event) => {
      const target = event.target;
      if (!shouldBlock(target)) return;
      if (target && target.closest("img")) event.preventDefault();
    });

    document.addEventListener("dragstart", (event) => {
      const target = event.target;
      if (!shouldBlock(target)) return;
      if (target && target.closest("img")) event.preventDefault();
    });

    const isPicturesPage = (() => {
      const path = (window.location && window.location.pathname) || "";
      return path.includes("/pictures");
    })();

    const picturesNavHtml = () => {
      if (!isPicturesPage) return "";
      const items = [
        { id: "lab-mentors", label: "Lab" },
        { id: "milestones", label: "Milestones" },
        { id: "conferences-talks", label: "Talks" },
        { id: "beyond-the-lab", label: "Beyond" },
      ];
      const buttons = items
        .map(
          (x) =>
            `<button type="button" class="button" data-style="bare" data-gallery-jump="#${x.id}">${x.label}</button>`,
        )
        .join("");
      return `<div class="gallery-lightbox-nav" role="navigation" aria-label="Picture categories">${buttons}</div>`;
    };

    const permissionNote = () => {
      const path = (window.location && window.location.pathname) || "";
      const isArtPage = path.includes("/art");
      // Keep the note short inside the lightbox to avoid repeating the full policy text
      // that’s shown on the page itself under “Prints & permissions”.
      if (isPicturesPage || isArtPage) {
        return "© 2025 Michael A. David · See “Prints & permissions” on this page.";
      }
      return "© 2025 Michael A. David.";
    };

    const open = (src, title, subtitle) => {
      if (img) img.src = src || "";
      if (img) img.alt = title || "Image";
      if (meta) {
        const safeTitle = title ? `<div class="gallery-lightbox-title">${title}</div>` : "";
        const safeSubtitle = subtitle ? `<div class="gallery-lightbox-subtitle">${subtitle}</div>` : "";
        const note = `<div class="gallery-lightbox-note">${permissionNote()}</div>`;
        meta.innerHTML = `${safeTitle}${safeSubtitle}${picturesNavHtml()}${note}`;
      }
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
    };

    const getContext = (trigger) => {
      const root = trigger && trigger.closest ? trigger.closest("[data-gallery]") : null;
      const container = root || document;
      const items = [...container.querySelectorAll("[data-gallery-open]")].filter((el) => el.dataset.gallerySrc);
      return { container, items };
    };

    const openFromTrigger = (trigger) => {
      if (!trigger) return;
      const src = trigger.dataset.gallerySrc;
      if (!src) return;
      const title = trigger.dataset.galleryTitle || "";
      const subtitle = trigger.dataset.gallerySubtitle || "";
      const { items } = getContext(trigger);
      galleryItems = items;
      galleryIndex = items.indexOf(trigger);
      open(src, title, subtitle);
    };

    const close = () => {
      if (img) img.src = "";
      if (typeof dialog.close === "function") dialog.close();
      else dialog.removeAttribute("open");
      galleryItems = [];
      galleryIndex = -1;
    };

    if (meta) {
      meta.addEventListener("click", (event) => {
        const btn = event.target && event.target.closest ? event.target.closest("[data-gallery-jump]") : null;
        if (!btn) return;
        const hash = btn.getAttribute("data-gallery-jump") || "";
        if (!hash) return;
        close();
        // Defer the hash jump slightly so the dialog close doesn't interfere with scrolling.
        window.setTimeout(() => {
          window.location.hash = hash;
        }, 50);
      });
    }

    document.addEventListener("click", (event) => {
      const trigger = event.target.closest("[data-gallery-open]");
      if (!trigger) return;

      event.preventDefault();
      openFromTrigger(trigger);
    });

    if (closeBtn) closeBtn.addEventListener("click", close);
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) close();
    });
    window.addEventListener("keydown", (event) => {
      if (!dialog.hasAttribute("open")) return;
      if (event.key === "Escape") {
        close();
        return;
      }
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        if (!galleryItems.length || galleryIndex < 0) return;
        event.preventDefault();
        const dir = event.key === "ArrowRight" ? 1 : -1;
        const next = (galleryIndex + dir + galleryItems.length) % galleryItems.length;
        const trigger = galleryItems[next];
        if (!trigger) return;
        galleryIndex = next;
        const src = trigger.dataset.gallerySrc;
        const title = trigger.dataset.galleryTitle || "";
        const subtitle = trigger.dataset.gallerySubtitle || "";
        open(src, title, subtitle);
      }
    });
  };

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
}
