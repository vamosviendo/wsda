from typing import Iterable

from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .helpers import esperar_condicion


class MiFirefox(webdriver.Firefox):
    def __init__(self, base_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url

    def get_page(self, page="/"):
        return self.get(f"{self.base_url}{page}")

    def get_computed_style(self, element, prop):
        """Devuelve el valor de una propiedad CSS computada (interpretada por el browser)."""
        return self.execute_script(
            f"return window.getComputedStyle(arguments[0]).{prop}", element
        )

    def get_img_natural_width(self, img):
        return self.execute_script(
            "return arguments[0].naturalWidth", img
        )

    def screenshot(self, nombre="debug"):
        path = f"./tmp/selenium_{nombre}.png"
        self.save_screenshot(path)
        print(f"Screenshot guardado: {path}")

    def wait_for(
            self,
            selector: str,
            criterio: str = By.CSS_SELECTOR,
            timeout: float = 5
    ) -> WebElement:
        return esperar_condicion(
            self.find_element, timeout, criterio, selector
        )

    def wait_fors(
            self,
            selector: str,
            criterio: str = By.CSS_SELECTOR,
            fail=True,
            timeout: float = 5) -> Iterable[WebElement]:
        def busqueda():
            elementos = self.find_elements(criterio, selector)
            if fail:
                assert len(elementos) != 0, \
                    f'no se encontraron elementos coincidentes con "{selector}"'
            return elementos

        return esperar_condicion(busqueda, timeout)

    def wait_for_not(self, selector, criterio=By.CSS_SELECTOR, timeout=5):
        def not_present():
            try:
                self.find_element(criterio, selector)
                raise AssertionError(
                    f"Elemento {selector} se encuentra presente en la página"
                )
            except (NoSuchElementException, StaleElementReferenceException):
                pass

        return esperar_condicion(not_present, timeout)

    def wait_for_url(self, path, timeout=5):
        def current_url():
            assert self.current_url == f"{self.base_url}{path}"

        return esperar_condicion(current_url, timeout)
