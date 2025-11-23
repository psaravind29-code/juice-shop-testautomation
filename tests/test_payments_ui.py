"""
UI Test: Navigate to My Payments and add card details.

This test demonstrates:
- Navigating through the UI after login (autouse login fixture)
- Using stable locators (IDs, aria-labels, XPath with text)
- Handling overlays and dynamic elements
- Generating unique test data (card numbers)
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

BASE_URL = "http://localhost:3000"


def test_add_card_ui(driver):
    """
    Test that a logged-in user can navigate to Payments and add a card.
    
    Precondition: autouse login fixture has already authenticated the user.
    """
    wait = WebDriverWait(driver, 15)
    
    # Navigate to home
    driver.get(BASE_URL)
    
    # Remove any overlays that might block clicks
    _remove_overlays(driver)
    
    # Wait briefly for overlays to be fully gone
    try:
        wait.until(lambda d: not d.execute_script(
            "return !!document.querySelector('.cdk-overlay-backdrop, .mat-mdc-dialog-surface, .overlay')"
        ))
    except Exception:
        pass
    
    # Open account menu by clicking navbar account button
    acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
    _click_with_fallback(driver, acct_btn)
    
    # Navigate to My Account (sometimes appears in the menu)
    try:
        acct_link = wait.until(EC.element_to_be_clickable((By.XPATH, 
            "//*[contains(text(),'My Account') or contains(text(),'Account')]"
        )))
        _click_with_fallback(driver, acct_link)
    except Exception:
        # Account link might not exist; Payment Methods may be directly accessible from menu
        pass
    
    # Wait for overlays again before clicking Payment Methods
    try:
        wait.until(lambda d: not d.execute_script(
            "return !!document.querySelector('.cdk-overlay-backdrop, .mat-mdc-dialog-surface')"
        ))
    except Exception:
        pass
    
    # Click on Payment Methods (text variations handled)
    pm_link = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//*[contains(text(),'Payment Methods') or contains(text(),'Payments') or contains(text(),'My Payments')]"
    )))
    _click_with_fallback(driver, pm_link)
    
    # Click Add button to open card form
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//button[contains(., 'Add') or contains(., 'Add Card') or contains(., 'Add Payment')]"
    )))
    _click_with_fallback(driver, add_btn)
    
    # Generate unique test card number
    last4 = str(random.randint(1000, 9999))
    card_number = f"411111111111{last4}"
    
    # Fill card form: try ID/name locators first, fallback to positional
    try:
        # Name on Card
        name_field = wait.until(EC.visibility_of_element_located((By.XPATH,
            "//input[@placeholder='Name on Card' or @id='cardName' or contains(@placeholder,'Name')]"
        )))
        name_field.clear()
        name_field.send_keys("Test User")
        
        # Card Number
        num_field = driver.find_element(By.XPATH,
            "//input[@placeholder='Card Number' or @id='cardNumber' or contains(@placeholder,'Card')]"
        )
        num_field.clear()
        num_field.send_keys(card_number)
        
        # Expiry Month
        month_field = driver.find_element(By.XPATH,
            "//input[@placeholder='Expiry Month' or @id='cardMonth' or contains(@placeholder,'Month')]"
        )
        month_field.clear()
        month_field.send_keys("12")
        
        # Expiry Year
        year_field = driver.find_element(By.XPATH,
            "//input[@placeholder='Expiry Year' or @id='cardYear' or contains(@placeholder,'Year')]"
        )
        year_field.clear()
        year_field.send_keys("2030")
        
        # CVV
        cvv_field = driver.find_element(By.XPATH,
            "//input[@placeholder='CVV' or @id='cardCvv' or contains(@placeholder,'CVC') or contains(@placeholder,'CVV')]"
        )
        cvv_field.clear()
        cvv_field.send_keys("123")
    except Exception:
        # Fallback: fill visible inputs in order (Name, Card#, Month, Year)
        inputs = driver.find_elements(By.CSS_SELECTOR, "input:not([disabled]):not([readonly])")
        visible_inputs = [inp for inp in inputs if inp.is_displayed()]
        
        if len(visible_inputs) >= 5:
            visible_inputs[0].clear(); visible_inputs[0].send_keys("Test User")
            visible_inputs[1].clear(); visible_inputs[1].send_keys(card_number)
            visible_inputs[2].clear(); visible_inputs[2].send_keys("12")
            visible_inputs[3].clear(); visible_inputs[3].send_keys("2030")
            visible_inputs[4].clear(); visible_inputs[4].send_keys("123")
        else:
            raise AssertionError(f"Expected at least 5 visible input fields, found {len(visible_inputs)}")
    
    # Submit the form by clicking Save/Submit button
    time.sleep(0.5)  # Brief pause for form to be ready
    save_btns = driver.find_elements(By.XPATH,
        "//button[contains(., 'Save') or contains(., 'Add') or contains(., 'Submit')]"
    )
    if save_btns:
        _click_with_fallback(driver, save_btns[0])
    
    # Wait for confirmation and verify card was added
    time.sleep(1)
    
    # Assert: the last 4 digits should appear somewhere on the page (success indicator)
    assert last4 in driver.page_source, f"Card ending in {last4} not found in page; card may not have been added"


def _remove_overlays(driver):
    """Remove CDK overlays, dialogs, and click close buttons."""
    try:
        driver.execute_script("""
        const selectors = [
            '.cdk-overlay-backdrop', 
            '.cdk-overlay-backdrop-showing', 
            '.mat-mdc-backdrop', 
            '.overlay', 
            '.modal-backdrop', 
            '.mat-mdc-dialog-container', 
            '.mat-mdc-dialog-surface', 
            '.cdk-global-overlay-wrapper'
        ];
        selectors.forEach(s => { 
            document.querySelectorAll(s).forEach(n => n.remove()); 
        });
        const closeButtons = document.querySelectorAll(
            '[mat-dialog-close], button[aria-label="Close"], button.close, .close-button'
        );
        closeButtons.forEach(b => { 
            try { b.click(); } catch(e) {} 
        });
        """)
    except Exception:
        pass


def _click_with_fallback(driver, element):
    """Click an element; fallback to JS click if normal click fails."""
    try:
        element.click()
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
        except Exception:
            _remove_overlays(driver)
            driver.execute_script("arguments[0].click();", element)
