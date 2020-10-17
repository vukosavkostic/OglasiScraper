from selenium import webdriver

DIRECTORY = 'OglasiScrapper'
SEARCH_TERM = 'Novi Sad'
MIN_PRICE = 0
MAX_PRICE = 300
CURRENCY = 'EUR'
BASE_URL = 'https://www.oglasi.rs/'
FILTERS = {
    'min': MIN_PRICE,
    'max': MAX_PRICE,
    'currency': CURRENCY
}

def get_webdriver():
    return webdriver.Chrome('/home/vuko/Desktop/Python/drivers/chromedriver')
