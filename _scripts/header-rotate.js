/**
 * Home header background rotation.
 *
 * Controlled by data attributes on the <header> element:
 * - `data-header-rotate`
 * - `data-header-rotate-images='[...]'` (JSON array of URLs)
 * - `data-header-rotate-interval="14000"` (ms)
 *
 * Respects reduced motion:
 * - OS setting: prefers-reduced-motion
 * - Site toggle: `document.documentElement.dataset.motion === "reduced"`
 *
 * CSS hooks (see `_styles/header.scss`):
 * - sets `--rotate-image` (CSS `url(...)`)
 * - toggles `data-rotate-show` to fade overlay
 *
 * SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2025 Michael A. David
 */

(() => {
  const header = document.querySelector("header[data-header-rotate]");
  if (!header) return;

  const prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const reducedByToggle = document.documentElement.dataset.motion === "reduced";
  if (prefersReducedMotion || reducedByToggle) return;

  const raw = header.dataset.headerRotateImages;
  if (!raw) return;

  let images;
  try {
    images = JSON.parse(raw);
  } catch {
    return;
  }
  if (!Array.isArray(images)) return;
  images = images.map((x) => (typeof x === "string" ? x.trim() : "")).filter(Boolean);
  if (images.length < 2) return;

  const intervalMs = Number.parseInt(header.dataset.headerRotateInterval || "14000", 10);
  const interval = Number.isFinite(intervalMs) && intervalMs > 2000 ? intervalMs : 14000;

  const FADE_MS = 1100;
  let index = -1;

  const setImageVar = (url) => {
    const safe = String(url).replaceAll('"', '\\"');
    header.style.setProperty("--rotate-image", `url(\"${safe}\")`);
  };

  const setBaseImage = (url) => {
    const safe = String(url).replaceAll('"', '\\"');
    header.style.setProperty("--image", `url(\"${safe}\")`);
  };

  const rotateOnce = () => {
    index = (index + 1) % images.length;
    const next = images[index];

    setImageVar(next);

    // Trigger fade in.
    requestAnimationFrame(() => {
      header.dataset.rotateShow = "true";
    });

    // After fade in completes, swap base, then fade overlay out.
    window.setTimeout(() => {
      setBaseImage(next);
      header.dataset.rotateShow = "false";
    }, FADE_MS);
  };

  window.setTimeout(() => {
    window.setInterval(rotateOnce, interval);
  }, interval);
})();
