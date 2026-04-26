import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestNavigation:
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 10)

    def teardown_method(self, method):
        self.driver.quit()

    def test_navigation(self):
        driver = self.driver
        wait = self.wait

        # Open app
        driver.get("http://127.0.0.1:8000/") # Replace if web app does not open to this address
        driver.set_window_size(1295, 735)

        # Click About
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "About"))).click()

        # Verify About page loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Click Calculator
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Calculator"))).click()

        # Verify Calculator page loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Click Home
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Home"))).click()

        # Final assertion: Home link still visible
        assert wait.until(
            EC.visibility_of_element_located((By.LINK_TEXT, "Home"))
        )