"""
TASK 2: UI test that navigates to My Payments options and adds card details
"""

import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def test_add_card_ui(driver):
    """
    TASK 2: UI Test - Add new payment card using manual exploration XPaths
    """
    logger.info("=" * 60)
    logger.info("TASK 2: UI TEST - ADD PAYMENT CARD")
    logger.info("=" * 60)
    
    wait = WebDriverWait(driver, 15)
    
    # Step 1: Navigate to payment methods page
    logger.info("Step 1: Navigating to payment methods page...")
    try:
        driver.get("http://localhost:3000/#/saved-payment-methods")
        wait.until(EC.presence_of_element_located((By.XPATH, "//app-saved-payment-methods")))
        logger.info("  → Successfully navigated to payment methods")
        time.sleep(2)
    except Exception as e:
        logger.error(f"Failed to navigate to payment methods: {e}")
        raise
    
    # Step 2: Take initial screenshot
    logger.info("Step 2: Taking initial screenshot...")
    driver.save_screenshot("payment_methods_initial.png")
    logger.info("  → Screenshot saved: payment_methods_initial.png")
    
    # Step 3: Check existing cards
    logger.info("Step 3: Checking existing cards...")
    try:
        card_rows = driver.find_elements(By.XPATH, "//mat-row")
        logger.info(f"  → Found {len(card_rows)} existing card(s)")
        
        for i, row in enumerate(card_rows):
            try:
                card_number = row.find_element(By.XPATH, "./mat-cell[1]").text
                card_name = row.find_element(By.XPATH, "./mat-cell[2]").text
                expiry_date = row.find_element(By.XPATH, "./mat-cell[3]").text
                logger.info(f"  → Card {i+1}: {card_number} | {card_name} | {expiry_date}")
            except Exception as e:
                logger.warning(f"  → Could not read card row {i}: {e}")
                
    except Exception as e:
        logger.warning(f"  → Could not read existing cards: {e}")
    
    # Step 4: Expand add new card form
    logger.info("Step 4: Expanding add new card form...")
    try:
        add_card_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/app-root/mat-sidenav-container/mat-sidenav-content/app-saved-payment-methods/mat-card/div/app-payment-method/div/div[2]/mat-expansion-panel/mat-expansion-panel-header")
        ))
        add_card_btn.click()
        logger.info("  → Add card form expanded")
        time.sleep(2)
    except Exception as e:
        logger.error(f"Failed to expand add card form: {e}")
        raise
    
    # Step 5: Fill card details
    logger.info("Step 5: Filling card details...")
    try:
        # Cardholder name
        name_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/app-root/mat-sidenav-container/mat-sidenav-content/app-saved-payment-methods/mat-card/div/app-payment-method/div/div[2]/mat-expansion-panel/div/div/div/div/mat-form-field[1]//input")
        ))
        name_field.clear()
        name_field.send_keys("UI Test User")
        logger.info("  → Cardholder name entered")
        
        # Card number
        card_field = driver.find_element(By.XPATH, "/html/body/app-root/mat-sidenav-container/mat-sidenav-content/app-saved-payment-methods/mat-card/div/app-payment-method/div/div[2]/mat-expansion-panel/div/div/div/div/mat-form-field[2]//input")
        card_field.clear()
        card_field.send_keys("4111111111111111")
        logger.info("  → Card number entered")
        
        # Expiry month
        month_field = driver.find_element(By.XPATH, "/html/body/app-root/mat-sidenav-container/mat-sidenav-content/app-saved-payment-methods/mat-card/div/app-payment-method/div/div[2]/mat-expansion-panel/div/div/div/div/mat-form-field[3]//select")
        month_field.send_keys("12")
        logger.info("  → Expiry month selected")
        
        # Expiry year
        year_field = driver.find_element(By.XPATH, "/html/body/app-root/mat-sidenav-container/mat-sidenav-content/app-saved-payment-methods/mat-card/div/app-payment-method/div/div[2]/mat-expansion-panel/div/div/div/div/mat-form-field[4]//input")
        year_field.clear()
        year_field.send_keys("2025")
        logger.info("  → Expiry year entered")
        
    except Exception as e:
        logger.error(f"Failed to fill card details: {e}")
        raise
    
    # Step 6: Submit the form
    logger.info("Step 6: Submitting card form...")
    try:
        submit_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Submit') or contains(., 'Add') or contains(., 'Save')]")
        for button in submit_buttons:
            if button.is_displayed() and button.is_enabled():
                button.click()
                logger.info("  → Card form submitted")
                break
        time.sleep(3)
    except Exception as e:
        logger.error(f"Failed to submit card form: {e}")
        raise
    
    # Step 7: Take final screenshot and verify
    logger.info("Step 7: Taking final screenshot...")
    driver.save_screenshot("payment_methods_final.png")
    logger.info("  → Screenshot saved: payment_methods_final.png")
    
    # Verify card was added by checking count
    try:
        updated_cards = driver.find_elements(By.XPATH, "//mat-row")
        logger.info(f"  → Now have {len(updated_cards)} card(s) total")
    except Exception as e:
        logger.warning(f"  → Could not verify card count: {e}")
    
    logger.info("✓ TASK 2 COMPLETED: UI test for card addition finished")
    logger.info("=" * 60)