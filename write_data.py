import csv
from scrapper import OglasiApi
from datetime import date
from constants import(
    get_webdriver,
    DIRECTORY,
    SEARCH_TERM,
    MIN_PRICE,
    MAX_PRICE,
    CURRENCY,
    BASE_URL,
    FILTERS
)

def write_to_file(file, data):
    print('Writing data to a file...')
    for page in data:
        for ad in page:
            file.write(ad)

def convert_to_eur_date(year, month, day):
    return f"{day}-{month}-{year}"

# constants
HEADERS = 'url, ad_name, price, location, quadrature, room_number, advertiser_name, advertiser_number, date\n'
YEAR = date.today().year
MONTH = date.today().month
DAY = date.today().day
FILE_NAME = f"oglasi-{convert_to_eur_date(YEAR, MONTH, DAY)}.csv"

# initializing objects and running script
oglasi = OglasiApi(SEARCH_TERM, FILTERS, BASE_URL)
property = oglasi.run()

# working with files
file = open(FILE_NAME, 'w')
file.write(HEADERS)

write_to_file(file, property)
