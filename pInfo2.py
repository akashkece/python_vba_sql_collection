import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

n = 0
def chrome():
    """
    This function returns a chrome instance
    """
    option = webdriver.ChromeOptions()
    option.add_argument("--ignore-certificate-errors")
    option.add_argument("--ignore-ssl-errors")
    option.add_argument("--safebrowsing-disable-download-protection")
    return webdriver.Chrome(options=option)


def fkart(bot, p_url):
    global n
    n += 1
    print(f"Checking for {n}")
    try:
        bot.get(p_url)
        rated_by, reviewed_by = (
            bot.find_element_by_class_name("_1je6zX")
            .text.replace(",", "")
            .replace(" reviews", "")
            .split(" ratings and ")
        )
        return [
            p_url,
            bot.find_element_by_class_name("_3qQ9m1")
            .text.replace(",", "")
            .replace("₹", ""),
            bot.find_element_by_class_name("_3auQ3N")
            .text.replace(",", "")
            .replace("₹", ""),
            bot.find_element_by_class_name("_1iCvwn").text.replace("% off", ""),
            bot.find_element_by_class_name("_2ZPBS2").text,
            rated_by,
            reviewed_by,
        ]
    except:
        return [p_url, "Error", "Error", "Error", "Error", "Error", "Error"]


def flip(bot, s_url):
    try:
        bot.get(s_url)
        tot_items = int(
            re.findall(" of ([0-9]+)", bot.find_element_by_class_name("_2yAnYN").text)[
                0
            ]
        )
        pages = tot_items // 40 + 1
        return tot_items, pages
    except:
        return "error", "error"


def main():
    c = re.compile('data-id="[A-Z0-9]+".+?href="(.+?)">')
    bot = chrome()
    s_url = "https://www.flipkart.com/search?q=trekking+bag&sid=reh%2Cplk%2Csan&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_2_8_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_2_8_na_na_na&as-pos=2&as-type=RECENT&suggestionId=trekking+bag|Rucksacks&requestId=70185105-ede1-40c0-a5d0-7c4654041861&as-searchtext=trekking&p[]=facets.price_range.from%3DMin&sort=popularity&p[]=facets.price_range.to%3D2000&p[]=facets.capacity%255B%255D%3DMore%2Bthan%2B60L&p[]=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove"
    p_links = []
    tot_items, pages = flip(bot, s_url)
    for i in range(pages):
        bot.get(s_url + "&page=" + str(i + 1))
        p_links.extend(
            ["https://www.flipkart.com" + s for s in c.findall(bot.page_source)]
        )
    if len(p_links) == tot_items:
        print("All pages correctly stored")
    else:
        print(f"p_links has {len(p_links)} elements while tot_items is {tot_items}")
    p_result = []
    for p_url in p_links:
        p_result.append(fkart(bot, p_url))
    p_result = pd.DataFrame.from_dict(p_result)
    p_result.columns = [
        "product_url",
        "current_price",
        "list_price",
        "discount",
        "rating",
        "rated_by",
        "reviewed_by",
    ]
    p_result.to_excel("flipkart_product_details.xlsx", index=False)
    bot.quit()


if __name__ == "__main__":
    main()
