from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    EMAIL_INPUT = (By.ID, 'email')  # Stable ID locator
    PASSWORD_INPUT = (By.ID, 'password')
    LOGIN_BUTTON = (By.ID, 'loginButton')
    ACCOUNT_MENU = (By.CSS_SELECTOR, '[aria-label="Show/hide account menu"]')  # Stable aria-label

    def login(self, email, password):
        self.click(*self.ACCOUNT_MENU)  # Open menu if needed
        self.click(By.LINK_TEXT, 'Login')  # Navigate to login
        self.send_keys(*self.EMAIL_INPUT, email)
        self.send_keys(*self.PASSWORD_INPUT, password)
        self.click(*self.LOGIN_BUTTON)