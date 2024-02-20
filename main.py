
import os
import time
import json
import urllib
import shutil
import zipfile
import platform
import selenium
import urllib3
import threading
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cryptography.fernet import Fernet


class NotFoundSuitableDriver(Exception):
    """Exception raised when no suitable driver is found."""
    pass


class NotLoginOrPasswordException(Exception):
    """Exception raised when login or password is not provided."""
    pass


class GitHubLoginError(Exception):
    """Exception raised when there's an error during GitHub login."""
    pass


class GitHubDirrectoryNotfoundError(Exception):
    """Exception raised when the GitHub directory is not found."""
    pass


git_link = 'https://github.com/BSNIKYT/SvodkaDZ/'

win_driver_download_path = 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2F1217046%2Fchromedriver_win32.zip?generation=1698692359126601&alt=media'
lin_driver_download_path = 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1217044%2Fchromedriver_linux64.zip?generation=1698689249131026&alt=media'


def is_login_error_exists(driver):
    """
    Check if there's a login error on the page.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        bool: True if a login error exists, False otherwise.
    """
    try:
        driver.find_element(By.XPATH, "//div[@class='js-flash-alert']").text
        return True
    except selenium.common.exceptions.NoSuchElementException:
        return False


def is_2Fauth(driver):
    """
    Check if two-factor authentication is enabled.

    Args:
        driver: The Selenium WebDriver instance.

    Returns:
        bool: True if 2FA is enabled, False otherwise.
    """
    two_factor_auth = False
    try:
        if driver.find_element(By.XPATH, '//*[contains(text(), "Two-factor authentication")]'):
            two_factor_auth = True
        else:
            two_factor_auth = False
    except:
        two_factor_auth = False
    return two_factor_auth


class TwoFactorAuth():
    """Class to handle two-factor authentication."""

    def __init__(self, logger):
        """
        Initialize TwoFactorAuth class.

        Args:
            logger: The logger instance.
        """
        self.logger = logger
        self.auth_ = False
        self.logger.info(f'TwoFactorAuth() has been initialized')
        self.priorities = ["github_mobile_element", "authentication_code_element", "passkey_element"]

    def auth(self, driver):
        """
        Authenticate the user with different methods.

        Args:
            driver: The Selenium WebDriver instance for interacting with the web page.
        """
        for priority in self.priorities:
            try:
                element = getattr(self, priority)
                element(driver)
                if self.auth_:
                    break  # Exit loop if authentication succeeds
            except Exception as e:
                driver.save_screenshot('screenshot_2FAError.png')
                continue  # Move to the next priority if authentication fails

    def github_mobile_element(self, driver):
        """
        Authenticate using GitHub Mobile method.

        Args:
            driver: The Selenium WebDriver instance.
        """
        github_mobile_element = driver.find_element(By.XPATH, '//a[contains(text(), "Use GitHub Mobile")]')
        github_mobile_element.click()
        challenge_value_element = driver.find_element(By.CSS_SELECTOR, 'h3[data-target="sudo-credential-options.githubMobileChallengeValue"]')
        challenge_value = challenge_value_element.text.strip() if challenge_value_element else None

        self.logger.info(f"[2FA][GithubMobile] Enter this value on our mobile app: {challenge_value}")
        self.auth_ = False

        status = 'None'
        while status not in ('OK', 'Keyboard'):
            try:
                time.sleep(6)
                if is_2Fauth(driver):
                    challenge_value_element = driver.find_element(By.CSS_SELECTOR, 'h3[data-target="sudo-credential-options.githubMobileChallengeValue"]')
                    challenge_value = challenge_value_element.text.strip() if challenge_value_element else None
                    self.logger.debug(f'[2FA][GithubMobile] Enter this value on our mobile app: {challenge_value}')
                else:
                    self.logger.info('[2FA][GithubMobile] Successfully authenticated')
                    status = 'OK'
                    self.auth_ = True
                    break
            except KeyboardInterrupt:
                self.logger.error("[2FA][GithubMobile] KeyboardInterrupt")
                status = 'Keyboard'
                break

    def authentication_code_element(self, driver):
        """
        Authenticate using an authentication code.

        Args:
            driver: The Selenium WebDriver instance.
        """
        authentication_code_element = driver.find_element(By.XPATH, '//a[contains(text(), "Use your authenticator app")]')
        authentication_code_element.click()

        def send_new_code(code):
            driver.find_element(By.ID, 'app_totp').send_keys(code)

        def while_ok_or_keyboard():
            status = 'None'
            while status not in ('OK', 'Keyboard'):
                try:
                    time.sleep(0.5)
                    if is_2Fauth(driver):
                        code = input('[2FA][Authenticator] Enter code from authenticator: ')
                        self.logger.debug('[2FA][Authenticator] Enter code from authenticator: ', code)
                        send_new_code(code)
                    else:
                        self.logger.info('[2FA][Authenticator] Successfully authenticated')
                        status = 'OK'
                        self.auth_ = True
                        break
                except KeyboardInterrupt:
                    self.logger.error("[2FA][GithubMobile] KeyboardInterrupt")
                    status = 'Keyboard'
                    break

        while_ok_or_keyboard()

    def passkey_element(self, driver):
        """
        Authenticate using a passkey.

        Args:
            driver: The Selenium WebDriver instance.
        """
        passkey_element = driver.find_element(By.XPATH, '//h2[contains(text(), "Passkey")]')
        passkey_element.click()
        self.auth_ = False
        print('[2FA][Passkey] Click')


class InCodeLogger():
    """Class for logging messages."""

    def __init__(self, logger=None):
        """
        Initialize InCodeLogger class.

        Args:
            logger: The logger instance.
        """
        if logger is not None:
            self.logger = logger
            self.debug = self.logger.debug
            self.info = self.logger.info
            self.error = self.logger.error
            self.logger.debug('Logger is not None')
        else:
            self.logger = self
            class LR():
                def __init__(self, print_bool=True):
                    self.print_bool = print_bool

                def info(self, text):
                    val = 'INFO'
                    self.write(val, text)

                def debug(self, *args):
                    val = 'DEBUG'
                    self.write(val, *args)

                def error(self, *args):
                    val = 'ERROR'
                    self.write(val, *args)

                def write(self,

 val, *args):
                    if self.print_bool:
                        print(f'[{val}]', *args)
            self.logger = LR()
            self.debug = self.logger.debug
            self.info = self.logger.info
            self.error = self.logger.error
            self.logger.debug('Logger is None')


class DownloadDriver():
    """Class to handle downloading the WebDriver."""

    def check(self):
        """
        Check if the WebDriver is installed and download it if not.

        Returns:
            bool: True if the WebDriver is installed, False otherwise.
        """
        if self.platform_system == 'Windows' or self.platform_system == 'Linux':
            if self.platform_system == 'Windows':
                driver_path = os.path.join(self.WDir, 'modules', 'chromedriver', 'Windows', 'chromedriver.exe')
            elif self.platform_system == 'Linux':
                driver_path = os.path.join(self.WDir, 'modules', 'chromedriver', 'Linux', 'chromedriver')

            if not os.path.exists(driver_path):
                try:
                    self.exc_chrome_driver_filepath = os.path.dirname(driver_path)
                    if not os.path.exists(self.exc_chrome_driver_filepath):
                        os.makedirs(self.exc_chrome_driver_filepath)

                    os.chdir(self.exc_chrome_driver_filepath)
                    self.download()
                    self.unzip()
                    os.chdir(self.WDir)

                    return True
                except Exception as err:
                    self.logger.error(f"Error: {err}")
                    return False
            else:
                return True
        else:
            raise NotFoundSuitableDriver('Unknown platform system %s' % self.platform_system)

    def __init__(self, logger):
        """
        Initialize DownloadDriver class.

        Args:
            logger: The logger instance.
        """
        self.logger = logger
        self.WDir = os.path.join(os.getcwd())
        self.platform_system = platform.system()
        self.installed = self.check()
        self.logger.debug('Initial DownloadDriver().platform is %s' % self.platform_system)

    def download(self):
        """Download the WebDriver."""
        if self.platform_system == 'Windows':
            url = win_driver_download_path
        elif self.platform_system == 'Linux':
            url = lin_driver_download_path
        urllib.request.urlretrieve(url, 'chromedriver.zip')
        self.logger.debug('Downloaded chromedriver.zip')

    def unzip(self):
        """Unzip the downloaded WebDriver."""
        try:
            with zipfile.ZipFile('chromedriver.zip', 'r') as zip_ref:
                zip_ref.extractall('.')
                all_files = zip_ref.namelist()
                extracted_folder = all_files[0].split('/')[0]
                source_dir = os.path.join(os.getcwd(), extracted_folder)
                target_dir = self.exc_chrome_driver_filepath

                for item in all_files:
                    item_path = os.path.join(os.getcwd(), item)
                    if os.path.isfile(item_path):
                        shutil.move(item_path, target_dir)

                os.rmdir(source_dir)

        except Exception as err:
            self.logger.error(f"Error while unzipping: {err}")

        finally:
            os.remove('chromedriver.zip')

        self.logger.debug('Unzipped chromedriver.zip')

    def move_files(self, source_dir):
        """
        Move files from source directory to the current directory.

        Args:
            source_dir: The source directory.
        """
        current_dir = os.getcwd()
        source_path = os.path.join(current_dir, source_dir)

        if os.path.exists(source_path) and os.path.isdir(source_path):
            files = os.listdir(source_path)
            for file in files:
                file_path = os.path.join(source_path, file)
                if os.path.isfile(file_path):
                    shutil.move(file_path, current_dir)
                elif os.path.isdir(file_path):
                    self.move_files(file_path)
        self.logger.debug('Moved files')


class InitLogin():
    """Class to handle the initialization and login process."""

    def __init__(self, logger, login, password):
        """
        Initialize InitLogin class.

        Args:
            logger: The logger instance.
            login: The username for login.
            password: The password for login.
        """
        self.logger = logger
        self.loginValue = login
        self.password = password
        self.logger.debug('InitLogin initialized')

        self.config()
        self.login()

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
        options.add_experimental_option("prefs", {"download.default_directory" : self.download_default_directory})
        for option in ['--log-level=3']:
            options.add_argument(option)

        try:
            if service != None:
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            self.logger.debug('InitLogin().get called with service: %s', service)
        except selenium.common.exceptions.NoSuchDriverException as err:
            installed = DownloadDriver(self.logger).installed
            self.logger.error('Driver is not installed: %s')
            if installed == False:
                print('[SELENIUM] Chrome driver has not been installed!')
                return
            return InitLogin(self.logger, self.loginValue, self.password).get()

    def login(self):
        """Login to GitHub."""
        self.logger.debug(f'InitLogin().get called with login: {self.loginValue}')
        self.driver.get('https://github.com/login')
        self.driver.implicitly_wait(50)
        self.driver.implicitly_wait(10)
        input_text_login = self.driver.find_element(By.ID, 'login_field')
        input_text_login.send_keys(self.loginValue)
        input_text_password = self.driver.find_element(By.ID, 'password')
        input_text_password.send_keys(self.password)
        btn = self.driver.find_element(By.NAME, 'commit')
        time.sleep(1)
        btn.click()
        self.driver.implicitly_wait(5)

        if is_login_error_exists(self.driver):
            self.logger.error(f'Password or username is incorrect')
            raise GitHubLoginError('Password or username is incorrect')
        
        self.auth = False
        two_factor_auth = False
        try:
            if self.driver.find_element(By.XPATH, '//*[contains(text(), "Two-factor authentication")]'):
                two_factor_auth = True
            else:
                two_factor_auth = False
        except:
            two_factor_auth = False
            
        if two_factor_auth:
            TWA = TwoFactorAuth(self.logger)
            TWA.authkey(self.driver)
            self.auth = TWA.auth_
        else:
            self.auth = True
        
        if self.auth:
            self.logger.info(f'Authentication success by {self.loginValue}')
        else:
            self.logger.info(f'Authentication failed by {self.loginValue}')

    def change_repository(self, link):
        """
        Change the repository to the specified link.

        Args:
            link: The URL of the repository.
        """
        try:


            self.logger.info(f'Change repository to {link}')
            self.driver.get(link)
        except:
            pass

    def download_zip_archive(self, link):
        """
        Download the ZIP archive of the repository.

        Args:
            link: The URL of the repository.
        """
        try:
            self.logger.info(f'Download zip archive by {link}')
            self.change_repository(link)
            self.driver.implicitly_wait(3)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            button = soup.find('button', {'type': 'button', 'aria-haspopup': 'true', 'tabindex': '0', 'class': 'types__StyledButton-sc-ws60qy-0 unyiY'})

            try:
                button_id = button.get("id")
                self.driver.find_element(By.ID, f'{button_id}').click()
                time.sleep(5)
                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "Download ZIP"))).click()
                while True:
                    if os.path.exists(rf'''{self.download_default_directory}{os.sep}{link.split('/')[4]}-main.zip'''):
                        break
                self.logger.info(f'Download zip archive is success')
            except AttributeError:
                self.logger.error(f'Download zip archive is failed by 403/404 error.')
                raise GitHubDirrectoryNotfoundError('403/404')
        except urllib3.exceptions.MaxRetryError:
            raise GitHubDirrectoryNotfoundError('403/404')

    def quit(self):
        """Quit the WebDriver."""
        self.driver.quit()


if __name__ == '__main__':
    IncodeL = InCodeLogger()
    IL = InitLogin(IncodeL, 'login', 'password')
    IL.download_zip_archive('https://github.com/BSNIKYT/SvodkaDZ')
