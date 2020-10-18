from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from constants import get_webdriver
import time
import re


class OglasiApi():
    def __init__(self, search_term, filters, base_url):
        self.driver = get_webdriver()
        self.base_url = base_url
        self.search_term = search_term
        self.filters = filters
        # url difference after adding price filters
        self.city_filter = '/grad/'
        self.price_filter = f"?pr%5Bs%5D={self.filters['min']}&pr%5Be%5D={self.filters['max']}&pr%5Bc%5D={self.filters['currency']}"
        self.page = 1

    def run(self):
        print('Starting script...')
        print(f'Looking for property in {self.search_term}...')
        self.driver.get(self.base_url)
        time.sleep(5)
        # couple not so important steps, keep them or not?
        nekretnine_button = self.driver.find_element_by_css_selector("div[class='tile red']")
        nekretnine_button.click()
        # nekretnine_button.send_keys(Keys.RETURN)
        time.sleep(5)
        izdavanje_nekretnina_button = self.driver.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/div/div/div/div/div[2]/a/h3')
        izdavanje_nekretnina_button.click()
        time.sleep(5)
        # lokacije_button = self.driver.find_element_by_xpath('/html/body/div[3]/div/aside/div[2]/div/button')
        # lokacije_button.click()
        # time.sleep(5)
        # textbox = self.driver.find_element_by_xpath('/html/body/div[6]/div/div/div/div[2]/div[3]/div/div[2]/div/form/div/div[1]/div/input')
        # time.sleep(2)
        # textbox.send_keys(self.search_term)
        # novi_sad_element = self.driver.find_element_by_css_selector("a[class='ng-binding ng-click-active']")
        # novi_sad_element.click()
        # time.sleep(5)
        # prikazi_button = self.driver.find_element_by_xpath('/html/body/div[6]/div/div/div/div[1]/div[2]/div[2]/div[1]/button[2]')
        # prikazi_button.click()
        # time.sleep(5)
        search_term_for_url = self.search_term.lower().replace(' ', '-')
        new_url = f"{self.driver.current_url}{self.city_filter}{search_term_for_url}"
        self.driver.get(new_url)
        time.sleep(3)
        price_filter_applied_url = f"{self.driver.current_url}{self.price_filter}"
        self.driver.get(price_filter_applied_url)
        time.sleep(5)
        all_property = []
        while True:
            print(f"Current URL: {self.driver.current_url}...")
            print(f"Current page is: {self.page}...")
            page_url = f"{self.driver.current_url}p={self.page}"
            time.sleep(5)
            property = self.get_page_data()
            all_property.append(property)
            self.driver.get(page_url)
            try:
                next_page_button = self.driver.find_element_by_xpath('/html/body/div[3]/div/div/nav/ul[1]/li[8]/a')
                next_page_button.click()
                time.sleep(5)
                self.page = self.page + 1
            except NoSuchElementException as e:
                print('No more pages...')
                break

            if self.page == 30:
                break

        self.driver.quit()
        return all_property


    def get_page_data(self):
        print('Getting links of property...')
        links = self.get_property_links()
        if not links:
            print('Script stopped...')
            return

        print(f"Got {len(links)} links of property from page {self.page}...")
        property_data = self.get_property_info(links)
        print(f"Got info of {len(property_data)} ads in {self.search_term}...")
        return property_data

    def get_property_links(self):
        links = []
        try:
            property_ads = self.driver.find_elements_by_css_selector("article[itemprop='itemListElement']")
        except NoSuchElementException as e:
            print('Couldn\'t acces to property ads...')

        try:
            for ad in property_ads:
                    link = ad.find_element_by_tag_name('a').get_attribute('href')
                    links.append(link)
        except Exception as e:
            print('Couldn\'t get product links...')

        return links

    def get_property_info(self, links):
        print('Getting ads data...')
        asins = self.get_asins(links)
        property_data = []
        for asin in asins:
            ad = self.get_data_of_one_ad(asin)
            if ad:
                property_data.append(ad)

        return property_data

    def get_data_of_one_ad(self, asin):
        print(f"Getting data of ad with unique code: {asin}")
        short_url = self.shorten_url(asin)
        self.driver.get(short_url)
        time.sleep(5)
        name = self.get_ad_name(asin)
        price = self.get_ad_price(asin)
        location = self.get_ad_location(asin)
        # room_numbers = self.get_room_numbers(asin)
        quadrature = self.get_quadrature(asin)
        advertiser_name = self.get_advertiser_name(asin)
        advertiser_number = self.get_advertiser_number(asin)
        date = self.get_date(asin)
        # if name and price and location and room_numbers and quadrature and advertiser_name and advertiser_number and date:
        ad_info = f"{short_url}, {name}, {price}, {location}, {quadrature}, {advertiser_name}, {advertiser_number}, {date}, \n"
        return ad_info

        # return None

    def get_ad_name(self, asin):
        try:
            return  self.driver.find_element_by_css_selector("h1[class='fpogl-title text-primary']").text.strip().replace(',', ' ')
        except NoSuchElementException:
            print(f"Couldn\'t get name of ad with code: {asin}")
            print(f"Ad URL is - {self.driver.current_url}")
            return ""

    def get_ad_price(self, asin):
        try:
            return self.driver.find_element_by_css_selector("span[itemprop='price']").text.strip().replace(',', '.')
        except NoSuchElementException:
            print(f"Couldn\'t get price of ad with code: {asin}")
            print(f"Ad URL is - {self.driver.current_url}")
            return ""

    def get_ad_location(self, asin):
        try:
            return self.driver.find_element_by_css_selector("td[style='vertical-align: top;padding-left:16px']").text.strip().replace(',', ' ')
        except NoSuchElementException:
            print(f"Couldn\'t get location of ad with code: {asin}")
            print(f"Ad URL is - {self.driver.current_url}")
            return ""

    # def get_room_numbers(self, asin):
    #     try:
    #         element = self.driver.find_element_by_css_selector("td[style='vertical-align: top;padding-left:16px']")
    #         print(element.find_element_by_tag_name('a').get_attribute('href').text.strip().replace(',', ' ')
    #     except NoSuchElementException as e:
    #         print(f"Couldn\'t get room numbers of ad with code: {asin}")
    #         print(f"Ad URL is - {self.driver.current_url}")
    #         print(e)

    def get_quadrature(self, asin):
        try:
            return self.driver.find_element_by_css_selector("td[style='vertical-align: top;padding-left:16px']").text.strip().replace(',', '.')
        except NoSuchElementException:
            print(f"Couldn\'t get quadrature of ad with code: {asin}")
            print(f"Ad URL is - {self.driver.current_url}")
            return ""

    def get_advertiser_name(self, asin):
        try:
            return self.driver.find_element_by_css_selector("div[style='display:inline-block']").text.strip().replace(',', ' ')
        except NoSuchElementException:
            print(f"Couldn\'t get advertiser name of ad with code: {asin}")
            print(f"Ad URL is - {self.driver.current_url}")
            return ""

    def get_advertiser_number(self, asin):
        try:
            return self.driver.find_element_by_css_selector("a[href^='tel:']").text.strip()
        except NoSuchElementException:
            print(f"Couldn\'t get advertiser number of ad with code: {asin}")
            print(f"Ad URL is - {self.driver.current_url}")
            return ""

    def get_date(self, asin):
        try:
            return self.driver.find_element_by_xpath('/html/body/div[2]/div/div/section/article/div[2]/div[1]/time').text.strip()
        except NoSuchElementException as e:
            print(f"Couldn\'t get date when ad with code:  {asin} was published")
            print(f"Ad URL is - {self.driver.current_url}")
            print(e)
            return ""

    def get_asins(self, links):
        return [self.get_asin(link) for link in links]

    def get_asin(self, link):
        asin_regex = re.compile(r'\d\d-\d\d\d\d\d\d\d')
        m = asin_regex.search(link)
        if m:
            return m.group()

        elif m == None:
            asin_regex = re.compile(r'\d\d-\d\d\d\d\d\d')
            m = asin_regex.search(link)
            if m:
                return m.group()

    def shorten_url(self, asin):
        return f"{self.base_url}/oglasi/nekretnine/{asin}/"
