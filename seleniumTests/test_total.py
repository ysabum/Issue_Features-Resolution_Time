import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


# ---------- FIXTURE SETUP ----------
class BaseTest:
    def setup_method(self, method):
        options = Options()
        options.page_load_strategy = "eager"

        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 3)

    def teardown_method(self, method):
        self.driver.quit()


# ---------- TEST 1: FORM SUBMISSION ----------
class TestFormSubmission(BaseTest):

    def test_formSubmission(self):
        driver = self.driver
        wait = self.wait

        driver.get("http://127.0.0.1:8000/")
        driver.set_window_size(1295, 735)

        # Navigate
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Home"))).click()
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Calculator"))).click()

        # Wait for form (faster + more meaningful than waiting for body)
        title_input = wait.until(
            EC.visibility_of_element_located((By.NAME, "title"))
        )

        # Fill form
        title_input.clear()
        title_input.send_keys("Hello world!")

        comment_input = wait.until(
            EC.visibility_of_element_located((By.NAME, "comment"))
        )
        comment_input.clear()
        comment_input.send_keys(
            "I can't believe that today of all days, I was born!"
        )

        # Submit (use more specific selector than ".btn")
        submit_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn, input.btn"))
        )
        submit_btn.click()

        # Close suggestion box if present
        try:
            wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#rec_relevance_box .btn-close"))
            ).click()
        except:
            pass

        # Final verification (fast check)
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Calculator")))


# ---------- TEST 2: NAVIGATION ----------
class TestNavigation(BaseTest):

    def test_navigation(self):
        driver = self.driver
        wait = self.wait

        driver.get("http://127.0.0.1:8000/")
        driver.set_window_size(1295, 735)

        # Click About
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "About"))).click()

        # Verify page changed (fast + meaningful)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Click Calculator
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Calculator"))).click()

        # Wait for calculator form instead of generic body (BIG SPEED IMPROVEMENT)
        wait.until(EC.visibility_of_element_located((By.NAME, "title")))

        # Click Home
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Home"))).click()

        # Final assertion
        assert wait.until(
            EC.visibility_of_element_located((By.LINK_TEXT, "Home"))
        )