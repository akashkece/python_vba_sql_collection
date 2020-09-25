import re
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


def chrome():
    """This creates a chrome instance
    """
    option = webdriver.ChromeOptions()
    option.add_argument("--ignore-certificate-errors")
    option.add_argument("--ignore-ssl-errors")
    option.add_argument("--safebrowsing-disable-download-protection")
    option.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=option)


def midway(bot):
    """Takes chrome instance as input and returns midway authenticated chrome instance
    """
    print(
        "*" * 3,
        "Please Authenticate browser with your Midway credentials ",
        "*" * 3,
        "\n",
    )
    bot.get("https://midway.amazon.com")
    input("Please press enter once Midway Authentication is Successful: ")
    print(end="\n \n")
    return bot


bot = midway(chrome())
c = re.compile(
    r"Recommended Discount \(Tax Included\): [.0-9]+ with discount strategy: [_A-Z]+")


def pricingDiscount(asin):
    try:
        bot.get(
            'https://pricingrules.amazon.com/rest/itemDetails/1/1/null/' + asin + '/latestPricingRulesEvaluationDetails')
        page = bot.page_source
        if len(c.findall(page)) != 0:
            return c.findall(page)
        else:
            return "Not Found"
    except TimeoutException:
        return "Page Load Error"


def main():
    start_time = time.time()
    print(f"start time: {time.strftime('%x %X')}")
    asins = pd.read_excel(r"C:\Users\akmarmu\Downloads\asins(1).xlsx").iloc[:, 0]

    result = []
    for i in asins:
        result.append([i, pricingDiscount(i)])
    result = pd.DataFrame(result)
    result.columns = ["asin", "pricingDiscount_comment"]
    result.to_csv("pricing_remarks.csv", index=False)
    end_time = time.time()
    minutes = (end_time - start_time) // 60
    seconds = (end_time - start_time) % 60
    print(f"end time: {time.strftime('%x %X')}")
    print(
        f"Approx. time taken : {round(minutes)} minutes {round(seconds)} seconds")


if __name__ == "__main__":
    main()
bot.quit()
