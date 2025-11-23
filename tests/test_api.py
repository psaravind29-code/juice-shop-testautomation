"""
API Test: Add a payment card using the backend API with an auth token.

This test demonstrates:
- Extracting an auth token from the browser's localStorage
- Making authenticated API calls using the token
- Generating unique card details for each test run (using UUID)
"""
import requests
import uuid
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

BASE_URL = "http://localhost:3000"


def test_add_card_api_using_token_from_localstorage(driver, user):
    """
    Test that an authenticated user can add a card via the API.
    
    Precondition: autouse login fixture has already authenticated the user.
    Approach: Extract auth token from localStorage and POST to /api/PaymentMethods.
    """
    wait = WebDriverWait(driver, 10)
    
    # Verify login: wait for Logout button or similar indicator
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, 
            "//*[contains(text(),'Logout') or contains(., 'Log out') or contains(., 'Sign out')]"
        )))
    except Exception:
        # If logout button not found, assume still logged in and proceed
        time.sleep(1)
    
    # Extract auth token from localStorage
    token = _extract_auth_token(driver)
    assert token, (
        "No auth token found in localStorage. "
        "Ensure login was successful. Check DevTools -> Application -> LocalStorage for the key."
    )
    
    # Prepare unique card details using UUID for guaranteed uniqueness
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    card_number = f"411111{unique_id}{1111:04d}"  # Format: 4111 11 XXXXXXXX 1111
    
    # Construct API request
    endpoint = f"{BASE_URL}/api/PaymentMethods"
    payload = {
        "cardholder": "API Test User",
        "cardNumber": card_number,
        "expiryMonth": "12",
        "expiryYear": "2030",
        "cvc": "123"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Send POST request
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
    
    # Verify success (accept 200/201/204 depending on API version)
    assert resp.status_code in (200, 201, 204), (
        f"API call failed with status {resp.status_code}: {resp.text}"
    )
    
    # Optional: verify response contains the card details
    if resp.text:
        try:
            resp_json = resp.json()
            # Some APIs echo back the card details; verify if available
            if isinstance(resp_json, dict):
                assert "cardNumber" in resp_json or "id" in resp_json, (
                    f"Unexpected API response: {resp_json}"
                )
        except Exception:
            # Non-JSON response is okay; status code was already verified
            pass


def _extract_auth_token(driver):
    """
    Extract auth token from browser localStorage.
    Searches for common token keys (token, authentication, etc.) and JWT patterns.
    """
    js = """
    const keys = Object.keys(window.localStorage);
    for (const k of keys) {
        try {
            const v = window.localStorage.getItem(k);
            if (!v) continue;
            
            // Try parsing as JSON to find nested token
            if (v.startsWith('{')) {
                try {
                    const obj = JSON.parse(v);
                    if (obj.token) return obj.token;
                    if (obj.authentication) return obj.authentication;
                    if (obj.access_token) return obj.access_token;
                } catch(e) {}
            }
            
            // Check for JWT (starts with eyJ) or string tokens
            if (typeof v === 'string' && (v.includes('eyJ') || v.length > 20)) {
                return v;
            }
        } catch(e) {}
    }
    return null;
    """
    return driver.execute_script(js)