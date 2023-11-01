import time
import pickle
import os
import credentials

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

fake_login = 'dingo1'
fake_password = 'hftdw442C' 

def init_driver():
    driver = webdriver.Chrome(service=Service(os.path.join(os.getcwd(), 'chromedriver.exe')))
    wait = WebDriverWait(driver, 30)
    return driver, wait

def logon_kp(driver, wait, login, password, nickname):
    driver.get('https://www.kinopoisk.ru/')

    if 'Я не робот' in driver.page_source:
        time.sleep(60)
    
    login_button = driver.find_element(By.CLASS_NAME, 'styles_loginButton__LWZQp')
    login_button.click()
    wait.until(lambda driver: 'passport.yandex.ru/auth' in driver.current_url)
    
    login_field = driver.find_element(By.ID, 'passp-field-login')
    login_field.send_keys(login)
    login_field.send_keys(Keys.ENTER)

    pass_field = wait.until(EC.presence_of_element_located((By.ID, 'passp-field-passwd'))) 
    pass_field.send_keys(password)
    pass_field.send_keys(Keys.ENTER)

    a = ActionChains(driver)
    avatar_elem =  wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class^="styles_avatar"]')))
    a.move_to_element(avatar_elem).perform()

    nickname_elem = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'styles_primaryTitleDefaultAccount__a0_6V')))

    return nickname == nickname_elem.text


def get_wishlist_html(driver):
    result = []
    while(True):
        film_list = driver.find_element(By.ID, 'itemList')
        result.append(film_list.get_attribute('innerHTML'))
        try:
            next_page_link = driver.find_element(By.XPATH, '//a[text()="»"]')
            next_page_link.click()
        except NoSuchElementException:
            return result
        
def get_ratings_html(driver):
    result = []
    while(True):
        film_list = driver.find_element(By.CLASS_NAME, 'profileFilmsList')
        result.append(film_list.get_attribute('innerHTML'))
        try:
            next_page_link = driver.find_element(By.XPATH, '//a[text()="»"]')
            next_page_link.click()
        except NoSuchElementException:
            return result    
        
        
def load_wishlist():
    driver, wait = init_driver()
    logon_kp(driver, wait, credentials.login, credentials.password, credentials.nickname)

    driver.get('https://www.kinopoisk.ru/mykp/movies/')
    num_select = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'per_page')))  # navigator_per_page
    num_select = Select(num_select)   
    num_select.select_by_value('200') 

    wishlist_html = get_wishlist_html(driver)
    pickle.dump(wishlist_html, open("wishlist_html.p", 'wb'))

    time.sleep(5)
    driver.close()


def load_ratings():
    driver, wait = init_driver()
    logon_kp(driver, wait, credentials.login, credentials.password, credentials.nickname)

    ratings_button = driver.find_element(By.XPATH, '//a[text()="Оценки"]')
    ratings_button.click()

    num_select = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'navigator_per_page')))
    num_select = Select(num_select)   
    num_select.select_by_value('200')

    ratings_html = get_ratings_html(driver)
    pickle.dump(ratings_html, open("ratings_html.p", 'wb'))

    time.sleep(5)
    driver.close()