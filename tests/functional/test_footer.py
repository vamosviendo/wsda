import pytest
from selenium.webdriver.common.by import By

from base.models import NavigationSettings


@pytest.fixture
def navigation_settings():
    NavigationSettings(instagram_url="https://instagram.com/lilianamedela").save()


def get_link_img_src(link):
    return link.find_element(By.CSS_SELECTOR, "img").get_attribute("src")

def test_footer(browser, site, navigation_settings):
    # En todas las páginas del sitio es visible el pie de página
    browser.get_page()
    footer = browser.wait_for("footer")
    assert footer.is_displayed()

    # Se muestra el crédito de diseño
    footer_credit = browser.wait_for("#footer-credit")
    assert footer_credit.text == "Diseño: HT"

    # Se muestran links configurados en NavigationSettings,
    # apuntando a las url correctas
    links = browser.find_elements(By.CSS_SELECTOR, "#footer-social a")
    instagram_src = f"{browser.base_url}/static/images/instagram.svg"
    link_srcs = [get_link_img_src(l) for l in links]
    assert instagram_src in link_srcs

    insta_link = next(
        (l for l in links if get_link_img_src(l) == instagram_src),
        None
    )
    assert insta_link is not None
    assert insta_link.get_attribute("href") == "https://instagram.com/lilianamedela"
