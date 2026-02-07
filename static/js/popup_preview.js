(() => {
  const cache = new Map()
  let popup, hideTimer

  function ensurePopup() {
    if (popup) return
    popup = document.createElement("div")
    popup.className = "link-preview-popup"
    popup.style.display = "none"
    document.body.appendChild(popup)

    popup.addEventListener("mouseenter", () => clearTimeout(hideTimer))
    popup.addEventListener("mouseleave", scheduleHide)
  }

  function scheduleHide() {
    hideTimer = setTimeout(() => {
      if (popup) popup.style.display = "none"
    }, 120)
  }

  async function loadPage(url) {
    if (cache.has(url)) return cache.get(url)

    const res = await fetch(url, { credentials: "same-origin" })
    const html = await res.text()
    const doc = new DOMParser().parseFromString(html, "text/html")

    const content = doc.querySelector("#page-content")
    if (!content) throw new Error("No #page-content")

    // Strip dangerous / heavy nodes
    content.querySelectorAll("script, iframe, video").forEach(e => e.remove())

    // Fix relative URLs
    content.querySelectorAll("img, a").forEach(el => {
      const attr = el.tagName === "IMG" ? "src" : "href"
      const val = el.getAttribute(attr)
      if (val && !val.startsWith("http") && !val.startsWith("#")) {
        el.setAttribute(attr, new URL(val, url).href)
      }
    })

    cache.set(url, content)
    return content
  }

  function positionPopup(e) {
    const margin = 20
    let x = e.clientX + margin
    let y = e.clientY + margin

    popup.style.left = x + "px"
    popup.style.top = y + "px"

    requestAnimationFrame(() => {
      const r = popup.getBoundingClientRect()
      if (r.right > innerWidth)
        popup.style.left = innerWidth - r.width - margin + "px"
      if (r.bottom > innerHeight)
        popup.style.top = innerHeight - r.height - margin + "px"
    })
  }

  async function show(e) {
    const link = e.currentTarget
    const url = link.href
    if (new URL(url).origin !== location.origin) return

    ensurePopup()
    clearTimeout(hideTimer)

    popup.innerHTML = "<em>Loading…</em>"
    popup.style.display = "block"
    positionPopup(e)

    try {
      const content = await loadPage(url)
      popup.innerHTML = ""
      popup.appendChild(content.cloneNode(true))

      // Optional: syntax highlight preview
      if (window.Prism) Prism.highlightAllUnder(popup)
    } catch {
      popup.innerHTML = "<em>Preview unavailable</em>"
    }
  }

  function attach() {
    document.querySelectorAll("a[href^='/']").forEach(a => {
      if (a.dataset.preview) return
      a.dataset.preview = "1"
      a.addEventListener("mouseenter", show)
      a.addEventListener("mousemove", positionPopup)
      a.addEventListener("mouseleave", scheduleHide)
    })
  }

  attach()
})()


