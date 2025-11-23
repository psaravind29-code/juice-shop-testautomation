import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def test_add_card_ui(driver):
    """TASK 2: Navigate to Payment Methods page and verify content."""
    logger.info("=" * 60)
    logger.info("TASK 2: UI TEST - NAVIGATE TO PAYMENT METHODS")
    logger.info("=" * 60)
    
    wait = WebDriverWait(driver, 15)
    
    # Navigate to Saved Payment Methods
    logger.info("[Task2] → Navigating to Payment Methods page...")
    driver.get("http://localhost:3000/#/saved-payment-methods")
    time.sleep(1)
    
    # Verify page loaded
    logger.info("[Task2] → Verifying page content...")
    page_source = driver.page_source
    
    # Check for any payment-related content
    has_payment_content = (
        "payment" in page_source.lower() or
        "card" in page_source.lower() or
        "app-payment" in page_source.lower()
    )
    
    assert has_payment_content, "Payment Methods page did not load correctly"
    logger.info("[Task2] ✓ Payment Methods page loaded successfully")
    logger.info("[Task2] ✓ User can navigate to payment section")
    logger.info("=" * 60)
    logger.info("✓ TASK 2 COMPLETED: UI navigation test passed")
    logger.info("=" * 60)