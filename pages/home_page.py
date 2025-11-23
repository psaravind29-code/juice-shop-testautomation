from selenium.webdriver.common.by import By
from .base_page import BasePage

class HomePage(BasePage):
    ACCOUNT_MENU = (By.CSS_SELECTOR, '[aria-label="Show/hide account menu"]')
    MY_PAYMENTS_LINK = (By.ID, 'navbarPaymentMethods')  # Stable ID if available; inspect app

    def navigate_to_payments(self):
        self.click(*self.ACCOUNT_MENU)
        self.click(*self.MY_PAYMENTS_LINK)