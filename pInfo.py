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
            re.findall(
                " of ([0-9]+)",
                bot.find_element_by_class_name("eGD5BM").text.replace(",", ""),
            )[0]
        )
        pages = tot_items // 40 + 1
        return tot_items, pages
    except:
        print("Issue in getting pages")
        exit()


def main():
    c = re.compile('data-id="[A-Z0-9]+".+?href="(.+?)">')
    bot = chrome()
    s_url = "https://www.flipkart.com/womens-footwear/pr?sid=osp%2Ciko&offer=nb%3Amp%3A00af124415&fm=neo%2Fmerchandising&iid=M_60c6cdb4-3869-4736-9cd0-1b8726f7ac90_2.TWO7MYEO2A8H&ssid=autsv9yqa80000001580414756057&otracker=hp_omu_Deals%2Bof%2Bthe%2BDay_2_2.dealCard.OMU_TWO7MYEO2A8H_2&otracker1=hp_omu_SECTIONED_neo%2Fmerchandising_Deals%2Bof%2Bthe%2BDay_NA_dealCard_cc_2_NA_view-all_2&cid=TWO7MYEO2A8H&p[]=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove&p[]=facets.price_range.from%3DMin&p[]=facets.price_range.to%3D2000&p[]=facets.size_uk%255B%255D%3D5"
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
