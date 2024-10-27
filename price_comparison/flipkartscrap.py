from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import urllib
import json
import re

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

class FlipkartScraper:
    DRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'

    def __init__(self):

        options = webdriver.ChromeOptions()


        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value,OperatingSystem.LINUX.value]
        user_agent_rotator = UserAgent(software_names=software_names,operating_systems=operating_systems,limit=100)
        user_agent = user_agent_rotator.get_random_user_agent()

        
        options.add_argument ("--headless=new")
        options.add_argument ('--no-sandbox')
        options.add_argument ('--window-size=1420,1080')
        options.add_argument ('--disable-gpu')
        options.add_argument (f'user-agent={user_agent}')

        s = Service(self.DRIVER_PATH)

        try:
            # Initialize Chrome with the specified options
            self.driver = webdriver.Chrome(service=s,options=options)
        except:
            pass

    def start_scraping(self,keyword):
        self.driver.get("https://www.flipkart.com/")
        self.wait = WebDriverWait(self.driver, 10)
        return self.search_products(keyword)
        

    def search_products(self, keyword):
        search_box = self.driver.find_element(By.CLASS_NAME, 'Pke_EE')
        # type the keyword in searchbox
        search_box.send_keys(keyword)
        # create WebElement for a search button
        
        search_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "_2iLD__")))
        # click search_button
        search_button.click()
        # wait for the page to download
        self.driver.implicitly_wait(5)
        #print(self.driver.page_source)

        available_pages = self.get_available_pages()
    

        # parsed_url = urllib.parse.urlparse(self.driver.current_url)
        # query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
        # crid = query_params.get('crid', None)
        # sprefix = query_params.get('sprefix', None)

        product_urls = self.extract_product_urls(keyword,available_pages)

        all_product_data = []
        for product_url in product_urls:
            output = self.parse_product_data(product_url)
            all_product_data.extend(output)
        
        self.driver.quit()
        # Write data to a JSON file
        return all_product_data

    def get_available_pages(self):
        available_pages = []
        # pagination_elements = self.wait.until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "*[class^='s-pagination-item'][not(contains(@class, 's-pagination-separator'))]"))
        # )
        pagination_elements = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#container > div > div.nt6sNV.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div:nth-child(2) > div:nth-child(26) > div > div > span:nth-child(1)"))
        )

        

        return pagination_elements[0]

    def extract_product_urls(self,keyword,available_pages):
        product_urls = []
        last_page = int(available_pages.text.split()[-1])
        page = 1
        while(page<2 and page<=last_page):
            flipkart_search_url = f'https://www.flipkart.com/search?q={keyword}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={page}'
            
            self.driver.get(flipkart_search_url)

            search_products = self.driver.find_elements(By.CSS_SELECTOR, "a.CGtC98")
            for product in search_products:
                relative_url = product.get_attribute("href")
                product_url = urllib.parse.urljoin('https://www.flipkart.com/', relative_url)
                product_urls.append(product_url)
            page += 1

        return product_urls[:5]

    def parse_product_data(self, product_url):
        self.driver.get(product_url)
        self.driver.implicitly_wait(5)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # try:
        #     image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", self.driver.page_source)[0])
        # except IndexError:
        #     image_data = None

        # try:
        #     variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', self.driver.page_source)
        # except IndexError:
        #     variant_data = None
        # #feature-bullets > ul > li:nth-child(1) > span
        
        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.a-price')))
        # try:
        #     # Extract price symbol
        #     price_symbol = self.driver.find_element(By.CSS_SELECTOR, '.a-price-symbol').text
        # except:
        #     price_symbol = ""

        # try:
        #     # Extract whole part of the price
        #     price_whole = self.driver.find_element(By.CSS_SELECTOR, '.a-price-whole').text
        # except:
        #     price_whole = ""

        # # Combine all parts into a single price string
        # price = f"{price_symbol}{price_whole}"
        try:
            price = self.driver.find_element(By.CSS_SELECTOR,'div.Nx9bqj.CxhGGd').text.strip()
        except:
            price = ""

        offer_list = []
        try:
            offers = soup.select('.kF1Ml8')
            
            for offer in offers:
                # print(offer)
                offer_title = offer.select("span.ynXjOy")[0].getText(strip=True).encode('utf-8').decode('unicode_escape')
                offer_content = offer.select("li > span:nth-child(2)")[0].getText(strip=True).encode('utf-8').decode('unicode_escape')
                offer_list.append({"title":offer_title,"content":offer_content})

        except:
            pass 
        

        yield {
            "url" : product_url,
            "name": self.driver.find_element(By.CLASS_NAME, "VU-ZEz").text.strip().encode('utf-8').decode('unicode_escape'),
            "price": price.encode('utf-8').decode('unicode_escape'),
            "offers": offer_list
        }

if __name__ == "__main__":
    f=FlipkartScraper()
    print(f.start_scraping("ipad"))

        
    