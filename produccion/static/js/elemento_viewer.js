/**
 * elemento_viewer.js
 * Visor de imagen para ElementoPage.
 *
 * Estados del overlay:
 *   0 — cerrado
 *   1 — pantalla completa (imagen ajustada al viewport)
 *   2 — tamaño real (imagen a resolución nativa, con scroll)
 *
 * Uso desde el template:
 *   <script src="{% static 'js/elemento_viewer.js' %}"></script>
 *   <script>elementoViewer.init();</script>
 *
 * La función init() se exporta para permitir tests con Jest/jsdom.
 * En el browser, el módulo queda disponible como window.elementoViewer.
 */

(function (global) {

    function init() {
        const preview = document.querySelector(".elemento-img-preview");
        if (!preview) return;

        // Crear overlay
        const overlay = document.createElement("div");
        overlay.className = "elemento-img-overlay";

        const overlayImg = document.createElement("img");
        overlay.appendChild(overlayImg);

        const closeBtn = document.createElement("button");
        closeBtn.className = "elemento-img-close";
        closeBtn.innerHTML = "&#x2715;";
        closeBtn.addEventListener("click", close);
        overlay.appendChild(closeBtn);

        document.body.appendChild(overlay);

        let stage = 0;  // 0=cerrado, 1=pantalla completa, 2=tamaño real

        function open(s) {
            stage = s;
            overlayImg.src = preview.dataset.full;

            if (s === 1) {
                overlayImg.style.maxWidth  = "100vw";
                overlayImg.style.maxHeight = "100vh";
                overlayImg.style.width     = "auto";
                overlayImg.style.height    = "auto";
                overlay.style.overflow        = "hidden";
                overlay.style.alignItems      = "center";
                overlay.style.justifyContent  = "center";
            } else {
                overlayImg.style.maxWidth  = "none";
                overlayImg.style.maxHeight = "none";
                overlayImg.style.width     = preview.dataset.width  + "px";
                overlayImg.style.height    = preview.dataset.height + "px";
                overlay.style.overflow       = "auto";
                overlay.style.alignItems     = "flex-start";
                overlay.style.justifyContent = "flex-start";
            }

            overlay.classList.add("activo");
        }

        function close() {
            stage = 0;
            overlay.classList.remove("activo");
        }

        preview.addEventListener("click", () => open(1));

        overlay.addEventListener("click", (e) => {
            if (e.target === closeBtn) return;
            if (stage === 1) {
                overlayImg.style.cursor = "zoom-out";
                open(2);
            } else {
                overlayImg.style.cursor = "zoom-in";
                open(1);
            }
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") close();
        });

        // Exponer estado interno para tests
        return { getStage: () => stage, overlay, overlayImg, closeBtn, preview };
    }

    // Compatibilidad: exporta como módulo CommonJS (Jest) o como global (browser)
    if (typeof module !== "undefined" && module.exports) {
        module.exports = { init };
    } else {
        global.elementoViewer = { init };
    }

}(typeof window !== "undefined" ? window : global));