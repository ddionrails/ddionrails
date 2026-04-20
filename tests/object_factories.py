from contextlib import contextmanager
from typing import Generator

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

SELENIUM_URL = "http://selenium-firefox:4444"


@contextmanager
def selenium_browser() -> Generator[WebDriver, None, None]:
    """Provide a selenium remote webdriver."""
    options = Options()
    options.add_argument("-headless")
    options.add_argument("browser.download.folderList=2")
    options.add_argument("browser.download.manager.showWhenStarting=False")

    _browser = WebDriver(SELENIUM_URL, options=options)

    yield _browser
    _browser.quit()
