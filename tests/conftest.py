# tests/conftest.py
import json
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://localhost:3000"


@pytest.fixture(scope="session")
def user():
    path = os.path.join(os.path.dirname(__file__), "new-user.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--window-size=1400,900")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture(autouse=True)
def auto_login(driver, user):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 20)

    # Dismiss welcome banner
    try:
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='Close Welcome Banner']"))).click()
        time.sleep(1)
    except:
        pass

    # Navigate directly to login page
    driver.get(f"{BASE_URL}/#/login")
    time.sleep(2)
    
    # Remove overlays
    _remove_overlays(driver)
    time.sleep(0.5)

    # Fill in login form
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(user["email"])
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(user["password"])
    
    # Click login button
    wait.until(EC.element_to_be_clickable((By.ID, "loginButton"))).click()
    
    # Wait for page to load after login
    time.sleep(2)
    print("✓ Login successful")


def _remove_overlays(driver):
    """Remove CDK overlay backdrops and Material dialogs that block interactions."""
    try:
        # Remove CDK overlay backdrops and panes
        driver.execute_script("""
            // Remove all CDK overlays
            document.querySelectorAll('.cdk-overlay-backdrop').forEach(el => el.remove());
            document.querySelectorAll('.cdk-overlay-pane').forEach(el => el.remove());
            
            // Also remove any mat-dialog-container
            document.querySelectorAll('.mat-mdc-dialog-container').forEach(el => el.remove());
            
            // Remove any other blocking overlays
            document.querySelectorAll('[role="presentation"]').forEach(el => {
                if (el.classList.contains('cdk-overlay-backdrop')) el.remove();
            });
        """)
    except:
        pass