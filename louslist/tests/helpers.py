from selenium import webdriver
from selenium.webdriver.common.by import By

def search(driver: webdriver, term: str):
    search_input = driver.find_element(By.XPATH, "/html/body/nav/form/input")
    search_input.send_keys(term)
    search_button = driver.find_element(By.XPATH, "/html/body/nav/form/button")
    search_button.click()