from selenium.webdriver.common.by import By


def test_elemento_compuesto_muestra_galeria_de_sub_elementos(
        browser, elemento_compuesto, elemento, elemento_2, elemento_3):
    # Dado un elemento compuesto con varios sub-elementos
    # incluido en una página de área:

    # Si desde la página de área cliqueamos
    # en el elemento compuesto vamos a la página del elemento compuesto.
    browser.get_page(elemento_compuesto.url)
    titulo = browser.wait_for("#elemento-titulo")
    assert titulo.is_displayed()
    assert titulo.text == "Elemento compuesto"

    # Muestra galería con thumbnails de sub-elementos
    grid = browser.wait_for("#elementos-grid")
    imgs = grid.find_elements(By.TAG_NAME, "img")
    assert len(imgs) == 3

    links = grid.find_elements(By.TAG_NAME, "a")
    elementos_esperados = [elemento, elemento_2, elemento_3]
    for index, img in enumerate(imgs):
        src = img.get_attribute("src")
        assert browser.get_img_natural_width(img) > 0, f"La imagen {src} no se cargó"
        assert img.is_displayed(), f"La imagen {src} no es visible"
        assert "/media/" in src
        link = links[index]
        assert elementos_esperados[index].url in link.get_attribute("href")


def test_desde_elemento_compuesto_se_navega_a_sub_elemento(
        browser, elemento_compuesto, elemento):
    browser.get_page(elemento_compuesto.url)
    grid = browser.wait_for("#elementos-grid")
    grid.find_elements(By.TAG_NAME, "a")[0].click()
    assert "error" not in browser.title.lower()
    assert "not found" not in browser.title.lower()
    assert browser.current_url == browser.base_url + elemento.url


def test_navegacion_anterior_siguiente_entre_elementos_de_area(
        browser, area_page, elemento_compuesto, elemento_de_area):
    # Dado un elemento entre otros (hermanos bajo la misma área):
    browser.get_page(elemento_de_area.url)

    # Al final de la página hay un enlace con el título del elemento anterior
    anterior = browser.wait_for("#elemento-anterior")
    assert anterior.text == f"← {elemento_compuesto.titulo}"

    # Si cliqueamos en el enlace elemento_anterior, vamos al elemento anterior
    # del área
    anterior.click()
    browser.wait_for_url(elemento_compuesto.url, timeout=3)

    # También hay un enlace con el nombre del elemento siguiente
    siguiente = browser.wait_for("#elemento-siguiente")
    assert siguiente.text == f"{elemento_de_area.titulo} →"

    # Si cliqueo en el enlace elemento-siguiente, voy al elemento siguiente
    # del área.
    siguiente.click()
    browser.wait_for_url(elemento_de_area.url, timeout=3)

    # Si el elemento es el último del área, no aparece el enlace
    # elemento-siguiente.
    browser.wait_for_not("#elemento-siguiente")

    # Si el elemento es el primero del área, no aparece el enlace
    # elemento-anterior.
    browser.get_page(elemento_compuesto.url)
    browser.wait_for_not("#elemento-anterior")


def test_navegacion_anterior_siguiente_entre_subelementos_de_elemento_compuesto(
        browser, elemento_compuesto, elemento, elemento_2):
    # Dado un elemento entre otros (hermanos bajo el mismo elemento compuesto):
    browser.get_page(elemento_2.url)

    # Al final de la página hay un enlace con el título del elemento anterior
    anterior = browser.wait_for("#elemento-anterior")
    assert anterior.text == f"← {elemento.titulo}"

    # Si cliqueamos en el enlace elemento_anterior, vamos al sub-elemento
    # anterior del elemento compuesto
    anterior.click()
    browser.wait_for_url(elemento.url, timeout=3)

    # También hay un enlace con el nombre del sub-elemento siguiente
    siguiente = browser.wait_for("#elemento-siguiente")
    assert siguiente.text == f"{elemento_2.titulo} →"

    # Si cliqueo en el enlace elemento-siguiente, voy al elemento siguiente
    # del área.
    siguiente.click()
    browser.wait_for_url(elemento_2.url, timeout=3)

    # Si el elemento es el último del área, no aparece el enlace
    # elemento-siguiente.
    browser.wait_for_not("#elemento-siguiente")

    # Si el elemento es el primero del área, no aparece el enlace
    # elemento-anterior.
    browser.get_page(elemento.url)
    browser.wait_for_not("#elemento-anterior")


def test_galeria_de_elemento_compuesto_muestra_icono_segun_tipo_de_elemento(
        browser, elemento_compuesto, elemento_audio, elemento_video,
        elemento_texto, objeto_imagen, elemento_factory):
    """Para cada elemento de tipo video/audio/texto se muestra un ícono SVG
    sobreimpreso en la esquina inferior derecha del thumbnail."""

    # Crear un elemento de tipo imagen (sin ícono)
    elemento_factory(
        padre=elemento_compuesto,
        thumbnail=objeto_imagen,
        tipo="imagen",
        titulo="Elemento de imagen",
    )

    browser.get_page(elemento_compuesto.url)
    grid = browser.wait_for("#elementos-grid")

    # Verificar que cada elemento tiene su ícono según tipo
    for tipo in ("video", "audio", "texto"):
        icono = grid.find_element(By.CSS_SELECTOR, f".tipo-icono-{tipo}")
        assert icono.is_displayed(), f"El ícono de tipo {tipo} no es visible"
        src_name = icono.get_attribute("src").split("/")[-1]
        assert src_name.startswith(f"icon_{tipo}") and src_name.endswith(".svg")

    # El elemento de tipo imagen NO tiene ícono
    iconos_imagen = grid.find_elements(By.CSS_SELECTOR, ".tipo-icono-imagen")
    assert len(iconos_imagen) == 0


def test_elemento_compuesto_anidado_muestra_galeria(
        browser, elemento_compuesto, elemento_factory, objeto_imagen):
    sub_compuesto = elemento_factory(
        padre=elemento_compuesto,
        compuesto=True,
        titulo="Sub compuesto",
    )
    sub_elemento = elemento_factory(
        padre=sub_compuesto,
        thumbnail=objeto_imagen,
        titulo="Elemento anidado",
    )

    # El elemento compuesto raíz muestra al sub-elemento compuesto en su galería
    browser.get_page(elemento_compuesto.url)
    grid = browser.wait_for("#elementos-grid")
    assert sub_compuesto.url in grid.find_element(By.TAG_NAME, "a").get_attribute("href")

    # Y el sub-elemento compuesto muestra su propio sub-elemento.
    browser.get_page(sub_compuesto.url)
    grid2 = browser.wait_for("#elementos-grid")
    assert sub_elemento.url in grid2.find_element(By.TAG_NAME, "a").get_attribute("href")
