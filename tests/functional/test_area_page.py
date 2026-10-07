from selenium.webdriver.common.by import By

def test_area_page_muestra_elementos(browser, area_page, elemento_compuesto, elemento_de_area):
    # Dada un área con un elemento compuesto y un elemento simple:
    browser.get_page(area_page.url)

    # La página carga correctamente
    assert "error" not in browser.title.lower()

    # Se muestran correctamente título y descripción
    titulo = browser.wait_for(".area-titulo")
    assert titulo.is_displayed()
    assert "Area Page" in titulo.text

    desc = browser.find_element(By.CSS_SELECTOR, ".area-descripcion")
    assert desc.is_displayed()
    assert "Página de área genérica" in desc.text

    # El área muestra la lista de sus elementos
    elementos = browser.wait_for(".elementos-grid")
    assert elementos.is_displayed()
    display = browser.get_computed_style(elementos, "display")
    assert display == "flex"

    links = elementos.find_elements(By.CSS_SELECTOR, "a")
    hrefs = [link.get_attribute("href") for link in links]
    assert area_page.url in hrefs[0]  # enlaces a ElementoPage
    print("hrefs:", *hrefs, sep="\n")
    assert len(links) == 2
