/*
  Contact page helper:
  Build a pre-filled email draft via `mailto:` (no backend).
*/

(() => {
  const root = document.querySelector("[data-contact-mailto]");
  if (!root) return;

  const email = root.dataset.email || "";
  const topic = root.querySelector("[data-contact-topic]");
  const name = root.querySelector("[data-contact-name]");
  const message = root.querySelector("[data-contact-message]");
  const send = root.querySelector("[data-contact-send]");

  if (!email || !send) return;

  const enc = encodeURIComponent;

  const build = () => {
    const topicValue = topic ? String(topic.value || "").trim() : "Contact";
    const nameValue = name ? String(name.value || "").trim() : "";
    const msgValue = message ? String(message.value || "").trim() : "";

    const subject = `Website: ${topicValue}`;
    const lines = [];
    if (nameValue) lines.push(`Name: ${nameValue}`);
    if (msgValue) {
      if (nameValue) lines.push("");
      lines.push(msgValue);
    }
    const body = lines.join("\n");

    const params = [];
    params.push(`subject=${enc(subject)}`);
    if (body) params.push(`body=${enc(body)}`);

    return `mailto:${email}?${params.join("&")}`;
  };

  send.addEventListener("click", () => {
    window.location.href = build();
  });
})();

