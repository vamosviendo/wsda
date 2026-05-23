class NavMenuManager {
    constructor(container, navRow1, navRow2) {
        if (!container || !navRow1 || !navRow2) {
            throw new TypeError("container, navRow1 y navRow2 son requeridos")
        }
        this._container = container;
        this._row1 = navRow1;
        this._row2 = navRow2;
        this._split = false;
    }

    isSplit() {
        return this._split;
    }

    splitMenu() {
        console.log("Dividiendo con splitMenu")
        if (this._split) return;

        const items = [...this._row1.children, ...this._row2.children];
        const mid = Math.ceil(items.length / 2);

        items.forEach((item, i) => {
            if (i < mid) {
                this._row1.appendChild(item);
            } else {
                this._row2.appendChild(item);
            }
        });

        this._container.classList.add("nav-split");
        this._split = true;
    }

    unsplitMenu() {
        console.log("Unificando con unsplitMenu");
        if (!this._split) return;

        const items = [...this._row2.children]
        items.forEach((item) => {
            this._row1.appendChild(item);
        });

        this._container.classList.remove("nav-split");
        this._split = false;
    }

    updateMenu() {
        const allItems = [
            ...this._row1.querySelectorAll(":scope > li"),
            ...this._row2.querySelectorAll(":scope > li"),
        ];
        let totalWidth = 0;
        allItems.forEach((item) => {
            totalWidth += item.offsetWidth;
        });

        const gap = parseFloat(getComputedStyle(this._row1).columnGap) || 0;
        totalWidth += gap * Math.max(0, allItems.length - 1);

        const containerWidth = this._container.clientWidth;

        if (totalWidth > containerWidth) {
            this.splitMenu();
        } else {
            this.unsplitMenu();
        }
    }
}

function initNavMenu() {
    console.log("Inicializando con initNavMenu")
    const container = document.querySelector(".nav-container");
    const row1 = document.querySelector(".nav-row-1");
    const row2 = document.querySelector(".nav-row-2");

    if (!container || !row1 || !row2) {
        console.log("Retornando con null")
        return null;
    }

    const manager = new NavMenuManager(container, row1, row2)

    const observer = new ResizeObserver(() => {
        manager.updateMenu();
    });

    const headerInner = document.querySelector(".header-inner");
    if(headerInner) {
        observer.observe(headerInner);
    }

    manager.updateMenu();

    return manager;
}

if (typeof module != "undefined" && module.exports) {
    module.exports = { NavMenuManager, initNavMenu };
} else {
    console.log("Ejecutando script")
    window.navMenuManager = { init: initNavMenu };
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initNavMenu);
    } else {
        initNavMenu();
    }}
