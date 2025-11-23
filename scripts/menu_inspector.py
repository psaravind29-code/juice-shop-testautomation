"""
Diagnostic script to inspect Juice Shop menu structure after login.
Helps identify the correct locators for Payment Methods navigation.
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
    print("\n📋 Juice Shop Menu Structure Inspector\n")
    
    # Navigate to home
    print("1. Navigating to home...")
    driver.get(BASE_URL)
    time.sleep(2)
    
    # Remove overlays
    print("2. Removing overlays...")
    driver.execute_script("""
    const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing',
                       '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface'];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => el.remove());
    });
    """)
    time.sleep(1)
    
    # Open account menu
    print("3. Clicking account menu...")
    wait = WebDriverWait(driver, 10)
    acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
    
    try:
        acct_btn.click()
    except:
        driver.execute_script("arguments[0].click();", acct_btn)
    
    time.sleep(1)
    
    # Remove overlays again
    driver.execute_script("""
    const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing',
                       '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface'];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => el.remove());
    });
    """)
    time.sleep(1)
    
    # Click login button
    print("4. Clicking login button...")
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
    try:
        login_btn.click()
    except:
        driver.execute_script("arguments[0].click();", login_btn)
    
    time.sleep(1)
    
    # Fill and submit login
    print("5. Logging in...")
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
    
    # Wait for login to complete
    print("6. Waiting for login to complete...")
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//*[contains(text(), 'Logout')]")
    ))
    time.sleep(2)
    
    # Now inspect the menu
    print("7. Inspecting account menu structure after login...\n")
    
    # Click account menu again
    driver.execute_script("""
    const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing',
                       '.mat-mdc-dialog-container', '.mat-mdc-dialog-surface'];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => el.remove());
    });
    """)
    time.sleep(0.5)
    
    acct_btn = driver.find_element(By.ID, "navbarAccount")
    try:
        acct_btn.click()
    except:
        driver.execute_script("arguments[0].click();", acct_btn)
    
    time.sleep(1)
    
    # Get all menu items
    print("📌 MENU ITEMS IN ACCOUNT DROPDOWN:\n")
    
    # Get all links and buttons in dropdown
    all_links = driver.find_elements(By.XPATH, "//a | //button")
    
    menu_items = []
    for link in all_links:
        try:
            if link.is_displayed():
                text = link.text.strip()
                if text and len(text) > 0:
                    tag = link.tag_name
                    classes = link.get_attribute('class')
                    id_attr = link.get_attribute('id')
                    href = link.get_attribute('href')
                    
                    item = {
                        'text': text,
                        'tag': tag,
                        'id': id_attr,
                        'class': classes,
                        'href': href
                    }
                    menu_items.append(item)
                    print(f"  • {text}")
                    if id_attr:
                        print(f"    ID: {id_attr}")
                    if href:
                        print(f"    Href: {href}")
                    print()
        except:
            pass
    
    # Look specifically for payment-related items
    print("\n🔍 SEARCHING FOR PAYMENT-RELATED ITEMS:\n")
    
    payment_items = [item for item in menu_items if 'payment' in item['text'].lower() or 'card' in item['text'].lower()]
    
    if payment_items:
        print("✓ Found payment-related items:")
        for item in payment_items:
            print(f"  • {item['text']}")
            if item['id']:
                print(f"    ID: {item['id']}")
            if item['href']:
                print(f"    Href: {item['href']}")
            print()
    else:
        print("✗ No payment-related items found in current menu")
        print("\n📋 All visible text in page:")
        
        # Get all text on page
        all_text = driver.execute_script("""
            return document.body.innerText;
        """)
        
        print(all_text[:500] + "..." if len(all_text) > 500 else all_text)
    
    # Try navigating directly to payment methods page
    print("\n\n🔗 TRYING DIRECT NAVIGATION:\n")
    
    possible_urls = [
        "/#/PaymentMethods",
        "/#/payment-methods",
        "/#/my-payments",
        "/#/payments",
        "/payment-methods",
        "/payments"
    ]
    
    for url in possible_urls:
        test_url = BASE_URL + url
        print(f"Trying: {test_url}")
        driver.get(test_url)
        time.sleep(1)
        
        # Check if page loaded
        try:
            header = driver.find_element(By.XPATH, "//*[contains(text(), 'Payment') or contains(text(), 'payment')]")
            print(f"  ✓ FOUND! Page loaded successfully with payment content")
            print(f"  Current URL: {driver.current_url}")
            break
        except:
            print(f"  ✗ Page doesn't contain payment content")
    
    print("\n✅ Inspection complete!")

finally:
    driver.quit()
    print("\n✓ Driver closed")
