import requests
import json
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

BASE_URL = "http://localhost:3000"

def extract_token_from_localstorage(driver):
    # try to find a JWT or token-like value from localStorage
    js = """
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
    return driver.execute_script(js)

def test_add_card_api_using_token_from_localstorage(driver, user):
    # ensure logged in via autouse fixture
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Logout') or contains(., 'Log out') or contains(., 'Sign out')]")))

    token = extract_token_from_localstorage(driver)
    assert token, "No auth token found in localStorage; open DevTools -> Application -> Local Storage to find the correct key."

    # common endpoint used by many Juice Shop versions; if this fails, inspect Network when adding card via UI and update
    endpoint = BASE_URL + "/api/PaymentMethods"

    payload = {
        "cardholder": "API User",
        "cardNumber": f"411111111111{random.randint(1000,9999)}",
        "expiryMonth": "12",
        "expiryYear": "2030",
        "cvc": "123"
    }

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    resp = requests.post(endpoint, json=payload, headers=headers)
    # accept 200/201/204 depending on API
    assert resp.status_code in (200, 201, 204), f"API call failed ({resp.status_code}): {resp.text}"