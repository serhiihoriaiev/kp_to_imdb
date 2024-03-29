import time
import json
import credentials

from kp_functions import init_driver
from timeit import default_timer as timer
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def logon_imdb(driver, wait, email, password, nickname):
    """
    Logs into IMDB website and navigates to it's main page.
    """
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
    """
    Logs off the IMDB website
    """
    menu_elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.nav__userMenu')))
    menu_elem.click()
    
    time.sleep(2)
    signout_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.imdb-header-account-menu__sign-out')))
    signout_button.click()

    wait.until(EC.visibility_of_element_located((By.XPATH, '//span[text()="Sign In"]')))


def run_watchlist_adding(input_file='parsed_watchlist.txt'):
    """
    Runs IMDB watchlist adding routine for items from the input_file
    """
    driver, wait = init_driver()
    items_to_watchlist = unpack_item_file(input_file)
    logon_imdb(driver, wait, credentials.imdb_email, credentials.imdb_password, credentials.imdb_nickname)
    for item in items_to_watchlist:
        watchlisted = add_to_watchlist(driver, wait, item)

        with open('watchlist_result.txt', 'a', encoding='utf-8') as f:
            f.write(json.dumps(watchlisted) + ',\n')

    logoff_imdb(wait)


def run_rating(input_file='parsed_ratings.txt'):
    """
    Runs IMDB rating routine for items from the input_file
    """
    driver, wait = init_driver()
    items_to_rate = unpack_item_file(input_file)
    logon_imdb(driver, wait, credentials.imdb_email, credentials.imdb_password, credentials.imdb_nickname)
    for item in items_to_rate:
        rated = rate_item(driver, wait, item)

        with open('rate_result.txt', 'a', encoding='utf-8') as f:
            f.write(json.dumps(rated) + ',\n')

    logoff_imdb(wait)


def unpack_item_file(items_file):
    """
    Converts parsed content from file into list of dicts, where every dict is an IMDB item
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


def locate_item(driver,item):
    """
    This function searches for an item and opens its page
    """
    name = item['name'] if item['name'] else item['ru_name']

    search_field = driver.find_element(By.ID, 'suggestion-search')
    search_field.send_keys(name + ' ' + item['year'])
    search_field.send_keys(Keys.ENTER)

    try:  # for cases when captcha shows up 
        match = driver.find_element(By.CSS_SELECTOR, 'a.ipc-metadata-list-summary-item__t')
    except NoSuchElementException:
        if 'No results found for' in driver.page_source:
            return False
        match = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.ipc-metadata-list-summary-item__t')))

    if match.text.strip() != name:
        try:
            exact_match_button = driver.find_element(By.CSS_SELECTOR, 'a.results-section-exact-match-btn')
        except NoSuchElementException:
            return False
        exact_match_button.click()
        match = driver.find_element(By.CSS_SELECTOR, 'a.ipc-metadata-list-summary-item__t')    
    match.click()
    return True


def add_to_watchlist(driver, wait, item):
    """
    This function adds an item to watchlist if it's not there yet
    """
    if not locate_item(driver, item):
        item['watchlisted'] = False
        return item

    try:
        # if it's already rated, no need adding it to watchlist
        rate_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button.ipc-btn')))
    except TimeoutException:
        with open("last_page.html", "w") as html_file:
            html_file.write(driver.page_source)
        raise TimeoutException
    
    time.sleep(1)
    if rate_button.text != 'Rate':
        item['watchlisted'] = False
        item['rated'] = True
        return item
    
    watchlist_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.ipc-watchlist-ribbon__icon')))
    # time.sleep(2)
    try:
        check_if_in_watchlist = driver.find_element(By.CSS_SELECTOR, '.ipc-watchlist-ribbon--inWatchlist.hero-media__watchlist')
    except NoSuchElementException:
        watchlist_button.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ipc-watchlist-ribbon--inWatchlist.hero-media__watchlist')))
        
    item['watchlisted'] = True
        
    return item

def rate_item(driver, wait, item):
    """
    This function rates an item if it's not rated yet
    """
    if not locate_item(driver, item):
        item['rated'] = False
        return item

    rate_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button.ipc-btn')))
    time.sleep(2)

    if rate_button.text == 'Rate':
        rate_button.click()
        rating_star = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Rate ' + item['rating'] + '"]')))
        a = ActionChains(driver)
        a.move_to_element(rating_star).click().perform()

        confirm_button = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ipc-rating-prompt__rate-button')))
        confirm_button.click()
        time.sleep(1)
        
    item['rated'] = True
    return item


def list_unsuccessful(job_type):
    """
    job_type: str, may only be 'ratings' or 'watchlist'
    
    This is auxiliary function meant to be used when this script file is run as main.
    Takes result files (some kind of logs that is documented along the way of main functions)
    and returns list of items which weren't rated or watchlisted.
    """
    if job_type == 'ratings':
        file_name = 'rate_result.txt'
        key = 'rated'
    elif job_type == 'watchlist':
        file_name = 'watchlist_result.txt'
        key = 'watchlisted'

    items_to_parse = unpack_item_file(file_name)
    result = [item for item in items_to_parse if item[key] is False]

    for item in result:
        if job_type == 'ratings':
            print(item['name'], item['year'], item['rating'], sep=', ')
        elif job_type == 'watchlist':
            print(item['name'], item['year'], sep=', ')


if __name__ == '__main__':
    list_unsuccessful('ratings')