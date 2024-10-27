# scrapers.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import urllib.parse
import json
import re

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


class AmazonScraper:
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
            print(f"Error initializing Amazon driver: {e}")
            self.driver = None


    def extract_details(self, product_name):
        # Regex to match the product name, color, RAM, and ROM
        product = re.search(r'^[^(]+', product_name)  # Capture the product name before any parentheses
        color = re.search(r'\(([^,]+)', product_name)  # Capture the content between parentheses before the first comma
        ram = re.search(r'(\d+)GB(?: RAM)?', product_name)  # Match patterns like '8GB' or '8GB RAM'
        rom = re.search(r'(\d+)GB (?:Storage|ROM)', product_name)  # Match '128GB Storage' or '64GB ROM'

        # Extracted values or fallback to 'Unknown' if not found
        product = product.group().strip() if product else product_name
        color = color.group(1) if color else 'Unknown'
        ram = ram.group(1) if ram else 'Unknown'
        rom = rom.group(1) if rom else 'Unknown'

        return product, color, ram, rom


    def scrape_page(self, keyword, page):
        if not self.driver:
            return []

        try:
            # Construct the search URL for the specific page
            amazon_search_url = f'https://www.amazon.in/s?k={urllib.parse.quote(keyword)}&page={page}'
            self.driver.get(amazon_search_url)

            
            pagination_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".s-pagination-strip .s-pagination-item"))
            )
            available_pages = []
            for element in pagination_elements:
                available_pages.append(element.text)
            last_page = int(available_pages[-2])

            if page>last_page:
                print("No more pages to scrap")
                return []

            # Wait until the products are loaded
            search_products = self.wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.s-result-item[data-component-type=s-search-result]")
                )
            )

            product_urls = []
            for product in search_products:
                try:
                    soup = BeautifulSoup(product.get_attribute('innerHTML'), 'html.parser')
                    relative_url = product.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                    img_url = product.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    name = product.find_element(By.CSS_SELECTOR, "h2 a span").text
                    product_name,color,ram,rom = self.extract_details(name)
                    price = soup.select_one("span.a-price-whole").get_text(strip=True) if soup.select_one("span.a-price-whole") else "0"

                    product_url = urllib.parse.urljoin('https://www.amazon.in/', relative_url)
                    product_details = {
                        "img_url": img_url,
                        "name": product_name,
                        "color": color,
                        "ram" : ram,
                        "rom" : rom,
                        "price": int(price.replace(',','')),
                        "url": product_url
                    }
                    product_urls.append(product_details)
                except Exception as e:
                    print(f"Error extracting product data on Amazon page {page}: {e}")
                    continue

            return product_urls
        except Exception as e:
            print(f"Error scraping Amazon page {page}: {e}")
            return []
        finally:
            self.driver.quit()

    def extract_product_details(self,url):
        if not self.driver:
            return []

        try:
            product_details = dict() 
            self.driver.get(url)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # print(soup.select_one("#vsx-desktop-divider"))
            price = soup.select_one("span.a-price-whole").get_text(strip=True) if soup.select_one("span.a-price-whole") else "N/A"

            offers = soup.select_one("#vsxoffers_feature_div")
            offer_list = []
            for offer in offers.find_all("li"):
                offer_title = offer.find('h6',class_="offers-items-title").get_text(strip=True).encode('utf-8').decode('unicode_escape')
                offer_content = offer.find('span', class_='a-truncate-full a-offscreen').get_text(strip=True).encode('utf-8').decode('unicode_escape')
                offer_list.append({"title": offer_title, "content": offer_content})
            
            overview = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#productOverview_feature_div")))
            overview_div = BeautifulSoup(overview[0].get_attribute('innerHTML'), 'html.parser')
            overview_table_html = overview_div.find('table')
            overview_table = []
            for row in overview_table_html.tbody.find_all('tr'):
                overview_dict = dict()
                overview_dict["th"] = row.select_one("td.a-span3 span").get_text(strip=True)
                overview_dict["tr"] = row.select_one("td.a-span9 span").get_text(strip=True)
                overview_table.append(overview_dict)
            
            about_item = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#feature-bullets")))
            about_item_html = BeautifulSoup(about_item[0].get_attribute('innerHTML'), 'html.parser')
            about=[]
            for li in about_item_html.select("span.a-list-item"):
                about.append(li.get_text(strip=True))

            product_table = self.wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#productDetails_techSpec_section_1")))
            table = BeautifulSoup(product_table[0].get_attribute('innerHTML'), 'html.parser')

            details = []
            for row in table.tbody.find_all('tr'):
                detail = dict()
                detail["th"] = row.find("th").get_text(strip=True)
                detail["tr"] = row.find("td").get_text(strip=True)
                details.append(detail)
            
            product_details["price"] = int(price.replace(',','').replace('.',''))
            product_details["overview"] = overview_table
            product_details["offers"] = offer_list
            product_details["about"] = about
            product_details["details"] = details
            return product_details
        except Exception as e:
            print(f"Error scraping Amazon page: {e}")
            return []
        finally:
            self.driver.quit()




if __name__ == "__main__":
    a = AmazonScraper()
    # print(a.extract_product_details("https://www.amazon.in/Redmi-Storage-Bezel-Less-Slimmest-Pro-Grade/dp/B0CQPGG8KG/ref=sr_1_1_sspa?crid=HWXNJMPFEEPT&dib=eyJ2IjoiMSJ9.Gi_Yp1ZQyW9sObjGAzJn47sJIYwJUj-gJ5U4gkZBh4vWwH18mMloGJgHbrlpfj11xixUIDhK6Qjy-NV4_HUQGS4LE9R5KOfbcAZA1qTDQHSladFfc_ZEGn2wh0jWk5vLEnLi-e-7OiZsD59kUAfSbiJ-ZuSdl1KYseQC3tePJlZVM-4Ni8LmkAHobfzBaKNHern2m4Qsk99y7_GpsdhbAL4Ry0_Z7aeBVCXWKEp83_8.tQuX7qeJ9aTPOKsCyqm0Sgvn5RES7yPkmt4djhDOqmg&dib_tag=se&keywords=redmi&qid=1727534691&sprefix=%2Caps%2C274&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"))
    print(a.scrape_page("redmi note 13",1))