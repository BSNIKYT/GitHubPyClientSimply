import os
import time
import urllib.request
import shutil
import zipfile
import platform
import selenium
import urllib3
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NotFoundSuitableDriver(Exception):
    """Exception raised when no suitable driver is found."""
    pass


class NotLoginOrPasswordException(Exception):
    """Exception raised when login or password is not provided."""
    pass


class GitHubLoginError(Exception):
    """Exception raised when there's an error during GitHub login."""
    pass


class GitHubDirectoryNotFoundError(Exception):
    """Exception raised when the GitHub directory is not found."""
    pass


win_driver_download_path = 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2F1217046%2Fchromedriver_win32.zip?generation=1698692359126601&alt=media'
lin_driver_download_path = 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1217044%2Fchromedriver_linux64.zip?generation=1698689249131026&alt=media'


class InitLogin:
    """Class to handle the initialization and login process."""

    def __init__(self, login, password):
        """
        Initialize InitLogin class.

        Args:
            login: The username for login.
            password: The password for login.
        """
        self.loginValue = login
        self.password = password
        self.driver = None

    def setup_service(self):
        """Setup the WebDriver service."""
        if platform.system() == 'Windows':
            service = Service(executable_path=os.path.join(os.getcwd(), 'modules', 'chromedriver', 'Windows', 'chromedriver.exe'))
        elif platform.system() == 'Linux':
            service = Service(executable_path=os.path.join(os.getcwd(), 'modules', 'chromedriver', 'Linux', 'chromedriver'))
        else:
            service = None
        return service

    def config(self):
        """Configure the WebDriver options."""
        service = self.setup_service()
        options = webdriver.ChromeOptions()

        self.download_default_directory = os.getcwd()
        options.add_experimental_option("prefs", {"download.default_directory": self.download_default_directory})
        for option in ['--log-level=3']:
            options.add_argument(option)

        try:
            if service is not None:
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        except selenium.common.exceptions.NoSuchDriverException as err:
            raise NotFoundSuitableDriver('Driver is not installed.')

    def login(self):
        """Login to GitHub."""
        if not self.driver:
            self.config()
        self.driver.get('https://github.com/login')
        self.driver.implicitly_wait(50)
        input_text_login = self.driver.find_element(By.ID, 'login_field')
        input_text_login.send_keys(self.loginValue)
        input_text_password = self.driver.find_element(By.ID, 'password')
        input_text_password.send_keys(self.password)
        btn = self.driver.find_element(By.NAME, 'commit')
        time.sleep(1)
        btn.click()
        self.driver.implicitly_wait(5)

        if self.is_login_error_exists():
            raise GitHubLoginError('Password or username is incorrect')

        two_factor_auth = self.is_2Fauth()
        if two_factor_auth:
            self.handle_two_factor_auth()

    def is_login_error_exists(self):
        """Check if there's a login error on the page."""
        try:
            self.driver.find_element(By.XPATH, "//div[@class='js-flash-alert']").text
            return True
        except selenium.common.exceptions.NoSuchElementException:
            return False

    def is_2Fauth(self):
        """Check if two-factor authentication is enabled."""
        try:
            if self.driver.find_element(By.XPATH, '//*[contains(text(), "Two-factor authentication")]'):
                return True
        except:
            pass
        return False

    def handle_two_factor_auth(self):
        """Handle two-factor authentication."""
        # Implement your logic to handle 2FA here
        pass

    def quit(self):
        """Quit the WebDriver."""
        if self.driver:
            self.driver.quit()


if __name__ == '__main__':
    IL = InitLogin('login', 'password')
    IL.login()
