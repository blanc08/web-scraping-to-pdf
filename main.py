import csv
import logging
import os
import time
import requests

# Web Scraping libraries
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementNotInteractableException,
    ElementClickInterceptedException,
    TimeoutException,
)

# Utils
import retrying

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Scraping:
    def __init__(self, base_url: str, web_driver):
        self.base_url = base_url
        self.driver = web_driver
        self.labels = []
        self.items = []

        # create checkpoint

    # TODO: Main method
    def parse(self, path):
        """
        Parse an items for given path name
        """

        page = 1

        # Check if there are already procesed file for current path
        pages = os.listdir(os.path.join(os.path.curdir, "saved", path))
        if len(pages) > 0:
            pages = [
                int(str(page).split(".")[0]) if len(page.split(".")) > 1 else int(page)
                for page in pages
            ]
            pages.sort(reverse=True)
            print("pages", pages)
            page = pages[0] + 1

        has_more = True
        while has_more:
            has_more = self.parse_page(f"{self.base_url}/{path}", params={"p": page})
            page = page + 1

        return self.items

    def parse_page(self, url: str, params={}):
        """
        docstring
        """
        # fetch a page
        logger.info(f"Parsing items from path {url, params}")
        response = requests.get(url, params=params)

        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find("ol", attrs={"class": "products"})
        items = products.find_all("li", attrs={"class": "item"})
        if items != None or len(items) > 0:
            mapped_item = self.map_items(items)

            # save as file (checkpoint purpose)
            file_name = os.path.join(
                os.path.curdir, "saved", url.split("/")[-1], (str(params["p"]) + ".csv")
            )
            self.explicit_save(mapped_item, file_name)

            self.items.append(mapped_item)
            return True

        return False

    def retry_if_element_not_interactable(self, exception):
        """
        Returns True if we should retry on ElementNotInteractableException, False otherwise.
        """
        return isinstance(
            exception,
            (ElementNotInteractableException, ElementClickInterceptedException),
        )

    @retrying.retry(
        stop_max_delay=5,
        stop_max_attempt_number=10,
        # retry_on_exception=retry_if_element_not_interactable,
    )
    def switch_to_cm(self, dimension_url: str):
        """
        docstring
        """
        try:
            logger.debug(f"trying to fetch {self.base_url + dimension_url}")

            self.driver.get(self.base_url + dimension_url)

            time.sleep(2)

            # Close Region pop up first if exist
            # close Region modal if exist
            is_region_pop_up = self.driver.find_elements(
                by=By.ID, value="shop-country-options"
            )
            if len(is_region_pop_up) > 0:
                buttons = self.driver.find_elements(by=By.TAG_NAME, value="button")
                # 
                matching_elements = [
                    element for element in buttons if element.text.strip() == ""
                ]

                logger.info(
                    f"found region pup up - matching text {matching_elements[0].text}"
                )

                wait_close_pop_up = WebDriverWait(
                    self.driver, 100
                )  # Set a timeout of 60 seconds
                close_pop_up_button = wait_close_pop_up.until(
                    EC.element_to_be_clickable(matching_elements[0])
                )
                close_pop_up_button.click()

            wait_switch_button = WebDriverWait(
                self.driver, 60
            )  # Set a timeout of 60 seconds
            switch_button = wait_switch_button.until(
                EC.element_to_be_clickable((By.ID, "spec-cm-tab-switch"))
            )  # Wait for the region pop-up
            switch_button.click()

        except Exception as e:
            print(
                "is instance",
                isinstance(
                    e,
                    (ElementNotInteractableException, ElementClickInterceptedException),
                ),
            )
            logger.info(f"error while fetching data {type(e)} {e}")
            raise e

    def map_items(self, items):
        """
        docstring
        """
        result = []

        for index, item in enumerate(items):
            dictionary = {}
            try:

                # Name
                name = item.find("strong", {"class": "product-item-name"})
                if name != None:
                    dictionary["Name"] = name.a.text.strip()

                # Product Code
                code = item.find("span", {"class": "product-sku"})
                if code != None:
                    dictionary["Code"] = code.text.strip()

                # Dimensions
                # Dimension spec only available on details page
                dimension_url = item.find("a", {"class": "view-more"})
                if dimension_url != None:
                    dimension_url = dimension_url["href"]

                logger.info(f"{index} || {dimension_url}")

                self.switch_to_cm(dimension_url=dimension_url)

                # Specs
                spec_div = self.driver.find_element(by=By.ID, value="spec-cm-tab")
                if spec_div == None:
                    print(name, code, "have no specs")

                specs = spec_div.find_elements(by=By.TAG_NAME, value="tr")
                for spec in specs:
                    if ":" in spec.text:
                        splited_text = spec.text.split(": ")
                        dictionary[splited_text[0]] = " ".join(splited_text[1:])

                # Image
                image = self.driver.find_elements(
                    by=By.CLASS_NAME, value="fotorama__img"
                )
                if len(image) > 0:
                    dictionary["Image"] = image[0].get_attribute("src")

                # update labels if neccecary
                if len(self.labels) < len(dictionary.keys()):
                    self.labels = dictionary.keys()

                result.append(dictionary)

            except Exception as e:
                is_timeout = isinstance(e, (TimeoutException))
                logger.info(f"error while fetching data {type(e)} {e}")
                if is_timeout == False:
                    raise e

        return result

    def explicit_save(self, items: list, file_name="result.csv"):
        """
        docstring
        """
        max_header = {
            "index": 0,
            "length": 0,
        }

        for index, value in enumerate(items):
            length = len(value.keys())
            if length > max_header["length"]:
                max_header["length"] = length
                max_header["index"] = index

        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            headers = items[max_header["index"]].keys()
            writer.writerow(headers)
            for row in items:
                writer.writerow([value for value in row.values()])

    def save(self, file_name="result.csv"):
        """
        docstring
        """
        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Name",
                    "Code",
                    "Height",
                    "Width",
                    "Canopy",
                    "Socket",
                    "Wattage",
                    "Chain Length",
                    "Weight",
                ]
            )
            for row in self.items:
                writer.writerow([value for value in row.values()])


if __name__ == "__main__":

    # Web Driver
    logger.info("Initializing Web Driver")
    options = webdriver.ChromeOptions()
    web_driver = webdriver.Chrome()

    wall = Scraping(base_url="https://www.visualcomfort.com", web_driver=web_driver)

    items = wall.parse("wall")

    wall.save()

    # debug || offs
    web_driver.quit()

    print("wall", wall.labels)
