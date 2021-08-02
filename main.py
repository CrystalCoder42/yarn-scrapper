from selenium import webdriver
import dotenv
from pprint import pprint
import json
import time
import csv

dotenv.load_dotenv()
config = dotenv.dotenv_values()


def process_page_lovecrafts(selenium_driver, url):
    """
    Scrapes data from a given yarn page
    :param selenium_driver: The selenium driver
    :param url: The url of the product
    :return: A dict of the scraped data
        link: The url
        name: The name of the product
        blend: The fiber content of the yarn
        weight: The weight of the product (usually the ball size)
        price: The price of the product
        length: The yardage of the product
    """
    selenium_driver.get(url)
    name = selenium_driver.find_element_by_class_name("product-name").text
    blend = selenium_driver.find_element_by_class_name("blend-attribute").text
    weight = selenium_driver.find_element_by_class_name("ball_weight_yarn-attribute").text
    price = selenium_driver.find_element_by_class_name("price").text
    length = selenium_driver.find_element_by_class_name("yarn_length-attribute").text
    return {
        "link": url,
        "name": name,
        "blend": blend,
        "weight": weight,
        "price": price,
        "length": length
    }


def process_page_knitpicks(selenium_driver, url):
    """
    Scrapes a knitpicks product page
    :param selenium_driver: The selenium driver
    :param url: The product url
    :return: A dict of the scraped data
        link: The url
        name: The name of the product
        blend: The fiber content of the yarn
        weight: The weight of the product (usually the ball size)
        price: The price of the product
        length: The yardage of the product
    """
    selenium_driver.get(url)
    name = selenium_driver.find_element_by_class_name("product-title").text

    yarn_details_raw = selenium_driver.find_element_by_class_name("details-display").text
    yarn_details_list = yarn_details_raw.split("\n")
    yarn_details = dict([tuple(detail.split(": ")) for detail in yarn_details_list])

    blend = yarn_details.get("Fiber Content")
    weight = yarn_details.get("Grams")
    price = selenium_driver.find_element_by_class_name("price").text
    length = yarn_details.get("Yards")
    return {
        "link": url,
        "name": name,
        "blend": blend,
        "weight": weight,
        "price": price,
        "length": length
    }


def process_pages_lovecrafts(selenium_driver):
    selenium_driver.get("https://www.lovecrafts.com/en-us/l/yarns/yarns-by-weight/dk-yarn#?"
                        "colour=1853&"
                        "fiber_yarns=64%2C"
                        "65%2C"
                        "67%2C"
                        "1646%2C"
                        "1650%2C"
                        "1651%2C"
                        "1657%2C"
                        "1659%2C"
                        "1660%2C"
                        "1836%2C"
                        "6613%2C"
                        "36872%2C"
                        "60117%2C"
                        "93531&")
    product_items = selenium_driver.find_elements_by_class_name("product-item")
    product_links = [product_item.find_element_by_tag_name("a").get_attribute("href") for product_item in product_items]
    with open("output/product_info_v2.json", "w") as product_info_file:
        json.dump([process_page_lovecrafts(selenium_driver, link) for link in product_links], product_info_file)


def process_pages_knitpicks(selenium_driver, output_file):
    selenium_driver.get("https://www.knitpicks.com/3001/filter-products?"
                        "Color=Whites%20%26%20Off-Whites&Fiber-Content=Alpaca%2C"
                        "Cashmere%2C"
                        "Cotton%2C"
                        "Linen%2C"
                        "Merino%2C"
                        "Mohair%2C"
                        "Natural%2C"
                        "Silk%2C"
                        "Wool&Yarn-Weight=DK&ROBOTS=NO")
    product_items = selenium_driver.find_elements_by_class_name("category-item")
    product_links = [product_item.find_element_by_tag_name("a").get_attribute("href") for product_item in product_items]
    with open(output_file, "w") as product_info_file:
        json.dump([process_page_knitpicks(selenium_driver, link) for link in product_links], product_info_file)


def check_for_missing(file_name):
    """
    Checks for missing information
    """
    with open(file_name, "r") as product_info_file:
        product_info = json.load(product_info_file)
        for product in product_info:
            if "" in product.values():
                pprint(product)


def load_to_csv(input_file, output_file, weight_change):
    """
    Loads the json of yarn products into a csv and cleans the info
    """
    with open(input_file, "r") as product_info_file, \
            open(output_file, "w", newline='') as product_info_csv:
        product_info = json.load(product_info_file)
        cleaned_info = []
        for product in product_info:
            row = {
                "name": product.get("name").replace("\n", " "),
                "weight": float(product.get("weight").replace("oz", ""))*weight_change,
                "blend": product.get("blend"),
                "price": product.get("price"),
                "length": product.get("length").split("yds")[0],
            }
            cleaned_info.append(row)
        writer = csv.DictWriter(product_info_csv, ["name", "blend", "weight", "price", "length"])
        writer.writeheader()
        writer.writerows(cleaned_info)


if __name__ == '__main__':
    # driver = webdriver.Chrome(executable_path=config.get("CHROME_LOCATION"))
    # process_pages_knitpicks(driver, "output/product_info_v3.json")
    # driver.close()
    # check_for_missing("output/product_info_v3.json")
    load_to_csv("output/product_info_v3.json", "output/product_info_v2.csv", 1)
