# visual_debug.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

BASE_URL = "http://localhost:3000"

def visual_debug():
    # Run in visible mode so you can see what's happening
    opts = Options()
    # Remove headless to see the browser
    # opts.add_argument("--headless=new")  
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1200,800")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    
    try:
        # Load user
        with open('tests/new-user.json', 'r') as f:
            user = json.load(f)
        
        print("=== VISUAL DEBUG - Watch the browser ===")
        print("You should see the browser open and navigate...")
        
        # Login
        driver.get(f"{BASE_URL}/#/login")
        time.sleep(3)  # Longer wait for visual
        
        print("Browser should be on login page. Press Enter to continue...")
        input()
        
        # Fill credentials
        driver.find_element(By.ID, "email").send_keys(user["email"])
        driver.find_element(By.ID, "password").send_keys(user["password"])
        
        # Remove overlays
        driver.execute_script("""
        document.querySelectorAll('.cdk-overlay-backdrop, .cdk-overlay-container').forEach(el => el.remove());
        """)
        
        # Click login
        driver.find_element(By.ID, "loginButton").click()
        time.sleep(3)
        
        print("Should be logged in. Press Enter to open account menu...")
        input()
        
        # Click account
        driver.find_element(By.ID, "navbarAccount").click()
        time.sleep(2)
        
        print("Account menu should be open. Look at the dropdown in the browser.")
        print("What menu items do you see?")
        print("Press Enter to capture the contents...")
        input()
        
        # Capture what's visible
        buttons = driver.find_elements(By.TAG_NAME, "button")
        visible_buttons = [btn for btn in buttons if btn.is_displayed() and btn.text.strip()]
        
        print(f"\nFound {len(visible_buttons)} visible buttons:")
        for i, btn in enumerate(visible_buttons):
            print(f"{i+1}. '{btn.text}'")
            
        print("\nLook at the browser and tell me which button leads to Payments.")
        print("Press Enter to close...")
        input()
        
    finally:
        driver.quit()

if __name__ == "__main__":
    visual_debug()