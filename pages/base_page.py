from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)  # Explicit wait for stability

    def open_url(self, url):
        self.driver.get(url)

    def find_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))  # Stable wait

    def click(self, by, value):
        elem = self.find_element(by, value)
        elem.click()

    def send_keys(self, by, value, text):
        elem = self.find_element(by, value)
        elem.send_keys(text)