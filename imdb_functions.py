import time
import pickle
import os
import credentials

from kp_functions import init_driver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def logon_imdb(driver, wait, email, password, nickname):
    driver.get('https://www.imdb.com/registration/signin')

    signin_button = driver.find_element(By.XPATH, '//span[text()="Sign in with IMDb"]')
    signin_button.click()

    login_field = driver.find_element(By.ID, 'ap_email')
    login_field.send_keys(email)

    pass_field = driver.find_element(By.ID, 'ap_password')
    pass_field.send_keys(password)
    pass_field.send_keys(Keys.ENTER)

    try:
        nickname_elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.imdb-header__account-toggle--logged-in')))
    except TimeoutException:
        print('Timeout')
        logoff_imdb(driver, wait)

    return nickname == nickname_elem.text

def logoff_imdb(driver, wait):
    menu_elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.nav__userMenu')))
    menu_elem.click()
    
    time.sleep(2)
    signout_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.imdb-header-account-menu__sign-out')))
    signout_button.click()

    wait.until(EC.visibility_of_element_located((By.XPATH, '//span[text()="Sign In"]')))


if __name__ == '__main__':
    driver, wait = init_driver()
    logon_imdb(driver, wait, credentials.imdb_email, credentials.imdb_password, credentials.imdb_nickname)
    logoff_imdb(driver, wait)