from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, InvalidSessionIdException, TimeoutException
)
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os, traceback
from datetime import datetime

class LoginPageTests:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = os.environ.get("LOGIN_URL", "https://example.com/login")
        self._init_driver()

    def _init_driver(self):
        """Start (or restart) Chrome WebDriver."""
        try:
            opts = webdriver.ChromeOptions()
            # opts.add_argument("--headless=new")  # enable for CI
            service = Service(ChromeDriverManager().install())
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
            self.driver = webdriver.Chrome(service=service, options=opts)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            print("Could not start Chrome WebDriver:", e)
            raise

    def _dump_debug(self, label: str):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = os.path.join(os.getcwd(), f"selenium_debug_{ts}_{label}")
        os.makedirs(outdir, exist_ok=True)
        # traceback
        try:
            with open(os.path.join(outdir, "traceback.txt"), "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except Exception:
            pass
        # page source
        try:
            with open(os.path.join(outdir, "page_source.html"), "w", encoding="utf-8") as f:
                f.write(self.driver.page_source or "")
        except Exception:
            pass
        # screenshot
        try:
            self.driver.save_screenshot(os.path.join(outdir, "screenshot.png"))
        except Exception:
            pass
        print("Debug info saved to:", outdir)

    def _ensure_session(self):
        if not getattr(self.driver, "session_id", None):
            self._init_driver()

    def test_valid_login(self):
        try:
            self._ensure_session()
            self.driver.get(self.base_url)

            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "login-btn")

            username_field.clear()
            username_field.send_keys("valid_user@example.com")
            password_field.clear()
            password_field.send_keys("correct_password")
            login_button.click()

            self.wait.until(EC.url_contains("/dashboard"))
            print("Valid login test: PASSED")
            return True

        except (InvalidSessionIdException, WebDriverException):
            # try one restart
            try:
                self._init_driver()
                return self.test_valid_login()
            except Exception as e:
                print("Valid login test: FAILED -", e)
                self._dump_debug("valid_login")
                return False

        except Exception as e:
            print("Valid login test: FAILED -", e)
            self._dump_debug("valid_login")
            return False

    def test_invalid_login(self):
        try:
            self._ensure_session()
            self.driver.get(self.base_url)

            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "login-btn")

            username_field.clear()
            username_field.send_keys("invalid_user@example.com")
            password_field.clear()
            password_field.send_keys("wrong_password")
            login_button.click()

            error_message = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            assert "invalid" in (error_message.text or "").lower()
            print("Invalid login test: PASSED")
            return True

        except (InvalidSessionIdException, WebDriverException):
            try:
                self._init_driver()
                return self.test_invalid_login()
            except Exception as e:
                print("Invalid login test: FAILED -", e)
                self._dump_debug("invalid_login")
                return False

        except Exception as e:
            print("Invalid login test: FAILED -", e)
            self._dump_debug("invalid_login")
            return False

    def run_all_tests(self):
        print("Running Login Page Automated Tests...")
        try:
            valid_result = self.test_valid_login()
            invalid_result = self.test_invalid_login()
        finally:
            # ensure driver closed after tests
            try:
                if self.driver:
                    self.driver.quit()
            except Exception:
                pass

        success_rate = (valid_result + invalid_result) / 2 * 100
        print("\nTest Results:")
        print("Success Rate:", success_rate)
        print("Tests Passed:", int(valid_result + invalid_result), "/ 2")
        return success_rate

if __name__ == "__main__":
    tester = LoginPageTests()
    tester.run_all_tests()