function initThemeToggle() {
  const root = document.documentElement;
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;

  btn.textContent = root.dataset.theme === "dark" ? "☀︎" : "⏾";

  btn.addEventListener("click", () => {
    const isDark = root.dataset.theme === "dark";
    root.dataset.theme = isDark ? "light" : "dark";
    localStorage.setItem("theme", root.dataset.theme);
    btn.textContent = isDark ? "⏾" : "☀︎";
  });
}

function startRotator({
  containerSelector,
  itemSelector,
  dotSelector,
  interval = 5000,
  activeClass = "active",
}) {
  const container = containerSelector
    ? document.querySelector(containerSelector)
    : document;

  if (!container) return;

  const items = container.querySelectorAll(itemSelector);
  const dots = document.querySelectorAll(dotSelector);

  if (!items.length || !dots.length) return;

  let index = 0;
  let timer;

  function update() {
    items.forEach((el, i) =>
      el.classList.toggle(activeClass, i === index)
    );
    dots.forEach((el, i) =>
      el.classList.toggle(activeClass, i === index)
    );
  }

  function start() {
    update();
    timer = setInterval(() => {
      index = (index + 1) % items.length;
      update();
    }, interval);
  }

  function stop() {
    clearInterval(timer);
  }

  // pause when tab is hidden (perf win)
  document.addEventListener("visibilitychange", () => {
    document.hidden ? stop() : start();
  });

  start();
}

document.addEventListener("DOMContentLoaded", () => {
  startRotator({
    containerSelector: ".code-rotator",
    itemSelector: ".code-block",
    dotSelector: ".rotator-indicator span",
    interval: 5000,
  });

  startRotator({
    itemSelector: ".rotator-sentence",
    dotSelector: ".hero-rotator-indicator span",
    interval: 5000,
  });

  document.addEventListener("click", async (event) => {
    const btn = event.target.closest(".copy-btn");
    if (!btn) return;
  
    const pre = btn.closest("pre");
    if (!pre) return;
  
    const code = pre.querySelector("code");
    if (!code) return;
  
    const text = code.innerText.trim();
  
    try {
      await navigator.clipboard.writeText(text);
  
      // Visual feedback
      const original = btn.textContent;
      btn.textContent = "✅ Copied";
      btn.disabled = true;
  
      setTimeout(() => {
        btn.textContent = original;
        btn.disabled = false;
      }, 1500);
    } catch (err) {
      console.error("Copy failed", err);
      btn.textContent = "❌ Error";
    }
  });

  initThemeToggle();

});





