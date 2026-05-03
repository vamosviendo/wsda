import pytest
from selenium.webdriver.common.by import By

from produccion.models import ElementoPage, ProductoPage


@pytest.fixture
def area_page_con_productos(area_page, producto_page, objeto_imagen):
    area_page.productos = [("producto", {
        "nombre": producto_page.titulo,
        "descripcion": producto_page.descripcion,
        "imagen": objeto_imagen,
        "link": {"link_to": "page", "page": producto_page},
    })]
    area_page.save_revision().publish()
    return area_page


def test_producto_page(
        browser, area_page_con_productos, producto_page, elemento,
        test_page, objeto_imagen):
    # Dada una página de producto con varios elementos
    # incluida en una página de área:
    for index in ["2", "3"]:
        test_page(
            parent=producto_page,
            page_type=ElementoPage,
            title=f"ElementoPage {index}",
            slug=f"elemento_page_{index}",
            imagen=objeto_imagen,
        )

    # Si desde la página de área cliqueamos
    # en el producto vamos a la página del producto.
    browser.get_page(area_page_con_productos.url)
    links_producto = browser.wait_fors(".producto a")
    links_producto[0].click()
    assert "error" not in browser.title.lower()
    assert "not found" not in browser.title.lower()
    assert browser.current_url == browser.base_url + producto_page.url

    # La página de producto muestra título, descripción si la hay,
    # galería de imágenes
    titulo = browser.wait_for("#producto-titulo")
    assert titulo.is_displayed()
    assert titulo.text == "Producto Page"

    descripcion = browser.wait_for("#descripcion")
    assert descripcion.is_displayed()
    assert descripcion.text == "Página de producto genérica"

    # La galería de imágenes incluye imágenes de todos los elementos
    # del producto en la página
    grid = browser.wait_for("#elementos-grid")
    imgs = grid.find_elements(By.TAG_NAME, "img")
    assert len(imgs) == 3

    links = grid.find_elements(By.TAG_NAME, "a")
    elementos = ElementoPage.objects.all()

    for index, img in enumerate(imgs):
        src = img.get_attribute("src")
        # Las imágenes incluidas son cargadas realmente por el navegador-
        assert \
            browser.get_img_natural_width(img) > 0, \
            f"La imagen {src} no se cargó en el browser"

        # Las imágenes son visibles.
        assert \
            img.is_displayed(), \
            f"La imagen {src} está en el DOM pero no es visible"

        # El atributo src de las imágenes apunta a /media/
        assert \
            "/media/" in src, \
            f"El atributo src de la imagen {src} no apunta a /media/"

        # Las imágenes enlazan a una página de elemento
        assert len(imgs) == len(links)
        link = links[index]
        assert elementos[index].url in link.get_attribute("href")

def test_producto_anterior_siguiente(browser, area_page, producto_page, test_page):
    # Dado un producto entre otros:
    producto_page_2 = test_page(
        parent=area_page,
        page_type=ProductoPage,
        title="ProductoPage2",
        titulo="Producto Page 2",
        descripcion="Página de segundo producto genérica",
    )
    browser.get_page(producto_page_2.url)

    # Al final de la página hay un enlace con el título del producto anterior
    producto_anterior = browser.wait_for("#producto-anterior")
    assert producto_anterior.text == f"← {producto_page.titulo}"

    # Si cliqueamos en el enlace producto_anterior, vamos al producto anterior
    # del área
    producto_anterior.click()
    browser.wait_for_url(producto_page.url, timeout=3)

    # También hay un enlace con el nombre del producto siguiente
    producto_siguiente = browser.wait_for("#producto-siguiente")
    assert producto_siguiente.text == f"{producto_page_2.titulo} →"

    # Si cliqueo en el enlace producto-siguiente, voy al producto siguiente
    # del área.
    producto_siguiente.click()
    browser.wait_for_url(producto_page_2.url, timeout=3)

    # Si el producto es el último del área, no aparece el enlace
    # producto-siguiente.
    browser.wait_for_not("#producto-siguiente")

    # Si el producto es el primero del área, no aparece el enlace
    # producto-anterior.
    browser.get_page(producto_page.url)
    browser.wait_for_not("#producto-anterior")

