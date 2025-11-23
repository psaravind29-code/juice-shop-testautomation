import json
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

BASE_URL = "http://localhost:3000"

@pytest.fixture(scope="session")
def user():
    path = os.path.join(os.path.dirname(__file__), "new-user.json")
    with open(path) as f:
        return json.load(f)

@pytest.fixture(scope="session")
def driver():
    opts = Options()
    # remove headless if you want to see the browser
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    # allow newer chrome requiring remote origins flag
    opts.add_argument("--remote-allow-origins=*")
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1280, 900)
    yield d
    d.quit()


@pytest.fixture(scope="session", autouse=True)
def ensure_user_registered(driver, user):
    """Attempt to register the test user once per test session via the UI.
    This is defensive: if the user already exists the registration will fail but we ignore that.
    Runs before the function-scoped autouse `login` fixture.
    """
    wait = WebDriverWait(driver, 10)
    try:
        # try direct route to registration page (works for typical Juice Shop setups)
        driver.get(BASE_URL + '/#/register')
        # remove blocking overlays if any
        try:
            driver.execute_script("""
            const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', '.mat-mdc-backdrop', '.overlay', '.modal-backdrop', '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface'];
            selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
            """)
        except Exception:
            pass

        # fill registration form: prefer visible email and password inputs
        try:
            email_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']")))
            email_el.clear()
            email_el.send_keys(user['email'])
        except Exception:
            # give up filling email if not found
            pass

        try:
            pwds = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
            visible_pwds = [p for p in pwds if p.is_displayed()]
            if visible_pwds:
                visible_pwds[0].clear()
                visible_pwds[0].send_keys(user['password'])
                if len(visible_pwds) > 1:
                    visible_pwds[1].clear()
                    visible_pwds[1].send_keys(user['password'])
        except Exception:
            pass

        # try to click Register (many variations possible)
        try:
            regs = driver.find_elements(By.XPATH, "//button[contains(., 'Register') or contains(., 'Sign up') or contains(., 'Continue')]")
            if regs:
                try:
                    regs[0].click()
                except Exception:
                    try:
                        driver.execute_script("arguments[0].click();", regs[0])
                    except Exception:
                        pass
        except Exception:
            pass

        # small wait to let server process or show errors
        import time
        time.sleep(1)
    except Exception:
        # non-fatal; tests will attempt login regardless
        pass
    # attempt to log in once to establish a session (so subsequent autouse login is a no-op)
    try:
        driver.get(BASE_URL)
        try:
            driver.execute_script("""
            const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', '.mat-mdc-backdrop', '.overlay', '.modal-backdrop'];
            selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
            """)
        except Exception:
            pass
        # open account menu and click login
        try:
            acct = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'navbarAccount')))
            try:
                acct.click()
            except Exception:
                driver.execute_script('arguments[0].click();', acct)
        except Exception:
            pass

        try:
            login_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'navbarLoginButton')))
            try:
                login_btn.click()
            except Exception:
                driver.execute_script('arguments[0].click();', login_btn)
        except Exception:
            # ignore if login button not present
            pass

        # fill login form
        try:
            email_el = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']")))
            email_el.clear(); email_el.send_keys(user['email'])
            pw = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            pw.clear(); pw.send_keys(user['password'])
            # try submit via JS click (avoid overlays)
            try:
                sub = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                driver.execute_script('arguments[0].click();', sub)
            except Exception:
                pass
            # wait briefly for token in localStorage
            token_js = """
            const keys = Object.keys(window.localStorage);
            for (const k of keys) {
              try {
                const v = window.localStorage.getItem(k);
                if (!v) continue;
                if (v.startsWith('{')) {
                  try {
                    const obj = JSON.parse(v);
                    if (obj.token) return obj.token;
                    if (obj.authentication) return obj.authentication;
                  } catch(e){}
                }
                if (typeof v === 'string' && (v.includes('eyJ') || v.length>20)) return v;
              } catch(e){}
            }
            return null;
            """
            import time
            for _ in range(6):
                t = driver.execute_script(token_js)
                if t:
                    break
                time.sleep(0.5)
        except Exception:
            pass
    except Exception:
        pass
    yield

@pytest.fixture(autouse=True)
def login(driver, user):
    """Auto login before each test. Adjust if Juice Shop UI differs."""
    wait = WebDriverWait(driver, 15)
    driver.get(BASE_URL)
    # remove modal/backdrop overlays that can block clicks (cookie banners, overlays)
    try:
        driver.execute_script("""
        const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', '.mat-mdc-backdrop', '.overlay', '.modal-backdrop', '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface', '.cdk-global-overlay-wrapper'];
        selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
        // Attempt to click any dialog close buttons that might be present
        const closeButtons = document.querySelectorAll('[mat-dialog-close], button[aria-label="Close"], button.close, .close-button, button.mat-mdc-icon-button');
        closeButtons.forEach(b => { try { b.click(); } catch(e) {} });
        """)
        # wait briefly for any overlays/dialogs to be removed
        try:
            wait.until(lambda d: not d.execute_script("return !!document.querySelector('.cdk-overlay-backdrop, .cdk-overlay-backdrop-showing, .mat-mdc-backdrop, .mat-mdc-dialog-surface, dialog[role=\"dialog\"]')"))
        except Exception:
            # non-fatal; continue
            pass
    except Exception:
        pass

    # extra defensive removal/close for any stubborn dialog that might cover buttons
    try:
        driver.execute_script("""
        const dialogSelectors = ['.mat-mdc-dialog-container', '.mat-mdc-dialog-surface', 'dialog[role="dialog"]'];
        dialogSelectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
        const closeBtns = document.querySelectorAll('[mat-dialog-close], button[aria-label="Close"], button.close, .close-button');
        closeBtns.forEach(b => { try { b.click(); } catch(e) {} });
        """)
    except Exception:
        pass
    # open account menu
    try:
        acct_el = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
        try:
            acct_el.click()
        except Exception:
            # fallback to JS click if intercepted
            driver.execute_script("arguments[0].click();", acct_el)
    except Exception:
        # fallback: try by aria label or clickable element
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, "[aria-label='Account'], .account")
            if elems:
                try:
                    elems[0].click()
                except Exception:
                    driver.execute_script("arguments[0].click();", elems[0])
        except Exception:
            pass
    # click login button
    try:
        # ensure any dialog that appeared after page load is closed before clicking
        try:
            driver.execute_script("""
            const selectors = ['.mat-mdc-dialog-container', '.mat-mdc-dialog-surface', 'dialog[role="dialog"]'];
            selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
            const closeBtns = document.querySelectorAll('[mat-dialog-close], button[aria-label="Close"], button.close, .close-button');
            closeBtns.forEach(b => { try { b.click(); } catch(e) {} });
            """)
        except Exception:
            pass

        login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
        try:
            login_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", login_btn)
    except Exception:
        # fallback: look for button text
        btns = driver.find_elements(By.XPATH, "//button[contains(., 'Login') or contains(., 'Log in')]")
        if btns:
            try:
                btns[0].click()
            except Exception:
                driver.execute_script("arguments[0].click();", btns[0])
    # fill form (try common ids first)
    try:
        email_el = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        email_el.clear()
        email_el.send_keys(user["email"])
        pwd_el = driver.find_element(By.ID, "password")
        pwd_el.clear()
        pwd_el.send_keys(user["password"])
    except Exception:
        # fallback to inputs by name/placeholder; prefer visible inputs
        candidates = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email'], input[type='text']")
        inputs = [el for el in candidates if el.is_displayed() and el.size.get('height', 0) > 0]
        if inputs:
            try:
                inputs[0].clear()
                inputs[0].send_keys(user["email"])
            except Exception:
                driver.execute_script("arguments[0].value = arguments[1];", inputs[0], user["email"])
        pwds = [el for el in driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input[name='password'], input[placeholder*='password']") if el.is_displayed() and el.size.get('height', 0) > 0]
        if pwds:
            try:
                pwds[0].clear()
                pwds[0].send_keys(user["password"])
            except Exception:
                driver.execute_script("arguments[0].value = arguments[1];", pwds[0], user["password"])
    # submit
    try:
        # close any dialog that might appear just before submit
        try:
            driver.execute_script("""
            const selectors = ['.mat-mdc-dialog-container', '.mat-mdc-dialog-surface', 'dialog[role="dialog"]'];
            selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
            const closeBtns = document.querySelectorAll('[mat-dialog-close], button[aria-label="Close"], button.close, .close-button');
            closeBtns.forEach(b => { try { b.click(); } catch(e) {} });
            """)
        except Exception:
            pass

        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        try:
            submit_btn.click()
        except Exception:
            # try JS click (bypasses some interception)
            try:
                driver.execute_script("arguments[0].click();", submit_btn)
            except Exception:
                # try submitting the enclosing form as a last resort
                try:
                    driver.execute_script("arguments[0].closest('form') && arguments[0].closest('form').submit();", submit_btn)
                except Exception:
                    # final attempt: remove overlays and JS click
                    try:
                        driver.execute_script("""
                        const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', '.mat-mdc-backdrop', '.overlay', '.modal-backdrop', '.mat-mdc-dialog-surface', '.cdk-global-overlay-wrapper'];
                        selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
                        """)
                    except Exception:
                        pass
                    driver.execute_script("arguments[0].click();", submit_btn)
    except Exception:
        btns = driver.find_elements(By.XPATH, "//button[contains(., 'Login') or contains(., 'Log in') or contains(., 'Submit')]")
        if btns:
            btns[0].click()
    # wait for post-login indicator
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Logout') or contains(., 'Log out') or contains(., 'Sign out')]")), 10)
    except Exception:
        # small delay to allow session to settle
        time.sleep(2)
    yield
    # teardown: optional sign out to keep tests isolated
    try:
        # reopen account menu and click logout if present
        driver.find_element(By.ID, "navbarAccount").click()
        logout = driver.find_elements(By.XPATH, "//*[contains(text(),'Logout') or contains(., 'Log out') or contains(., 'Sign out')]")
        if logout:
            logout[0].click()
    except Exception:
        pass
