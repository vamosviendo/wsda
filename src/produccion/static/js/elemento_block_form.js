/**
 * elemento_block_form.js
 * Admin: en un ElementoBlock, cuando el checkbox "compuesto" está activo
 * se ocultan los campos exclusivos de elemento simple (tipo/contenido_*).
 *
 * Estrategia:
 *  - Delegación de eventos en document (soporta bloques agregados
 *    dinámicamente por el StreamField vía Telepath).
 *  - MutationObserver para aplicar el estado inicial a bloques inyectados.
 *  - Itera TODOS los bloques del formulario (puede haber varios en el área
 *    o en la página de elemento compuesto).
 */
(function () {
    'use strict';

    // Campos que sólo aplican a elemento simple. "compuesto" nunca se oculta.
    const CAMPOS_SIMPLES = [
        "tipo",
        "contenido_url",
        "contenido_multimedia",
        "contenido_texto",
    ];

    function contenedorDe(inputCompuesto) {
        // El form_template marca el wrapper con data-elemento-block,
        // y cada campo con data-contentpath.
        return inputCompuesto.closest("[data-elemento-block]");
    }

    function aplicar(inputCompuesto) {
        const cont = contenedorDe(inputCompuesto);
        if (!cont) return;

        const compuesto = inputCompuesto.checked;
        CAMPOS_SIMPLES.forEach(function (nombre) {
            cont.querySelectorAll(
                '[data-contentpath="' + nombre + '"]'
            ).forEach(function (campo) {
                campo.style.display = compuesto ? "none" : "";
            });
        });
    }

    function aplicarTodos() {
        document
            .querySelectorAll('[data-contentpath="compuesto"] input')
            .forEach(aplicar)
    }

    document.addEventListener("change", function (e) {
        if (e.target.closest('[data-contentpath="compuesto"]')) {
            aplicar(e.target);
        }
    });

    // Bloques agregados dinámicamente al StreamField
    new MutationObserver(function (mutations) {
        for (const m of mutations) {
            for (const nodo of m.addedNodes) {
                if (
                    nodo.nodeType === Node.ELEMENT_NODE &&
                    nodo.querySelector &&
                    nodo.querySelector('[data-contentpath="compuesto"] input')
                ) {
                    aplicarTodos();
                    return;
                }
            }
        }
    }).observe(document.body, { childList: true, subtree: true });

    aplicarTodos(); // estado inical (edición de páginas existentes)
})();
