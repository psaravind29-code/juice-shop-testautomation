from selenium.webdriver.common.by import By
from .base_page import BasePage

class PaymentsPage(BasePage):
    ADD_CARD_BUTTON = (By.CSS_SELECTOR, 'button#addNewCard')  # Inspect for stable selector
    NAME_INPUT = (By.ID, 'name')
    CARD_NUMBER_INPUT = (By.ID, 'cardNumber')
    EXPIRY_MONTH_SELECT = (By.ID, 'expiryMonth')
    EXPIRY_YEAR_SELECT = (By.ID, 'expiryYear')
    SUBMIT_BUTTON = (By.ID, 'submitButton')

    def add_card(self, name, card_num, exp_month, exp_year):
        self.click(*self.ADD_CARD_BUTTON)
        self.send_keys(*self.NAME_INPUT, name)
        self.send_keys(*self.CARD_NUMBER_INPUT, card_num)
        self.find_element(*self.EXPIRY_MONTH_SELECT).send_keys(exp_month)  # Or select option
        self.find_element(*self.EXPIRY_YEAR_SELECT).send_keys(exp_year)
        self.click(*self.SUBMIT_BUTTON)
        # Add verification: e.g., wait for success message
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.confirmation')))  # Example