from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from sys import platform
from pathlib import Path

ERROR_MSG_BASE = (
    "Scrapping only the name and the number of contributions "
    "from Google Maps public profile"
)

class SeleniumWrapper:
        
    def __init__(self, browser):
        # TODO check browser validity
        self.browser = browser[0].upper() + browser[1:]
        
        self.driver = None
        self._set_driver()
        

    def _get_driver_extension(self):
        if platform.startswith("linux"):
            return ""
        elif platform.startswith("win32"):
            return ".exe"
        raise Exception(
            "Mailfogle with selenium is not supported for this OS. "
            'Only "linux" and "windows" are possible\n' + ERROR_MSG_BASE
        )

    def _set_driver(self):
        msg = (
            "Your {browser} profile cannot be loaded. "
            "It may be missing or inaccessible.\n" + ERROR_MSG_BASE
        )

        extension = self._get_driver_extension()

        if self.browser == "Chrome":
            options = ChromeOptions()
            driver_filename = "chromedriver" + extension
        elif self.browser == "Firefox":
            options = FirefoxOptions()
            driver_filename = "geckodriver" + extension

        driver_path = f"./drivers/{driver_filename}"
        if not Path(driver_path).is_file():
            raise Exception(msg.format(browser=self.browser))


        self.driver = getattr(webdriver, self.browser)(
            options=options, executable_path=driver_path
        )
