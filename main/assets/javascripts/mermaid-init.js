/**
 * Mermaid initialisatie en klik-om-te-vergroten.
 *
 * fence_div_format levert <div class="mermaid">...</div>, wat mermaid.js
 * oppikt via mermaid.run(). Na rendering voegt dit script een
 * klik-overlay toe aan elk diagram.
 */
(function () {
  function waitForMermaid(callback) {
    if (typeof mermaid !== "undefined") {
      callback();
    } else {
      setTimeout(function () { waitForMermaid(callback); }, 100);
    }
  }

  function openOverlay(svg) {
    var overlay = document.createElement("div");
    overlay.className = "mermaid-overlay";

    var clone = svg.cloneNode(true);
    clone.removeAttribute("style");
    clone.removeAttribute("width");
    clone.removeAttribute("height");
    overlay.appendChild(clone);

    overlay.addEventListener("click", function () {
      overlay.remove();
    });

    document.addEventListener("keydown", function handler(e) {
      if (e.key === "Escape") {
        overlay.remove();
        document.removeEventListener("keydown", handler);
      }
    });

    document.body.appendChild(overlay);
  }

  function bindZoom() {
    // Gebruik event delegation op document: vangt klikken op ongeacht
    // welk SVG-kindelement (rect, text, path) de klik ontvangt.
    document.addEventListener("click", function (e) {
      var mermaidDiv = e.target.closest("div.mermaid");
      if (!mermaidDiv) return;

      // Niet openen als we al in de overlay zitten
      if (e.target.closest(".mermaid-overlay")) return;

      var svg = mermaidDiv.querySelector("svg");
      if (svg) {
        e.preventDefault();
        openOverlay(svg);
      }
    });

    // Cursor aanpassen zodra SVG's verschijnen
    var observer = new MutationObserver(function () {
      document.querySelectorAll("div.mermaid:not(.mermaid-overlay div)").forEach(function (div) {
        if (div.dataset.zoomStyled) return;
        div.dataset.zoomStyled = "true";
        div.style.cursor = "pointer";
        div.setAttribute("title", "Klik om te vergroten");
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  waitForMermaid(function () {
    mermaid.initialize({ startOnLoad: false, theme: "default" });
    bindZoom();
    mermaid.run();
  });
})();
