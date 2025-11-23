"""
Pytest fixtures for Juice Shop test automation.
"""
import json
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:3000"


@pytest.fixture(scope="session")
def user():
    """Load test user credentials from new-user.json."""
    path = os.path.join(os.path.dirname(__file__), "new-user.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def driver():
    """Create and return a Chrome WebDriver instance."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--remote-allow-origins=*")
    
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1280, 900)
    
    print("\n✓ WebDriver initialized")
    yield d
    d.quit()
    print("✓ WebDriver closed")


@pytest.fixture(scope="session", autouse=True)
def ensure_user_registered(driver, user):
    """Register the test user once per session (non-fatal if fails)."""
    try:
        print("\n[Setup] Attempting to register test user...")
        driver.get(BASE_URL + "/#/register")
        time.sleep(2)
        
        # Remove overlays
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
        
        # Fill email
        email_inputs = driver.find_elements(By.CSS_SELECTOR, 
                                           "input[type='email'], input[name='email']")
        visible_emails = [e for e in email_inputs if e.is_displayed()]
        if visible_emails:
            visible_emails[0].clear()
            visible_emails[0].send_keys(user["email"])
            print(f"[Setup]   - Email: {user['email']}")
        
        # Fill password
        pwd_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        visible_pwds = [p for p in pwd_inputs if p.is_displayed()]
        if len(visible_pwds) >= 1:
            visible_pwds[0].clear()
            visible_pwds[0].send_keys(user["password"])
            if len(visible_pwds) >= 2:
                visible_pwds[1].clear()
                visible_pwds[1].send_keys(user["password"])
            print("[Setup]   - Password entered")
        
        # Fill security answer
        try:
            sec_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            visible_sec = [s for s in sec_inputs if s.is_displayed()]
            if visible_sec:
                visible_sec[0].clear()
                visible_sec[0].send_keys("TestAnswer")
        except Exception:
            pass
        
        # Click Register
        regs = driver.find_elements(By.XPATH, 
                                    "//button[contains(., 'Register') or contains(., 'Sign up')]")
        if regs:
            try:
                regs[0].click()
            except Exception:
                driver.execute_script("arguments[0].click();", regs[0])
            time.sleep(2)
            print("[Setup] ✓ Register clicked")
            
    except Exception as e:
        print(f"[Setup] Registration attempt finished: {type(e).__name__}")
    
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
    """Auto-login before each test with overlay handling."""
    wait = WebDriverWait(driver, 15)
    driver.get(BASE_URL)
    time.sleep(1)
    
    _remove_overlays(driver)
    
    # Open account menu
    try:
        acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
        _click_with_fallback(driver, acct_btn)
        time.sleep(0.5)
    except Exception:
        pass
    
    # Click login button
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
        _click_with_fallback(driver, login_btn)
        time.sleep(0.5)
    except Exception:
        pass
    
    # Fill email
    try:
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        email_input.clear()
        email_input.send_keys(user["email"])
    except Exception:
        pass
    
    # Fill password
    try:
        pwd_input = driver.find_element(By.ID, "password")
        pwd_input.clear()
        pwd_input.send_keys(user["password"])
    except Exception:
        pass
    
    # Submit form
    try:
        _remove_overlays(driver)
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        _click_with_fallback(driver, submit_btn)
    except Exception:
        pass
    
    # Wait for login complete
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Log out')]")
        ))
    except Exception:
        time.sleep(2)
    
    yield
    
    # Teardown: logout
    try:
        _remove_overlays(driver)
        acct_btn = driver.find_element(By.ID, "navbarAccount")
        _click_with_fallback(driver, acct_btn)
        logout_btns = driver.find_elements(By.XPATH, 
                                          "//*[contains(text(), 'Logout') or contains(text(), 'Log out')]")
        if logout_btns:
            _click_with_fallback(driver, logout_btns[0])
    except Exception:
        pass
