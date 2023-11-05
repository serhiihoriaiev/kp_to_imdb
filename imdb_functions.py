import time
import json
import pickle
import os
import credentials

from kp_functions import init_driver
from timeit import default_timer as timer
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
        logoff_imdb(wait)

    return nickname == nickname_elem.text

def logoff_imdb(wait):
    menu_elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.nav__userMenu')))
    menu_elem.click()
    
    time.sleep(2)
    signout_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.imdb-header-account-menu__sign-out')))
    signout_button.click()

    wait.until(EC.visibility_of_element_located((By.XPATH, '//span[text()="Sign In"]')))

def unpack_item_file(items_file):
    """
    This function finds and returns URLs for IMDB items listed in items_file 
    """
    with open(items_file, 'r', encoding='UTF-8') as items_f:
        items = items_f.read()

    items = items.split(',\n')

    try:
        items.remove('')
    except ValueError:
        pass

    items = [json.loads(item.strip()) for item in items]
    return items

def locate_item(driver, wait, item):
    """
    This function searches for an item and opens it's page
    """
    name = item['name'] if item['name'] else item['ru_name']

    search_field = driver.find_element(By.ID, 'suggestion-search')
    search_field.send_keys(name + ' ' + item['year'])
    search_field.send_keys(Keys.ENTER)

    match = driver.find_element(By.CSS_SELECTOR, 'a.ipc-metadata-list-summary-item__t')
    if match.text.strip() != name:
        try:
            exact_match_button = driver.find_element(By.CSS_SELECTOR, 'a.results-section-exact-match-btn')
        except NoSuchElementException:
            return False
        exact_match_button.click()
        match = driver.find_element(By.CSS_SELECTOR, 'a.ipc-metadata-list-summary-item__t')    
    match.click()
    return True


def add_to_watchlist(driver, wait, items):
    """
    This function adds an item to watchlist if it's not there yet
    """
    result = []
    for item in items:
        if not locate_item(driver, wait, item):
            item['watchlisted'] = False
            result.append(item)
            continue
        
        watchlist_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.ipc-watchlist-ribbon__icon')))
        time.sleep(1)
        try:
            check_if_in_watchlist = driver.find_element(By.CSS_SELECTOR, '.ipc-watchlist-ribbon--inWatchlist.hero-media__watchlist')
        except NoSuchElementException:
            watchlist_button.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ipc-watchlist-ribbon--inWatchlist.hero-media__watchlist')))
            
        item['watchlisted'] = True
        result.append(item)
        
    return result


if __name__ == '__main__':
    start = timer()
    driver, wait = init_driver()
    # driver, wait = 0, 0
    items_to_watchlist = unpack_item_file('short_watchlist.txt')
    logon_imdb(driver, wait, credentials.imdb_email, credentials.imdb_password, credentials.imdb_nickname)
    watchlisted = add_to_watchlist(driver, wait, items_to_watchlist)

    with open('watchlist_result.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(watchlisted))

    logoff_imdb(wait)

    end = timer()
    print(f'Script lasted for {round(end-start, 1)} seconds')