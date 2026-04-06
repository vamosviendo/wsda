const { NavMenuManager, initNavMenu } = require("../wlili/static/js/wlili");

// ============================================================
// Helpers
// ============================================================

function crearNavContainer(items = ["Inicio", "Página 1", "Página 2", "Blog"]) {
    const container = document.createElement("div");
    container.className = "nav-container";

    const nav = document.createElement("nav");
    const ul1 = document.createElement("ul");
    ul1.className = "nav-row nav-row-1";

    items.forEach((text) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = "#";
        a.textContent = text;
        li.appendChild(a);
        ul1.appendChild(li);
    });

    const ul2 = document.createElement("ul");
    ul2.className = "nav-row nav-row-2";

    nav.appendChild(ul1);
    nav.appendChild(ul2);
    container.appendChild(nav);
    document.body.appendChild(container);

    return { container, nav, ul1, ul2 };
}

function crearHeaderInner() {
    const div = document.createElement("div");
    div.className = "header-inner";
    document.body.appendChild(div);
    return div;
}

let resizeCallback;
let lastObserver;

beforeAll(() => {
    global.ResizeObserver = jest.fn().mockImplementation((cb) => {
        resizeCallback = cb;
        lastObserver = {
            observe: jest.fn(),
            unobserve: jest.fn(),
            disconnect: jest.fn(),
        };
        return lastObserver;
    });
});

// ============================================================
// Limpieza entre tests
// ============================================================
afterEach(() => {
    document.body.innerHTML = "";
    jest.restoreAllMocks();
    resizeCallback = null;
    lastObserver = null;
});

// ============================================================
// 1. Constructor / inicialización
// ============================================================

describe("NavMenuManager", () => {
    describe("constructor()", () => {
        test("lanza TypeError si container es null", () => {
            expect(() => new NavMenuManager(null)).toThrow(TypeError);
        });

        test("lanza TypeError si navRow1 es null", () => {
            const { container, ul2 } = crearNavContainer();
            expect(() => new NavMenuManager(container, null, ul2)).toThrow(TypeError);
        });

        test("lanza TypeError si navRow2 es null", () => {
            const { container, ul1 } = crearNavContainer();
            expect(() => new NavMenuManager(container, ul1, null)).toThrow(TypeError);
        });

        test("almacena las referencias correctamente", () => {
            const { container, ul1, ul2 } = crearNavContainer();
            const manager = new NavMenuManager(container, ul1, ul2);
            expect(manager._container).toBe(container);
            expect(manager._row1).toBe(ul1);
            expect(manager._row2).toBe(ul2);
        });

        test("estado inicial: no está dividido", () => {
            const { container, ul1, ul2 } = crearNavContainer();
            const manager = new NavMenuManager(container, ul1, ul2);
            expect(manager.isSplit()).toBe(false);
        });
    });

    // ============================================================
    // 2. splitMenu()
    // ============================================================

    describe("splitMenu()", () => {
        test("distribuye los items equitativamente entre las dos filas", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B", "C", "D"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();

            expect(ul1.children.length).toBe(2);
            expect(ul2.children.length).toBe(2);
        });

        test("con cantidad impar, la primera fila tiene uno más", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B", "C"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();

            expect(ul1.children.length).toBe(2);
            expect(ul2.children.length).toBe(1);
        });

        test("con un solo item, queda en la primera fila", () => {
            const { container, ul1, ul2 } = crearNavContainer(["Solo"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();

            expect(ul1.children.length).toBe(1);
            expect(ul2.children.length).toBe(0);
        });

        test("con cero items, ambas filas vacías", () => {
            const { container, ul1, ul2 } = crearNavContainer([]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();

            expect(ul1.children.length).toBe(0);
            expect(ul2.children.length).toBe(0);
        });

        test("preserva el contenido de cada item", () => {
            const { container, ul1, ul2 } = crearNavContainer(["Inicio", "Contacto", "Blog"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();

            const textos = [
                ...ul1.querySelectorAll("a"),
                ...ul2.querySelectorAll("a"),
            ].map((a) => a.textContent);

            expect(textos).toEqual(["Inicio", "Contacto", "Blog"]);
        });

        test("agrega la clase 'nav-split' al container", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();

            expect(container.classList.contains("nav-split")).toBe(true);
        });

        test("cambia el estado a dividido", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();

            expect(manager.isSplit()).toBe(true);
        });

        test("es idempotente: no duplica items si se llama dos veces", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B", "C", "D"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();
            manager.splitMenu();

            expect(ul1.children.length).toBe(2);
            expect(ul2.children.length).toBe(2);
        });
    });

    // ============================================================
    // 3. unsplitMenu()
    // ============================================================

    describe("unsplitMenu()", () => {
        test("mueve todos los items a la primera fila", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B", "C", "D"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();
            manager.unsplitMenu();

            expect(ul1.children.length).toBe(4);
            expect(ul2.children.length).toBe(0);
        });

        test("remueve la clase 'nav-split' del container", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();
            manager.unsplitMenu();

            expect(container.classList.contains("nav-split")).toBe(false);
        });

        test("cambia el estado a no dividido", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();
            manager.unsplitMenu();

            expect(manager.isSplit()).toBe(false);
        });

        test("preserva el orden original de los items", () => {
            const { container, ul1, ul2 } = crearNavContainer(["Inicio", "Productos", "Contacto", "Blog"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.splitMenu();
            manager.unsplitMenu();

            const textos = [...ul1.querySelectorAll("a")].map((a) => a.textContent);
            expect(textos).toEqual(["Inicio", "Productos", "Contacto", "Blog"]);
        });

        test("es idempotente: no falla si ya está unificado", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            manager.unsplitMenu();
            manager.unsplitMenu();

            expect(ul1.children.length).toBe(2);
            expect(ul2.children.length).toBe(0);
        });
    });

    // ============================================================
    // 4. updateMenu()
    // ============================================================
    function mockMenuDimensions(items, container, itemWidths, containerWidth) {
        items.forEach((item, i) => {
            jest.spyOn(item, "offsetWidth", "get").mockReturnValue(itemWidths[i]);
        });
        jest.spyOn(window, "getComputedStyle").mockReturnValue({ columnGap: "8px" });
        jest.spyOn(container, "clientWidth", "get").mockReturnValue(containerWidth);
    }

    describe("updateMenu()", () => {
        test("no divide si el contenido cabe en el contenedor", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            const items = [...ul1.querySelectorAll(":scope > li")];
            mockMenuDimensions(items, container, [80, 80], 400);

            manager.updateMenu();

            expect(manager.isSplit()).toBe(false);
            expect(ul2.children.length).toBe(0);
        });

        test("divide si el contenido excede el ancho del contenedor", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B", "C", "D"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            const items = [...ul1.querySelectorAll(":scope > li")];
            mockMenuDimensions(items, container, [150, 150, 150, 150], 400);

            manager.updateMenu();

            expect(manager.isSplit()).toBe(true);
            expect(ul1.children.length).toBe(2);
            expect(ul2.children.length).toBe(2);
        });

        test("unifica si ya estaba dividido y ahora cabe", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B", "C", "D"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            const items = [...ul1.querySelectorAll(":scope > li")];

            mockMenuDimensions(items, container, [150, 150, 150, 150], 400);
            manager.updateMenu();
            expect(manager.isSplit()).toBe(true);

            mockMenuDimensions(items, container, [80, 80, 80, 80], 400);
            manager.updateMenu();

            expect(manager.isSplit()).toBe(false);
            expect(ul1.children.length).toBe(4);
            expect(ul2.children.length).toBe(0);
        });

        test("no hace nada si ya está dividido y sigue sin caber", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B", "C", "D"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            const items = [...ul1.querySelectorAll(":scope > li")];

            mockMenuDimensions(items, container, [150, 150, 150, 150], 400);
            manager.updateMenu();

            const itemsRow1 = ul1.children.length;
            const itemsRow2 = ul2.children.length;

            manager.updateMenu();

            expect(ul1.children.length).toBe(itemsRow1);
            expect(ul2.children.length).toBe(itemsRow2);
        });

        test("no hace nada si ya está unificado y sigue cabiendo", () => {
            const { container, ul1, ul2 } = crearNavContainer(["A", "B"]);
            const manager = new NavMenuManager(container, ul1, ul2);
            const items = [...ul1.querySelectorAll(":scope > li")];

            mockMenuDimensions(items, container, [80, 80], 400);
            manager.updateMenu();
            manager.updateMenu();

            expect(manager.isSplit()).toBe(false);
            expect(ul1.children.length).toBe(2);
            expect(ul2.children.length).toBe(0);
        });
    });

    // ============================================================
    // 5. initNavMenu() — función de fábrica
    // ============================================================

    describe("initNavMenu()", () => {
        test("devuelve null si no existe .nav-container", () => {
            crearHeaderInner();
            const result = initNavMenu();
            expect(result).toBeNull();
        });

        test("devuelve null si no existe .nav-row-1", () => {
            const container = document.createElement("div");
            container.className = "nav-container";
            const nav = document.createElement("nav");
            const ul2 = document.createElement("ul");
            ul2.className = "nav-row nav-row-2";
            nav.appendChild(ul2);
            container.appendChild(nav);
            document.body.appendChild(container);

            const result = initNavMenu();
            expect(result).toBeNull();
        });

        test("devuelve null si no existe .nav-row-2", () => {
            const container = document.createElement("div");
            const nav = document.createElement("nav");
            const ul1 = document.createElement("ul");
            ul1.className = "nav-row nav-row-1";
            nav.appendChild(ul1);
            container.appendChild(nav);
            document.body.appendChild(container);

            const result = initNavMenu();
            expect(result).toBeNull();
        });

        test("devuelve una instancia de NavMenuManager cuando todo existe", () => {
            const { container } = crearNavContainer();
            const result = initNavMenu();
            expect(result).toBeInstanceOf(NavMenuManager);
        });

        test("crea un ResizeObserver al inicializar", () => {
            crearNavContainer();
            initNavMenu();
            expect(ResizeObserver).toHaveBeenCalled();
        });

        test("observa cambios de tamaño en .header-inner", () => {
            crearNavContainer();
            const headerInner = crearHeaderInner();

            initNavMenu();

            // const observerInstance = ResizeObserver.mock.results[0].value;
            expect(lastObserver.observe).toHaveBeenCalledWith(headerInner);
        });

        test("llama a updateMenu() cuando ResizeObserver detecta un cambio", () => {
            crearNavContainer();
            const manager = initNavMenu();
            const updateSpy = jest.spyOn(manager, "updateMenu");

            resizeCallback();

            expect(updateSpy).toHaveBeenCalled();
        });

        test("llama a updateMenu() al inicializar", () => {
            const { container, ul1 } = crearNavContainer();
            const updateSpy = jest.spyOn(NavMenuManager.prototype, "updateMenu");

            initNavMenu();

            expect(updateSpy).toHaveBeenCalled();
        });
    });
});
