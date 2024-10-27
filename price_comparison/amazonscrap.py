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

class AmazonScraper:
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
            self.driver = webdriver.Chrome(service=s,options=options)
        except:
            pass# Close the browser after scraping

    def start_scraping(self,keyword):
        self.driver.get("https://www.amazon.in/")
        self.wait = WebDriverWait(self.driver, 10)
        return self.search_products(keyword)


    def search_products(self, keyword):
        search_box = self.driver.find_element(By.ID, 'twotabsearchtextbox')
        # type the keyword in searchbox
        search_box.send_keys(keyword)
        # create WebElement for a search button

        search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "nav-search-submit-button")))
        # click search_button
        search_button.click()
        # wait for the page to download
        self.driver.implicitly_wait(5)

        available_pages = self.get_available_pages()

        product_urls = self.extract_product_urls(keyword,available_pages)
       
        all_product_data = []
        for product_url in product_urls:
            output = self.parse_product_data(product_url)
            all_product_data.extend(output)

        # Write data to a JSON file
        self.driver.quit()
        return all_product_data

    def get_available_pages(self):
        available_pages = []
        # pagination_elements = self.wait.until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "*[class^='s-pagination-item'][not(contains(@class, 's-pagination-separator'))]"))
        # )
        pagination_elements = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".s-pagination-strip .s-pagination-item"))
        )

        for element in pagination_elements:
            available_pages.append(element.text)

        return available_pages

    def extract_product_urls(self,keyword,available_pages):
        product_urls = []
        last_page = int(available_pages[-2])
        page = 1
        while(page<2 and page<=last_page):
            amazon_search_url = f'https://www.amazon.in/s?k={keyword}&page={page}'
           
            self.driver.get(amazon_search_url)

            search_products = self.driver.find_elements(By.CSS_SELECTOR, "div.s-result-item[data-component-type=s-search-result]")
            for product in search_products:
                relative_url = product.find_element(By.CSS_SELECTOR, "h2>a").get_attribute("href")
                product_url = urllib.parse.urljoin('https://www.amazon.in/', relative_url)
                product_urls.append(product_url)
            page += 1

        return product_urls[:5]

    def parse_product_data(self, product_url):
        self.driver.get(product_url)
        self.driver.implicitly_wait(5)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Extract product name
        name = soup.select_one('#productTitle').get_text(strip=True)

        # Extract price
        try:
            price = soup.select_one('#corePriceDisplay_desktop_feature_div span.a-price-whole').get_text(strip=True)
        except AttributeError:
            price = "N/A"

        # Extract star rating
        try:
            stars = soup.select_one('i[data-hook=average-star-rating]').get_text(strip=True)
        except AttributeError:
            stars = "N/A"

        # Extract feature bullets
        feature_bullets = [bullet.get_text(strip=True).encode('utf-8').decode('unicode_escape') for bullet in soup.select("#feature-bullets ul li")]

        # Extract offers
        offer_list = []
        offers = soup.select("#anonCarousel1 > ol > li")

        for offer in offers:
            offer_title = offer.find('h2').get_text(strip=True).encode('utf-8').decode('unicode_escape')
            offer_content = offer.find('span', class_='a-truncate-full a-offscreen').get_text(strip=True).encode('utf-8').decode('unicode_escape')
            offer_list.append({"title": offer_title, "content": offer_content})

        # Extract image data
        try:
            image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", str(soup))[0])
        except:
            image_data = []

        yield {
            "url": product_url,
            "name": name.encode('utf-8').decode('unicode_escape'),
            "price": price.encode('utf-8').decode('unicode_escape'),
            "stars": stars,
            "feature_bullets": feature_bullets,
            "offers": offer_list,
            "images": image_data
        }

if __name__ == "__main__":
    a = AmazonScraper()
    print(a.start_scraping("ipad"))


