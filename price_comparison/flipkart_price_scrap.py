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

        # Randomize user agent
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        user_agent_rotator = UserAgent(
            software_names=software_names,
            operating_systems=operating_systems,
            limit=100
        )
        user_agent = user_agent_rotator.get_random_user_agent()

        options.add_argument("--headless=new")  # Ensure headless mode is active
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1420,1080')
        options.add_argument('--disable-gpu')
        options.add_argument(f'user-agent={user_agent}')

        s = Service(self.DRIVER_PATH)

        try:
            self.driver = webdriver.Chrome(service=s, options=options)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            print(f"Error initializing Flipkart driver: {e}")
            self.driver = None

    def extract_color(self,product_name):
    # Regex to match color and ROM
        product = re.search(r'^[^(]+', product_name)
        color = re.search(r'\(([^,]+)', product_name)  # Capture content between parentheses before the first comma
    
        # Extracted values or fallback to 'Unknown' if not found
        product = product.group().strip() if product else product_name
        color = color.group(1) if color else 'Unknown'

        return product,color
    
    def extract_ram_rom(self,details):
        ram = re.search(r'(\d+) GB RAM', details)  # Match the number before 'GB RAM'
        rom = re.search(r'(\d+) GB ROM', details)  # Match the number before 'GB ROM'
    
        # Extracted values or fallback to 'Unknown' if not found
        ram = ram.group(1) if ram else 'Unknown'  # Get only the numeric part
        rom = rom.group(1) if rom else 'Unknown'  # Get only the numeric part

        return ram, rom 

    def scrape_page(self, keyword, page):
        if not self.driver:
            return []

        try:
            # Construct the search URL for the specific page
            flipkart_search_url = f'https://www.flipkart.com/search?q={urllib.parse.quote(keyword)}&page={page}'
            self.driver.get(flipkart_search_url)

            # Wait until the products are loaded
            search_products = self.wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, "div._75nlfW")
                )
            )

            # pagination_elements = self.wait.until(
            #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#container > div > div.nt6sNV.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div:nth-child(2) > div:nth-child(26) > div > div > span:nth-child(1)"))
            # )
            # last_page = int(pagination_elements[0].text.split()[-1])
            # print(last_page)

            product_urls = []
            for product in search_products:
                try:
                    soup = BeautifulSoup(product.get_attribute('innerHTML'), 'html.parser')
                    name = soup.select_one("div.KzDlHZ").get_text(strip=True)
                    product_name,color = self.extract_color(name)
                    details = soup.select_one("ul.G4BRas li").get_text(strip=True)
                    ram,rom = self.extract_ram_rom(details)
                    img_url = soup.select_one("img.DByuf4")["src"]
                    price = soup.select_one("div.Nx9bqj._4b5DiR").get_text(strip=True)
                    product_url = urllib.parse.urljoin('https://www.flipkart.com/', soup.select_one("a.CGtC98")["href"])

                    product_details = {
                        "img_url": img_url,
                        "name": product_name,
                        "color": color,
                        "ram": ram,
                        "rom": rom,
                        "price": int(price[1:].replace(',','')),
                        "url": product_url
                    }
                    product_urls.append(product_details)
                except Exception as e:
                    print(f"Error extracting product data on Flipkart page {page}: {e}")
                    continue

            return product_urls
        except Exception as e:
            print(f"Error scraping Flipkart page {page}: {e}")
            return []
        finally:
            self.driver.quit()
    def extract_product_details(self, url):
        if not self.driver:
            return []

        try:
            product_details = {}
            self.driver.get(url)

            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Extract price with safety checks
            price_element = soup.select_one("div.Nx9bqj.CxhGGd")
            price = int(price_element.get_text(strip=True)[1:].replace(',', '')) if price_element else None
            product_details["price"] = price

            # Extract offers if available
            offer_list = []
            offers = soup.select('.kF1Ml8')
            for offer in offers:
                try:
                    offer_title_element = offer.select_one("span.ynXjOy")
                    offer_content_element = offer.select_one("li > span:nth-child(2)")

                    offer_title = offer_title_element.get_text(strip=True) if offer_title_element else 'No title'
                    offer_content = offer_content_element.get_text(strip=True) if offer_content_element else 'No content'

                    offer_list.append({"title": offer_title, "content": offer_content})
                except Exception as e:
                    print(f"Error extracting offer details: {e}")
                    continue

            product_details["offers"] = offer_list
            return product_details

        except Exception as e:
            print(f"Error scraping Flipkart product page: {e}")
            return []

        finally:
            # Move driver quit outside the function if you plan to reuse it
            if self.driver:
                self.driver.quit()

        

if __name__ == "__main__":
    a = FlipkartScraper()
    print(a.extract_product_details("https://www.flipkart.com/redmi-note-13-5g-prism-gold-128-gb/p/itm82475e073eb2e?pid=MOBGXYWXMQEFE9VH&lid=LSTMOBGXYWXMQEFE9VHZLVZ66&marketplace=FLIPKART&q=redmi+note+13&store=tyy%2F4io&srno=s_1_4&otracker=search&iid=1865ba39-a90b-42f0-b64c-31458cde527b.MOBGXYWXMQEFE9VH.SEARCH&ssid=6rkk43xidc0000001728662237608&qH=1be01344da6d1dc7"))
    # print(a.scrape_page("redmi note 13",1))