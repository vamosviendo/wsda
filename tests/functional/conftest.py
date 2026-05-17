import pytest
from selenium.webdriver.firefox.options import Options

from tests.functional.base import MiFirefox


@pytest.fixture(scope="session")
def browser(live_server_url):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--width=1280")
    options.add_argument("--height=900")
    driver = MiFirefox(options=options, base_url=live_server_url)
    driver.implicitly_wait(5)
    yield driver
    driver.close()
