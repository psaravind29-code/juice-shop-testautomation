import requests
import uuid
import logging

logger = logging.getLogger(__name__)
BASE_URL = "http://localhost:3000"

def test_add_card_api(driver, user):
    logger.info("=== TASK 3: ADD UNIQUE CARD VIA API ===")

    # Get auth token from localStorage (Juice Shop uses JWT)
    token = driver.execute_script("return localStorage.getItem('token') || sessionStorage.getItem('token');")
    assert token, "No token found! Login failed?"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    unique_card = f"545301{str(uuid.uuid4().int)[:8]}0002"[:16]

    payload = {
        "fullName": "API Test User",
        "cardNumber": unique_card,
        "expiryMonth": "12",
        "expiryYear": "2099"
    }

    response = requests.post(f"{BASE_URL}/api/Cards", json=payload, headers=headers)
    assert response.status_code == 201, f"API Failed: {response.text}"

    logger.info(f"UNIQUE CARD ADDED VIA API: {unique_card}")
    logger.info("TASK 3 COMPLETED SUCCESSFULLY")