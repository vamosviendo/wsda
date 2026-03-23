const { init } = require("../produccion/static/js/elemento_viewer");

// ============================================================
// Helpers
// ============================================================

/**
 * Construye el DOM mínimo que el visor necesita:
 * una imagen preview con los data-attributes que el template genera.
 */
function crearPreview({
    full = "/media/images/obra.jpg",
    width = "1200",
    height = "900",
} = {}) {
    const img = document.createElement("img");
    img.className = "elemento-img-preview";
    img.dataset.full = full;
    img.dataset.width = width;
    img.dataset.height = height;
    document.body.appendChild(img);
    return img;
}

function dispararClic(elemento) {
    elemento.dispatchEvent(new MouseEvent("click", { bubbles: true }));
}

function dispararTecla(key) {
    document.dispatchEvent(new KeyboardEvent("keydown", {key, bubbles: true }));
}

// ============================================================
// Limpieza entre tests
// ============================================================

afterEach(() => {
    // Resetear el DOM completo entre tests para que no haya interferencia.
    document.body.innerHTML = "";
});

// ============================================================
// 1. Inicialización
// ============================================================
describe("init()", () => {
    test("devuelve null si no hay imagen preview en el DOM", () => {
        // Sin .elemento-img-preview en el body
        const resultado = init();
        expect(resultado).toBeUndefined();
    });

    test("crea el overlay y lo agrega al body", () => {
        crearPreview();
        init();
        const overlay = document.querySelector(".elemento-img-overlay");
        expect(overlay).not.toBeNull();
    });

    test("crea un img dentro del overlay", () => {
        crearPreview();
        init();
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg).not.toBeNull();
    });

    test("crea el botón de cierre dentro del overaly", () => {
        crearPreview();
        init();
        const closeBtn = document.querySelector(".elemento-img-close");
        expect(closeBtn).not.toBeNull();
    });

    test("el overlay empieza sin la clae 'activo'", () => {
        crearPreview();
        init();
        const overlay = document.querySelector(".elemento-img-overlay");
        expect(overlay.classList.contains("activo")).toBe(false);
    });

    test("el stage inicial es 0 (cerrado)", () => {
        crearPreview();
        const viewer = init();
        expect(viewer.getStage()).toBe(0);
    });
});


// ============================================================
// 2. Apertura del overlay — clic en preview
// ============================================================
describe("clic en imagen preview", () => {
    test("agrega la clase 'activo' al overlay", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        expect(overlay.classList.contains("activo")).toBe(true);
    });

    test("el stage pasa a 1 (pantalla completa)", () => {
        const preview = crearPreview();
        const viewer = init();
        dispararClic(preview);
        expect(viewer.getStage()).toBe(1);
    });

    test("la imagen del overlay carga la URL de la imagen completa", () => {
        const preview = crearPreview({ full: "/media/images/obra-full.jpg" });
        init();
        dispararClic(preview);
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.src).toContain("obra-full.jpg");
    });

    test("en estado 1 la imagen tiene max-width: 100vw", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.style.maxWidth).toBe("100vw");
    });

    test("en estado 1 la imagen tiene max-height: 100vh", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.style.maxHeight).toBe("100vh");
    });

    test("en estado 1 el overflow del overlay es hidden", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        expect(overlay.style.overflow).toBe("hidden");
    });
});

// ============================================================
// 3. Clic en overlay — transición entre estados 1 y 2
// ============================================================
describe("clic en overlay", () => {
    test("pasa de estado 1 a 2 (tamaño real)", () => {
        const preview = crearPreview();
        const viewer = init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);
        expect(viewer.getStage()).toBe(2);
    });

    test("en estado 2, la imagen tiene max-width y max-height: none", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.style.maxWidth).toBe("none");
        expect(overlayImg.style.maxHeight).toBe("none");
    });

    test("en estado 2, la imagen tiene el ancho y alto del data-attribute en px", () => {
        const preview = crearPreview({ width: "1200", height: "900"});
        init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.style.width).toBe("1200px");
        expect(overlayImg.style.height).toBe("900px");
    });

    test("en estado 2, el overflow del overlay es auto (para scroll)", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);
        expect(overlay.style.overflow).toBe("auto");
    });

    test("clic en estado 2 vuelve a estado 1", () => {
        const preview = crearPreview();
        const viewer = init();
        dispararClic(preview);                          // -> estado 1
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);                          // -> estado 2
        dispararClic(overlay);                          // -> estado 1
        expect(viewer.getStage()).toBe(1);
    });

    test("desde estado 2, la imagen vuelve a tener max-width: 100vw", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);                          // -> estado 1
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);                          // -> estado 2
        dispararClic(overlay);                          // -> estado 1
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.style.maxWidth).toBe("100vw");
    });
});

// ============================================================
// 4. Cierre del overlay
// ============================================================
describe("cierre del overlay", () => {
    test("clic en botón X remueve la clase 'activo'", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        const closeBtn = document.querySelector(".elemento-img-close");
        dispararClic(closeBtn);
        const overlay = document.querySelector(".elemento-img-overlay");
        expect(overlay.classList.contains("activo")).toBe(false);
    });

    test("un clic en el botón de cierre NO propaga al overlay y pone el estado en 0", () => {
        const preview = crearPreview();
        const viewer = init();
        dispararClic(preview);                          // -> estado 1
        const closeBtn = document.querySelector(".elemento-img-close");
        dispararClic(closeBtn);                         // debe cerrar, no cambiar estado
        expect(viewer.getStage()).toBe(0);    // el stage debe ser 0, no 2
    });

    test("tecla Escape remueve la clase 'activo'", () => {
        const preview = crearPreview();
        init();
        dispararClic(preview);
        dispararTecla("Escape");
        const overlay = document.querySelector(".elemento-img-overlay");
        expect(overlay.classList.contains("activo")).toBe(false);
    });

    test("tecla Escape pone el estado en 0'", () => {
        const preview = crearPreview();
        const viewer = init();
        dispararClic(preview);
        dispararTecla("Escape");
        expect(viewer.getStage()).toBe(0);
    });

    test("otras teclas no cierran el overlay", () => {
        const preview = crearPreview();
        const viewer = init();
        dispararClic(preview);
        dispararTecla("Enter");
        dispararTecla("Space");
        dispararTecla("ArrowLeft");
        expect(viewer.getStage()).toBe(1);
    });

    test("se puede volver a abrir el overlay después de cerrarlo", () => {
        const preview = crearPreview();
        const viewer = init();
        dispararClic(preview);              // abrir
        dispararTecla("Escape");       // cerrar
        dispararClic(preview);              // abrir de nuevo
        expect(viewer.getStage()).toBe(1);
        const overlay = document.querySelector(".elemento-img-overlay");
        expect(overlay.classList.contains("activo")).toBe(true);
    });
});


// ============================================================
// 5. Comportamiento con distintas dimensiones de imagen
// ============================================================

describe("dimensiones de imagen", () => {

    test("imagen apaisada: ancho y alto se aplican correctamente", () => {
        const preview = crearPreview({ width: "2400", height: "1600" });
        init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);          // → estado 2 (tamaño real)
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.style.width).toBe("2400px");
        expect(overlayImg.style.height).toBe("1600px");
    });

    test("imagen cuadrada: ancho y alto son iguales", () => {
        const preview = crearPreview({ width: "800", height: "800" });
        init();
        dispararClic(preview);
        const overlay = document.querySelector(".elemento-img-overlay");
        dispararClic(overlay);
        const overlayImg = document.querySelector(".elemento-img-overlay img");
        expect(overlayImg.style.width).toBe("800px");
        expect(overlayImg.style.height).toBe("800px");
    });
});
