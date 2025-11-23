"""
Diagnostic script to verify test setup.
Run this to check:
1. Is Juice Shop running?
2. Can we log in with the test credentials?
3. Can we navigate to Payment Methods?
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:3000"
EMAIL = "aravindps987@gmail.com"
PASSWORD = "cat@123"

def main():
    print("Starting diagnostic...")
    
    # Set up Chrome
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--remote-allow-origins=*")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_window_size(1280, 900)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Step 1: Can we reach Juice Shop?
        print(f"\n1. Checking if Juice Shop is running at {BASE_URL}...")
        driver.get(BASE_URL)
        title = driver.title
        print(f"   ✓ Juice Shop is running (title: '{title}')")
        
        # Remove overlays immediately
        print(f"\n1b. Removing overlays...")
        driver.execute_script("""
        const selectors = ['.cdk-overlay-backdrop', '.cdk-overlay-backdrop-showing', '.mat-mdc-dialog-surface', '.overlay'];
        selectors.forEach(s => { document.querySelectorAll(s).forEach(n => n.remove()); });
        """)
        time.sleep(1)
        print(f"   ✓ Overlays removed")
        
        # Step 2: Try to log in with test credentials
        print(f"\n2. Attempting login with {EMAIL} / {PASSWORD}...")
        
        # Click account menu
        acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
        try:
            acct_btn.click()
        except Exception:
            # JS click fallback
            driver.execute_script("arguments[0].click();", acct_btn)
        time.sleep(1)
        
        # Click login
        try:
            login_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarLoginButton")))
            login_btn.click()
            time.sleep(1)
        except Exception as e:
            print(f"   ✗ Could not find login button: {e}")
            driver.quit()
            return
        
        # Fill email and password
        try:
            email_field = wait.until(EC.visibility_of_element_located((By.ID, "email")))
            email_field.send_keys(EMAIL)
            
            pwd_field = driver.find_element(By.ID, "password")
            pwd_field.send_keys(PASSWORD)
            
            # Submit
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            driver.execute_script("arguments[0].click();", submit_btn)  # JS click to avoid overlays
            time.sleep(2)
            print(f"   ✓ Login form submitted")
        except Exception as e:
            print(f"   ✗ Could not fill/submit login form: {e}")
            driver.quit()
            return
        
        # Step 3: Verify login success
        print(f"\n3. Checking if login was successful...")
        try:
            logout_btn = wait.until(EC.presence_of_element_located((By.XPATH, 
                "//*[contains(text(),'Logout') or contains(text(),'Log out')]"
            )))
            print(f"   ✓ Login successful! Found Logout button")
        except Exception as e:
            print(f"   ✗ Login may have failed (no Logout button found): {e}")
            print(f"   → This likely means the user account '{EMAIL}' does not exist in Juice Shop")
            print(f"   → Solution: Manually register this user in Juice Shop via the web UI")
            driver.quit()
            return
        
        # Step 4: Try to navigate to Payment Methods
        print(f"\n4. Navigating to Payment Methods...")
        acct_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarAccount")))
        acct_btn.click()
        time.sleep(1)
        
        try:
            pm_link = wait.until(EC.element_to_be_clickable((By.XPATH,
                "//*[contains(text(),'Payment Methods') or contains(text(),'Payments') or contains(text(),'My Payments')]"
            )))
            pm_link.click()
            time.sleep(1)
            print(f"   ✓ Successfully navigated to Payment Methods")
        except Exception as e:
            print(f"   ✗ Could not find Payment Methods link: {e}")
            print(f"   → This might mean: (a) account menu structure is different, or (b) user not logged in")
            driver.quit()
            return
        
        print(f"\n✓ All checks passed! Test setup is working.")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    finally:
        driver.quit()
        print("\nDone.")

if __name__ == "__main__":
    main()
