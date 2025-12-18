/*
  Small navigation UX helpers:
  - Close the mobile nav when a link is clicked.
  - Close the mobile nav on Escape.
*/

(() => {
  const toggle = document.querySelector("header .nav-toggle");
  const nav = document.querySelector("header nav");
  if (!toggle || !nav) return;

  const close = () => {
    if (toggle.checked) toggle.checked = false;
  };

  nav.addEventListener("click", (event) => {
    const a = event.target && event.target.closest ? event.target.closest("a") : null;
    if (!a) return;
    close();
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
  });
})();

