from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

BASE_URL = "http://localhost:3000"

def test_add_card_ui(driver):
    wait = WebDriverWait(driver, 15)
    driver.get(BASE_URL)
    # remove any overlays/dialogs that may cover the navbar after navigation
    try:
        driver.execute_script("""
        const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', '.mat-mdc-backdrop', '.overlay', '.modal-backdrop', '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface', '.cdk-global-overlay-wrapper'];
        selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
        const closeButtons = document.querySelectorAll('[mat-dialog-close], button[aria-label="Close"], button.close, .close-button');
        closeButtons.forEach(b => { try { b.click(); } catch(e) {} });
        """)
    except Exception:
        pass
    # open account menu
        # ensure overlays are gone before clicking the account button
        try:
            wait.until(lambda d: not d.execute_script("return !!document.querySelector('.cdk-overlay-backdrop, .cdk-overlay-backdrop-showing, .mat-mdc-dialog-surface, .mat-mdc-backdrop, .overlay')"))
        except Exception:
            pass
        acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
    try:
        acct_btn.click()
    except Exception:
        # fallback to JS click if an overlay still intercepts the click
        try:
            driver.execute_script("arguments[0].click();", acct_btn)
        except Exception:
            # last resort: remove common overlay selectors and try JS click again
            try:
                driver.execute_script("""
                const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', '.mat-mdc-backdrop', '.overlay', '.modal-backdrop', '.mat-mdc-dialog-surface'];
                selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
                """)
            except Exception:
                pass
            driver.execute_script("arguments[0].click();", acct_btn)
    # go to account/profile page
    try:
        acct = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'My Account') or contains(text(),'Account')]")))
        acct.click()
    except Exception:
        # sometimes account link is directly visible in menu
        pass

    # click Payment Methods (text may vary)
        try:
            wait.until(lambda d: not d.execute_script("return !!document.querySelector('.cdk-overlay-backdrop, .cdk-overlay-backdrop-showing, .mat-mdc-dialog-surface, .mat-mdc-backdrop, .overlay')"))
        except Exception:
            pass
        pm = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Payment Methods') or contains(text(),'Payments') or contains(text(),'My Payments')]")))
    pm.click()

    # click Add (variations)
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add') or contains(., 'Add Card') or contains(., 'Add Payment')]")))
    add_btn.click()

    # prepare card values
    last4 = str(random.randint(1000, 9999))
    card_number = f"411111111111{last4}"

    # try to fill inputs by placeholders or positions
    try:
        # Name on card
        name_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Name on Card' or @id='cardName' or contains(@placeholder,'Name')]")))
        name_field.clear()
        name_field.send_keys("Test User")
        # Card number
        num_field = driver.find_element(By.XPATH, "//input[@placeholder='Card Number' or @id='cardNumber' or contains(@placeholder,'Card')]")
        num_field.clear()
        num_field.send_keys(card_number)
        # Month / Year / CVC
        driver.find_element(By.XPATH, "//input[@placeholder='Expiry Month' or @id='cardMonth' or contains(@placeholder,'Month')]").send_keys("12")
        driver.find_element(By.XPATH, "//input[@placeholder='Expiry Year' or @id='cardYear' or contains(@placeholder,'Year')]").send_keys("2030")
        driver.find_element(By.XPATH, "//input[@placeholder='CVV' or @id='cardCvv' or contains(@placeholder,'CVC') or contains(@placeholder,'CVV')]").send_keys("123")
    except Exception:
        # fallback: use visible inputs in sequence
        inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        if len(inputs) >= 4:
            inputs[0].send_keys("Test User")
            inputs[1].send_keys(card_number)
            inputs[2].send_keys("12")
            inputs[3].send_keys("2030")
        else:
            raise

    # click Save / Add
    save_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Save') or contains(., 'Add') or contains(., 'Submit')]")
    if save_btns:
        save_btns[0].click()
    time.sleep(1)

    # assert last 4 digits are present somewhere on the page
    assert last4 in driver.page_source
