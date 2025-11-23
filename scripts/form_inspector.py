"""
Diagnostic script to inspect the Add Card form structure.
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

BASE_URL = "http://localhost:3000"

# Load credentials
with open('tests/new-user.json') as f:
    user = json.load(f)

# Setup driver
opts = Options()
opts.add_argument("--headless=new")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=opts)
driver.set_window_size(1920, 1080)

try:
    print("\n📋 Add Card Form Inspector\n")
    
    # Setup: Navigate and login
    print("1. Navigating and logging in...")
    driver.get(BASE_URL)
    time.sleep(2)
    
    # Remove overlays and login (same as conftest)
    driver.execute_script("""
    const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing',
                       '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface'];
    selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); });
    """)
    
    wait = WebDriverWait(driver, 10)
    
    # Click account menu
    acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
    try:
        acct_btn.click()
    except:
        driver.execute_script("arguments[0].click();", acct_btn)
    time.sleep(0.5)
    
    # Click login button
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
    try:
        login_btn.click()
    except:
        driver.execute_script("arguments[0].click();", login_btn)
    time.sleep(0.5)
    
    # Login
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
    email_input.clear()
    email_input.send_keys(user["email"])
    
    pwd_input = driver.find_element(By.ID, "password")
    pwd_input.clear()
    pwd_input.send_keys(user["password"])
    
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    try:
        submit_btn.click()
    except:
        driver.execute_script("arguments[0].click();", submit_btn)
    
    # Wait for login
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Logout')]")))
    time.sleep(2)
    
    print("✓ Login successful\n")
    
    # Navigate to Payment Methods
    print("2. Navigating to Payment Methods page...")
    driver.get(f"{BASE_URL}/#/PaymentMethods")
    time.sleep(2)
    
    # Remove overlays
    driver.execute_script("""
    const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing',
                       '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface'];
    selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); });
    """)
    time.sleep(1)
    
    print("✓ On Payment Methods page\n")
    
    # Find and click Add button (specifically on Payment Methods page)
    print("3. Finding and clicking 'Add Card' button...")
    
    # First, verify we're on Payment Methods page
    page_text = driver.find_element(By.TAG_NAME, "body").text
    print(f"Page contains 'Payment Methods': {'Payment Methods' in page_text}")
    print(f"Page contains 'No payment methods found': {'No payment methods found' in page_text}\n")
    
    # Look for Add Card button more specifically
    add_card_btns = driver.find_elements(By.XPATH,
        "//*[contains(text(), 'Add Card') or contains(text(), 'New Card')]"
    )
    
    print(f"Found {len(add_card_btns)} buttons matching 'Add Card' or 'New Card'")
    
    if len(add_card_btns) == 0:
        # Try more generic search
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nAll buttons on page:")
        for i, btn in enumerate(all_buttons):
            if btn.is_displayed():
                print(f"  Button {i}: '{btn.text}'")
    
    # If we have add card button, click it
    if add_card_btns:
        btn = add_card_btns[0]
        try:
            btn.click()
        except:
            driver.execute_script("arguments[0].click();", btn)
        
        time.sleep(2)
    else:
        print("\n⚠️  No 'Add Card' button found. Trying to find payment methods table...")
        # Maybe we need to scroll or the page structure is different
        all_btns = driver.find_elements(By.TAG_NAME, "button")
        for btn in all_btns:
            if btn.is_displayed() and "Add" in btn.text and "Basket" not in btn.text:
                print(f"Found button: {btn.text}")
                try:
                    btn.click()
                except:
                    driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
                break

finally:
    driver.quit()
    print("\n✓ Driver closed")
