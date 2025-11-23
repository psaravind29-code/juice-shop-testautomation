"""
Script to discover locators in Juice Shop application.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from conftest import BASE_URL, init_driver

def discover_juice_shop_locators():
    driver = init_driver(headless=False)
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        print("=== JUICE SHOP LOCATOR DISCOVERY ===")
        
        # Find account menu
        print("\n1. ACCOUNT MENU BUTTONS:")
        account_selectors = [
            "button#navbarAccount",
            "button[aria-label*='account' i]",
            "button[aria-label*='menu' i]",
            ".account-menu",
            "[aria-label='Show/hide account menu']"
        ]
        
        for selector in account_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✓ Found with: {selector}")
                print(f"  Text: '{element.text}' | ID: {element.get_attribute('id')}")
            except:
                print(f"✗ Not found: {selector}")
        
        # Click account menu to see dropdown
        try:
            account_btn = driver.find_element(By.ID, "navbarAccount")
            account_btn.click()
            time.sleep(2)
            
            print("\n2. ACCOUNT MENU ITEMS:")
            menu_items = driver.find_elements(By.CSS_SELECTOR, "button, a")
            for item in menu_items:
                if item.is_displayed() and item.text.strip():
                    print(f"  - '{item.text}'")
                    print(f"    ID: {item.get_attribute('id')}")
                    print(f"    Class: {item.get_attribute('class')}")
                    print(f"    aria-label: {item.get_attribute('aria-label')}")
            
        except Exception as e:
            print(f"Could not open account menu: {e}")
        
        # Take screenshot
        driver.save_screenshot("juice_shop_discovery.png")
        
        input("\nPress Enter to close browser and see XPath examples...")
        
    finally:
        driver.quit()

def show_xpath_examples():
    print("\n3. USEFUL XPATH EXAMPLES:")
    print("""
    Common XPath patterns for Juice Shop:
    
    - By text:          //button[contains(text(), 'Orders & Payments')]
    - By partial text:  //*[contains(., 'Payment')]
    - By ID:            //*[@id='navbarAccount']
    - By attribute:     //button[@aria-label='Show/hide account menu']
    - Combination:      //button[@id='navbarLoginButton' and contains(text(), 'Login')]
    
    Best practices:
    1. Use IDs when available (most stable)
    2. Use text content for buttons/links
    3. Use aria-labels for accessibility elements
    4. Avoid index-based selectors like [1], [2]
    """)

if __name__ == "__main__":
    discover_juice_shop_locators()
    show_xpath_examples()