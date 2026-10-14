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


def test_galeria_de_area_muestra_icono_segun_tipo_de_elemento(
        browser, area_page, elemento_factory, objeto_imagen):
    """Para cada elemento simple de tipo video/audio/texto colgando del área
    se muestra un ícono SVG sobreimpreso en el thumbnail del card."""
    for tipo in ("video", "audio", "texto"):
        elemento_factory(
            padre=area_page,
            thumbnail=objeto_imagen,
            tipo=tipo,
            titulo=f"Elemento de {tipo}",
        )
    elemento_factory(
        padre=area_page,
        thumbnail=objeto_imagen,
        tipo="imagen",
        titulo="Elemento de imagen",
    )
    browser.get_page(area_page.url)
    grid = browser.wait_for(".elementos-grid")
    for tipo in ("video", "audio", "texto"):
        icono = grid.find_element(By.CSS_SELECTOR, f".tipo-icono-{tipo}")
        assert icono.is_displayed(), f"El icono de tipo {tipo} no es visible en la página de área"
        src_name = icono.get_attribute("src").split("/")[-1]
        assert src_name.startswith(f"icon_{tipo}") and src_name.endswith(".svg"), \
            f"El icono de tipo {tipo} tiene el nombre incorrecto: {src_name}"

    # El elemento de tipo imagen NO tiene ícono
    iconos_imagen = grid.find_elements(By.CSS_SELECTOR, ".tipo-icono-imagen")
    assert len(iconos_imagen) == 0
