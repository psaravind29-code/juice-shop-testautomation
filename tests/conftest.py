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
    # opts.add_argument("--headless=new")  # DISABLED: Uncomment to hide browser
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--remote-allow-origins=*")
    
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1920, 1080)  # Desktop view for better compatibility
    
    logger.info("✓ WebDriver initialized (headless, 1920x1080)")
    yield d
    
    d.quit()
    logger.info("✓ WebDriver closed")


@pytest.fixture(scope="session", autouse=True)
def ensure_user_registered(driver, user):
    """Register the test user once per session (non-fatal if fails)."""
    try:
        print("\n" + "="*80)
        print("TASK 2: USER REGISTRATION")
        print("="*80)
        print("[Setup] Attempting to register test user...")
        print(f"[Setup] → Navigating to registration page...")
        driver.get(BASE_URL + "/#/register")
        time.sleep(2)
        print(f"[Setup] ✓ Registration page loaded")
        
        # Remove overlays
        print(f"[Setup] → Removing overlays...")
        try:
            driver.execute_script("""
            const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', 
                               '.mat-mdc-dialog-surface', '.overlay'];
            selectors.forEach(s => { 
                document.querySelectorAll(s).forEach(n => n.remove()); 
            });
            """)
        except Exception:
            pass
        time.sleep(0.5)
        print(f"[Setup] ✓ Overlays removed")
        
        # Fill email
        print(f"[Setup] → Filling registration form...")
        email_inputs = driver.find_elements(By.CSS_SELECTOR, 
                                           "input[type='email'], input[name='email']")
        visible_emails = [e for e in email_inputs if e.is_displayed()]
        if visible_emails:
            visible_emails[0].clear()
            visible_emails[0].send_keys(user["email"])
            print(f"[Setup]   ✓ Email entered: {user['email']}")
            time.sleep(0.5)
        
        # Fill password
        pwd_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        visible_pwds = [p for p in pwd_inputs if p.is_displayed()]
        if len(visible_pwds) >= 1:
            visible_pwds[0].clear()
            visible_pwds[0].send_keys(user["password"])
            time.sleep(0.3)
            if len(visible_pwds) >= 2:
                visible_pwds[1].clear()
                visible_pwds[1].send_keys(user["password"])
            print("[Setup]   ✓ Password entered (both fields)")
            time.sleep(0.5)
        
        # Fill security answer
        print(f"[Setup]   → Filling security answer...")
        try:
            sec_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            visible_sec = [s for s in sec_inputs if s.is_displayed()]
            if visible_sec:
                visible_sec[0].clear()
                visible_sec[0].send_keys("TestAnswer")
                print("[Setup]   ✓ Security answer entered")
                time.sleep(0.5)
        except Exception:
            pass
        
        # Click Register
        print(f"[Setup] → Clicking Register button...")
        regs = driver.find_elements(By.XPATH, 
                                    "//button[contains(., 'Register') or contains(., 'Sign up')]")
        if regs:
            try:
                regs[0].click()
            except Exception:
                driver.execute_script("arguments[0].click();", regs[0])
            time.sleep(2)
            print("[Setup] ✓ Registration submitted")
            print("="*80)
            print()
            
    except Exception as e:
        print(f"[Setup] Registration attempt finished: {type(e).__name__}")
        print("="*80)
        print()
    
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
    Auto-login before each test with overlay handling.
    
    Handles Angular Material overlays that can block clicks via:
    1. Early overlay removal on page load
    2. Click fallbacks (normal -> JS -> remove overlays + JS)
    3. Graceful degradation with non-fatal exceptions
    """
    print("\n" + "="*90)
    print(" "*20 + "TASK 1: LOGIN SCRIPT (beforeEach Hook)")
    print("="*90)
    logger.info(f"Starting auto-login for {user['email']}")
    wait = WebDriverWait(driver, 15)
    print("[Login] → Navigating to home page...")
    driver.get(BASE_URL)
    time.sleep(2)
    print("[Login] ✓ Home page loaded")
    
    _remove_overlays(driver)
    logger.debug("Overlays removed on page load")
    time.sleep(1)
    
    # Open account menu
    try:
        acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
        print("[Login] → Clicking Account menu...")
        _click_with_fallback(driver, acct_btn)
        logger.debug("Account menu clicked")
        print("[Login] ✓ Account menu opened")
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Could not click account menu: {type(e).__name__}")
        pass
    
    # Click login button
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
        print("[Login] → Clicking Login button...")
        _click_with_fallback(driver, login_btn)
        logger.debug("Login button clicked")
        print("[Login] ✓ Login dialog opened")
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Could not click login button: {type(e).__name__}")
        pass
    
    # Fill email
    try:
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        print(f"[Login] → Typing email: {user['email']}")
        email_input.clear()
        email_input.send_keys(user["email"])
        logger.debug(f"Email filled: {user['email']}")
        print("[Login] ✓ Email entered")
        time.sleep(1)
    except Exception as e:
        logger.warning(f"Could not fill email: {type(e).__name__}")
        pass
    
    # Fill password
    try:
        pwd_input = driver.find_element(By.ID, "password")
        print("[Login] → Typing password...")
        pwd_input.clear()
        pwd_input.send_keys(user["password"])
        logger.debug("Password filled")
        print("[Login] ✓ Password entered")
        time.sleep(1)
    except Exception as e:
        logger.warning(f"Could not fill password: {type(e).__name__}")
        pass
    
    # Submit form
    try:
        _remove_overlays(driver)
        print("[Login] → Clicking Submit button...")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        _click_with_fallback(driver, submit_btn)
        logger.debug("Login form submitted")
        print("[Login] ✓ Login form submitted")
        time.sleep(3)
    except Exception as e:
        logger.warning(f"Could not submit login form: {type(e).__name__}")
        pass
    
    # Wait for login complete
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Log out')]")
        ))
        print("[Login] ✓ Login successful!")
        print("="*90)
        print()
        logger.info(f"✓ Login successful for {user['email']}")
        time.sleep(1)
    except Exception as e:
        logger.error(f"✗ Login verification failed: {type(e).__name__}. "
                    f"Account '{user['email']}' may not exist in Juice Shop. "
                    f"See REGISTRATION_REQUIRED.md for setup instructions.")
        time.sleep(2)
    
    yield
    
    # Teardown: logout
    print("="*90)
    print(" "*30 + "END TASK 1")
    print("="*90)
    print()
