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

    const open = (src, title, subtitle) => {
      if (img) img.src = src || "";
      if (img) img.alt = title || "Image";
      if (meta) {
        const safeTitle = title ? `<div class="gallery-lightbox-title">${title}</div>` : "";
        const safeSubtitle = subtitle ? `<div class="gallery-lightbox-subtitle">${subtitle}</div>` : "";
        meta.innerHTML = `${safeTitle}${safeSubtitle}`;
      }
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
    };

    const close = () => {
      if (img) img.src = "";
      if (typeof dialog.close === "function") dialog.close();
      else dialog.removeAttribute("open");
    };

    document.addEventListener("click", (event) => {
      const trigger = event.target.closest("[data-gallery-open]");
      if (!trigger) return;

      const src = trigger.dataset.gallerySrc;
      if (!src) return;

      event.preventDefault();
      open(src, trigger.dataset.galleryTitle || "", trigger.dataset.gallerySubtitle || "");
    });

    if (closeBtn) closeBtn.addEventListener("click", close);
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) close();
    });
    window.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && dialog.hasAttribute("open")) close();
    });
  };

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
}
