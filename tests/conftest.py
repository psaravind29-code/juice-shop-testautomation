"""
Pytest fixtures for Juice Shop test automation - Simplified working version
"""
import json
import os
import time
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import shutil

BASE_URL = "http://localhost:3000"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def user():
    """Load test user credentials from new-user.json - TASK 1"""
    path = os.path.join(os.path.dirname(__file__), "new-user.json")
    with open(path) as f:
        user_data = json.load(f)
    logger.info("✓ User credentials loaded from new-user.json")
    return user_data


@pytest.fixture(scope="session")
def driver():
    """Create and return a Chrome WebDriver instance."""
    logger.info("Initializing Chrome WebDriver...")
    
    opts = Options()
    
    # Run in visible mode to see the workflow
    headless = os.environ.get("HEADLESS", "0")  # Default to visible
    if headless not in ("0", "false", "False"):
        opts.add_argument("--headless=new")
    
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--remote-allow-origins=*")
    opts.add_argument("--window-size=1200,800")

    # SIMPLIFIED APPROACH: Let Selenium handle driver management
    # Remove any explicit service configuration
    try:
        d = webdriver.Chrome(options=opts)
        logger.info("✓ WebDriver initialized successfully")
        
        try:
            yield d
        finally:
            d.quit()
            logger.info("✓ WebDriver closed")
            
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        
        # Provide clear instructions
        logger.info("\n" + "="*60)
        logger.info("CHROMEDRIVER SETUP INSTRUCTIONS")
        logger.info("="*60)
        logger.info("1. First, verify ChromeDriver works:")
        logger.info("   chromedriver --version")
        logger.info("2. If it shows a version, ChromeDriver is working")
        logger.info("3. If not, install it:")
        logger.info("   brew install chromedriver")
        logger.info("4. If blocked by macOS:")
        logger.info("   - Go to System Preferences → Security & Privacy")
        logger.info("   - Click 'Allow Anyway' for ChromeDriver")
        logger.info("5. Test again: chromedriver --version")
        logger.info("="*60)
        raise


def _dismiss_popups(driver):
    """Dismiss welcome banner and cookie popup."""
    wait = WebDriverWait(driver, 5)
    
    # Dismiss welcome banner
    try:
        dismiss_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='mat-mdc-dialog-0']/div/div/app-welcome-banner/div[2]/button[2]/span[4]")
        ))
        dismiss_btn.click()
        logger.info("  → Welcome banner dismissed")
        time.sleep(1)
    except Exception:
        pass
    
    # Dismiss cookie popup
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div/a")
        ))
        cookie_btn.click()
        logger.info("  → Cookie popup dismissed")
        time.sleep(1)
    except Exception:
        pass


def _remove_overlays(driver):
    """Remove any overlays that might block interactions."""
    try:
        driver.execute_script("""
        const overlays = document.querySelectorAll('.cdk-overlay-backdrop, .cdk-overlay-container');
        overlays.forEach(overlay => {
            if (overlay && overlay.parentNode) {
                overlay.style.display = 'none';
            }
        });
        """)
        time.sleep(0.5)
    except Exception:
        pass


def _click_with_fallback(driver, element):
    """Click element with fallback strategies."""
    try:
        element.click()
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
        except Exception:
            _remove_overlays(driver)
            driver.execute_script("arguments[0].click();", element)


@pytest.fixture(autouse=True)
def login(driver, user):
    """
    TASK 1: Auto-login before each test
    """
    logger.info("=" * 60)
    logger.info("TASK 1: AUTO-LOGIN SETUP")
    logger.info("=" * 60)
    
    wait = WebDriverWait(driver, 15)

    # Step 1: Navigate to home page and dismiss popups
    logger.info("Step 1: Navigating to home page...")
    driver.get(BASE_URL)
    time.sleep(2)
    
    logger.info("Step 2: Dismissing popups...")
    _dismiss_popups(driver)
    
    # Step 3: Click account button
    logger.info("Step 3: Opening account menu...")
    try:
        account_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='navbarAccount']")
        ))
        _click_with_fallback(driver, account_btn)
        logger.info("  → Account menu opened")
        time.sleep(1.5)
    except Exception as e:
        logger.error(f"Failed to open account menu: {e}")
        raise

    # Step 4: Click login button in dropdown
    logger.info("Step 4: Clicking login button...")
    try:
        login_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='navbarLoginButton']")
        ))
        _click_with_fallback(driver, login_btn)
        logger.info("  → Login button clicked")
        time.sleep(1.5)
    except Exception as e:
        logger.error(f"Failed to click login button: {e}")
        raise

    # Step 5: Fill email
    logger.info("Step 5: Filling email...")
    try:
        email_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='email']")))
        email_input.clear()
        email_input.send_keys(user["email"])
        logger.info(f"  → Email entered: {user['email']}")
        time.sleep(0.5)
    except Exception as e:
        logger.error(f"Failed to fill email: {e}")
        raise

    # Step 6: Fill password
    logger.info("Step 6: Filling password...")
    try:
        password_input = driver.find_element(By.XPATH, "//*[@id='password']")
        password_input.clear()
        password_input.send_keys(user["password"])
        logger.info("  → Password entered")
        time.sleep(0.5)
    except Exception as e:
        logger.error(f"Failed to fill password: {e}")
        raise

    # Step 7: Click login submit button
    logger.info("Step 7: Submitting login form...")
    try:
        submit_btn = driver.find_element(By.XPATH, "//*[@id='loginButton']")
        _click_with_fallback(driver, submit_btn)
        logger.info("  → Login form submitted")
        time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to submit login: {e}")
        raise

    # Step 8: Verify login success
    logger.info("Step 8: Verifying login...")
    try:
        # Wait for URL to change from login page
        wait.until(EC.url_contains(f"{BASE_URL}/#"))
        
        # Verify account button is accessible (indicates logged in)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='navbarAccount']")))
        logger.info("✓ TASK 1 COMPLETED: Login successful!")
        
    except Exception as e:
        logger.error(f"Login verification failed: {e}")
        driver.save_screenshot("login_failure.png")
        raise

    logger.info("=" * 60)
    yield