"""
Pytest fixtures for Juice Shop test automation.

Provides:
- driver: Selenium WebDriver instance
- user: Test account credentials from new-user.json
- ensure_user_registered: Session-scoped fixture to register test user
- login: Auto-login fixture that runs before each test
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
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:3000"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def user():
    """Load test user credentials from new-user.json."""
    path = os.path.join(os.path.dirname(__file__), "new-user.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def driver():
    """Create and return a Chrome WebDriver instance."""
    logger.info("Initializing Chrome WebDriver...")
    opts = Options()
    # Headless is enabled by default for CI; set HEADLESS=0 to see the browser locally
    headless = os.environ.get("HEADLESS", "1")
    if headless not in ("0", "false", "False"):
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--remote-allow-origins=*")

    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1920, 1080)  # Desktop view for better compatibility

    logger.info("✓ WebDriver initialized")
    try:
        yield d
    finally:
        d.quit()
        logger.info("✓ WebDriver closed")


@pytest.fixture(scope="session", autouse=True)
def ensure_user_registered(driver, user):
    """Attempt to register the test user once per session.

    This step is best-effort and non-fatal: if the user already exists or the
    registration UI is not available, tests continue. Keep registration minimal
    to avoid noise in CI.
    """
    try:
        logger.info("Attempting session registration (non-fatal)")
        driver.get(BASE_URL + "/#/register")
        time.sleep(1)

        # Try to remove overlays if they exist
        try:
            driver.execute_script(
                """
                const selectors = ['.cdk-overlay-backdrop', '.mat-mdc-dialog-container',
                                   '.mat-mdc-dialog-surface', '.overlay'];
                selectors.forEach(s => document.querySelectorAll(s).forEach(n => n.remove()));
                """
            )
        except Exception:
            pass

        # Basic form filling if fields are present
        email_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
        visible_emails = [e for e in email_inputs if e.is_displayed()]
        if visible_emails:
            visible_emails[0].clear()
            visible_emails[0].send_keys(user["email"])

        pwd_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        visible_pwds = [p for p in pwd_inputs if p.is_displayed()]
        if visible_pwds:
            visible_pwds[0].clear()
            visible_pwds[0].send_keys(user["password"])
            if len(visible_pwds) > 1:
                visible_pwds[1].clear()
                visible_pwds[1].send_keys(user["password"])

        regs = driver.find_elements(By.XPATH, "//button[contains(., 'Register') or contains(., 'Sign up')]")
        if regs:
            try:
                regs[0].click()
            except Exception:
                driver.execute_script("arguments[0].click();", regs[0])
            time.sleep(1)
            logger.info("Registration form submitted (if present)")
    except Exception as e:
        logger.debug(f"Registration step skipped/failed: {type(e).__name__}")

    yield


def _remove_overlays(driver):
    """Remove Angular Material overlays and dialogs."""
    try:
        driver.execute_script("""
        const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing',
                           '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface',
                           'dialog[role="dialog"]', '.overlay', '.modal-backdrop'];
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => el.remove());
        });
        """)
    except Exception:
        pass


def _click_with_fallback(driver, element):
    """Click with fallbacks: normal -> JS -> remove overlays + JS."""
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
    Auto-login before each test (TASK 1).
    
    Authenticates the user before test execution. Handles Angular Material overlays
    and implements multi-level click strategy for stability.
    """
    logger.info("Starting auto-login for %s", user['email'])
    wait = WebDriverWait(driver, 15)

    # Navigate to home page
    logger.debug("Navigating to home page")
    driver.get(BASE_URL)
    time.sleep(1.5)

    _remove_overlays(driver)
    logger.debug("Overlays removed on page load")

    # Open account menu
    try:
        acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
        logger.debug("Clicking account menu")
        _click_with_fallback(driver, acct_btn)
        logger.debug("Account menu opened")
        time.sleep(0.8)
    except Exception as e:
        logger.warning("Could not click account menu: %s", type(e).__name__)

    # Click login button
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
        logger.debug("Clicking login button")
        _click_with_fallback(driver, login_btn)
        logger.debug("Login dialog opened")
        time.sleep(0.8)
    except Exception as e:
        logger.warning("Could not click login button: %s", type(e).__name__)

    # Fill email
    try:
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        logger.debug("Filling login email")
        email_input.clear()
        email_input.send_keys(user["email"])
        logger.debug("Email entered")
        time.sleep(0.6)
    except Exception as e:
        logger.warning("Could not fill email: %s", type(e).__name__)

    # Fill password
    try:
        pwd_input = driver.find_element(By.ID, "password")
        logger.debug("Filling login password")
        pwd_input.clear()
        pwd_input.send_keys(user["password"])
        logger.debug("Password entered")
        time.sleep(0.6)
    except Exception as e:
        logger.warning("Could not fill password: %s", type(e).__name__)

    # Submit form
    try:
        _remove_overlays(driver)
        logger.debug("Submitting login form")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        _click_with_fallback(driver, submit_btn)
        logger.debug("Login form submitted")
        time.sleep(1.2)
    except Exception as e:
        logger.warning("Could not submit login form: %s", type(e).__name__)

    # Wait for login complete
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Log out')]")
        ))
        logger.info("Login successful for %s", user['email'])
        time.sleep(0.3)
    except Exception as e:
        logger.error("Login verification failed: %s", type(e).__name__)
        time.sleep(1)

    yield

    # Test execution complete - no additional cleanup required
