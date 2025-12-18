/*
  manages light/dark mode.
*/

{
  // immediately load saved (or default) mode before page renders
  document.documentElement.dataset.dark =
    window.localStorage.getItem("dark-mode") ?? "true";

  // reduced motion: saved user preference overrides OS preference
  const getSavedMotion = () => {
    try {
      return window.localStorage.getItem("reduced-motion");
    } catch {
      return null;
    }
  };

  const prefersReducedMotion =
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const savedMotion = getSavedMotion();
  const reduced =
    savedMotion === "true" ? true : savedMotion === "false" ? false : prefersReducedMotion;

  document.documentElement.dataset.motion = reduced ? "reduced" : "full";

  const onLoad = () => {
    // update toggle button to match loaded mode
    document.querySelector(".dark-toggle").checked =
      document.documentElement.dataset.dark === "true";

    const motionToggle = document.querySelector(".motion-toggle");
    if (motionToggle) {
      motionToggle.checked = document.documentElement.dataset.motion === "reduced";
    }
  };

  // after page loads
  window.addEventListener("load", onLoad);

  // when user toggles mode button
  window.onDarkToggleChange = (event) => {
    const value = event.target.checked;
    document.documentElement.dataset.dark = value;
    window.localStorage.setItem("dark-mode", value);
  };

  window.onMotionToggleChange = (event) => {
    const value = Boolean(event.target.checked);
    document.documentElement.dataset.motion = value ? "reduced" : "full";
    try {
      window.localStorage.setItem("reduced-motion", value ? "true" : "false");
    } catch {
      // ignore
    }
  };
}
