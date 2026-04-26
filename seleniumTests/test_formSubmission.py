import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestFormSubmission:
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 10)

    def teardown_method(self, method):
        self.driver.quit()

    def test_formSubmission(self):
        driver = self.driver
        wait = self.wait

        # Open app
        driver.get("http://127.0.0.1:8000/") # Replace if web app does not open to this address
        driver.set_window_size(1295, 735)

        # Click Home 
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Home"))).click()

        # Go to Calculator
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Calculator"))).click()

        # Fill form
        title_input = wait.until(EC.visibility_of_element_located((By.NAME, "title")))
        title_input.clear()
        title_input.send_keys("Hello world!")

        comment_input = wait.until(EC.visibility_of_element_located((By.NAME, "comment")))
        comment_input.clear()
        comment_input.send_keys("I can't believe that today of all days, I was born!")

        # Submit form
        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn")))
        submit_btn.click()

        # Wait for suggestions box and close it (if it appears)
        try:
            close_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#rec_relevance_box .btn-close"))
            )
            close_btn.click()
        except:
            pass  # element might not appear. that's fine

        # Close any remaining modal/alert close buttons
        try:
            generic_close = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-close"))
            )
            generic_close.click()
        except:
            pass

        # Final check: Calculator link still visible (basic assertion)
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Calculator")))