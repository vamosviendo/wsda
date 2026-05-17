from selenium.webdriver.common.by import By


def test_header(browser, site, area_page):
    # En todas las páginas del sitio aparece un título y un menú de navegación
    browser.get_page()
    site_title = browser.wait_for("#site-title")
    assert site_title.is_displayed()
    assert site.site_name.lower() in site_title.text.lower()

    nav = browser.find_element(By.CSS_SELECTOR, "#nav-menu")
    assert nav.is_displayed()

    # El título es un enlace a la raíz
    link = site_title.find_element(By.CSS_SELECTOR, "a")
    href = link.get_attribute("href")
    assert href == browser.base_url + "/"
    assert href.endswith("/")

    # En el menú de navegación hay un link a la página principal
    links = nav.find_elements(By.CSS_SELECTOR, "a")
    link_texts = [x.text.lower() for x in links]
    assert "inicio" in link_texts
    link_inicio = next(x for x in links if "inicio" in x.text.lower())
    link_inicio.click()
    assert browser.current_url == browser.base_url + "/"

    # Dada una página de área, ésta se muestra en el menú de navegación y
    # lleva a la página de área correspondiente
    links = browser.find_elements(By.CSS_SELECTOR, "#nav-menu a")
    link_texts = [x.text.lower() for x in links]
    assert area_page.title.lower() in link_texts
    link_area = next(x for x in links if area_page.title.lower() in x.text.lower())
    link_area.click()
    assert browser.current_url == browser.base_url + area_page.url


def test_aplica_css(browser, site):
    browser.get_page()
    site_title = browser.wait_for("#site-title")
    font_family = browser.get_computed_style(site_title, "fontFamily")
    # Nos aseguramos de que no es el font genérico del sistema (serif/Times)
    # indicando que el CSS efectivamente cargó.
    assert font_family != "Times New Roman"
    assert font_family != "serif"
