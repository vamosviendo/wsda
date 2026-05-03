from selenium.webdriver.common.by import By

def test_area_page(browser, area_page):
    browser.get_page(area_page.url)

    # La página carga correctamente
    assert "error" not in browser.title.lower()

    # Se muestran correctamente título, descripción y grilla de productos
    titulo = browser.wait_for(".area-titulo")
    assert titulo.is_displayed()
    assert "Area Page" in titulo.text

    desc = browser.find_element(By.CSS_SELECTOR, ".area-descripcion")
    assert desc.is_displayed()
    assert "Página de área genérica" in desc.text

    productos = browser.find_elements(By.CSS_SELECTOR, ".productos-grid")
    assert len(productos) > 0, "No se encontró el contenedor .productos-grid en el DOM"

    # El css de la página se aplica correctamente
    grid = productos[0]
    display = browser.get_computed_style(grid, "display")
    assert display == "flex"
