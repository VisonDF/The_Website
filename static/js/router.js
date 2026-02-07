let navToken = 0;

async function navigate(url, { push = true } = {}) {
  const token = ++navToken;

  const res = await fetch(url, {
    headers: { "X-Partial": "1" }
  });

  if (!res.ok) {
    window.location.href = url;
    return;
  }

  const html = await res.text();
  if (token !== navToken) return;

  const doc = new DOMParser().parseFromString(html, "text/html");

  const newMain = doc.querySelector("#page-content");
  const oldMain = document.querySelector("#page-content");

  if (!newMain || !oldMain) {
    window.location.href = url;
    return;
  }

  oldMain.replaceWith(newMain);

  document.title = doc.title;

  if (push) {
    history.pushState(null, "", url);
  }

  if (window.Prism) {
    Prism.highlightAllUnder(newMain);
  }
}

document.addEventListener("click", (e) => {
  const a = e.target.closest("a[href]");
  if (!a) return;

  if (a.origin !== location.origin) return;
  if (a.target === "_blank") return;
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  if (a.hash && a.pathname === location.pathname) return;

  e.preventDefault();
  navigate(a.href);
});

window.addEventListener("popstate", () => {
  navigate(location.href, { push: false });
});


