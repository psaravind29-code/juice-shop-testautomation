# simple_debug.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

BASE_URL = "http://localhost:3000"

def dismiss_welcome_banner(driver):
    """Dismiss the welcome banner if it appears."""
    try:
        # Wait for welcome banner to appear
        dismiss_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='mat-mdc-dialog-0']/div/div/app-welcome-banner/div[2]/button[2]/span[2]/span"))
        )
        dismiss_btn.click()
        print("✓ Welcome banner dismissed")
        time.sleep(1)
        return True
    except Exception:
        print("No welcome banner found or already dismissed")
        return False

def remove_overlays(driver):
    """Remove overlays that might block interactions."""
    try:
        driver.execute_script("""
        // Remove Angular Material overlays and dialogs
        const overlays = document.querySelectorAll('.cdk-overlay-backdrop, .cdk-overlay-container, .cdk-overlay-pane');
        overlays.forEach(overlay => {
            if (overlay && overlay.parentNode) {
                overlay.style.display = 'none';
            }
        });
        """)
        time.sleep(1)
    except Exception:
        pass

def click_with_fallback(driver, element):
    """Click element with fallback strategies."""
    try:
        element.click()
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
        except Exception:
            remove_overlays(driver)
            driver.execute_script("arguments[0].click();", element)

def simple_debug():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    
    try:
        # Load user
        with open('tests/new-user.json', 'r') as f:
            user = json.load(f)
        
        print("=== SIMPLE DEBUG - Juice Shop Navigation ===")
        
        # Navigate to login page
        print("Step 1: Navigating to login page...")
        driver.get(f"{BASE_URL}/#/login")
        time.sleep(2)
        
        # Dismiss welcome banner if present
        dismiss_welcome_banner(driver)
        
        # Remove any overlays
        remove_overlays(driver)
        time.sleep(1)
        
        # Fill credentials
        print("Step 2: Filling login credentials...")
        driver.find_element(By.ID, "email").send_keys(user["email"])
        driver.find_element(By.ID, "password").send_keys(user["password"])
        
        # Click login with overlay handling
        print("Step 3: Clicking login button...")
        login_btn = driver.find_element(By.ID, "loginButton")
        click_with_fallback(driver, login_btn)
        time.sleep(3)
        
        # Dismiss any welcome banner that might appear after login
        dismiss_welcome_banner(driver)
        
        print("Step 4: Checking login success...")
        # Check if login was successful
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "navbarAccount"))
            )
            print("✓ Login successful")
        except:
            print("✗ Login failed")
            driver.save_screenshot("login_failed.png")
            print("✓ Screenshot saved as 'login_failed.png'")
            return
        
        print("Step 5: Opening account dropdown...")
        # Click account menu with overlay handling
        account_btn = driver.find_element(By.ID, "navbarAccount")
        click_with_fallback(driver, account_btn)
        time.sleep(2)
        
        # Remove any overlays that might have appeared
        remove_overlays(driver)
        time.sleep(1)
        
        print("\n=== ACCOUNT DROPDOWN CONTENTS ===")
        
        # Get all visible buttons after clicking account
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        visible_buttons = [btn for btn in all_buttons if btn.is_displayed() and btn.text.strip()]
        
        print(f"Found {len(visible_buttons)} visible buttons:")
        for i, btn in enumerate(visible_buttons):
            print(f"{i+1}. '{btn.text}'")
            
        # Save screenshot
        driver.save_screenshot("debug_result.png")
        print("\n✓ Screenshot saved as 'debug_result.png'")
        
    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("debug_error.png")
        print("✓ Error screenshot saved as 'debug_error.png'")
    finally:
        driver.quit()

if __name__ == "__main__":
    simple_debug()