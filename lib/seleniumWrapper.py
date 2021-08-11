from sys import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class Selenium:

	def __init__(self,browser):
		self.browser = browser
		self.driver = None
		DRIVER_PATH = ""

		# Detect OS
		if platform.startswith('linux'):	EXT = ""
		elif platform.startswith('win32'):	EXT = ".exe"
		else: raise Exception("The use of selenium is not supported for this OS. Only \"linux\" and \"win32\" are possible")

		# Choose the good driver
		if (self.browser == "chrome"):
			options = ChromeOptions()
			DRIVER_PATH = f"./drivers/chromedriver{EXT}"
			self.driver = webdriver.Chrome(options=options,executable_path=DRIVER_PATH)

		elif (self.browser == "firefox"):
			options = FirefoxOptions()
			DRIVER_PATH = f"./drivers/geckodriver{EXT}"
			self.driver = webdriver.Firefox(options=options,executable_path=DRIVER_PATH)