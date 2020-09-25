# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 19:12:54 2018

@author: akmarmu
"""

# Importing packages
from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import time

start_time = time.time()
print(f"start time: {time.strftime('%x %X')}")
print("")


n = 0

# Reading the input file
ds = pd.read_excel("asins.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]


# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
bot = webdriver.Chrome(options=option)

bot.get("https://midway.amazon.com")
time.sleep(15)

# Creating function to get CPLF value
def inventory(asin):
    global n
    n = n + 1
    print("checked for " + str(n))
    try:
        bot.get(
            "https://alaska-na.amazon.com/index.html?viewtype=summaryview&use_scrollbars=&fnsku_simple="
            + asin
            + "&marketplaceid=1&merchantid=1&AvailData=Get+Availability+Data"
        )
        ele1 = bot.find_element_by_xpath('(//*[text() = "Net"]/following::*)[1]').text
        ele2 = bot.find_elements_by_tag_name("th")[34].text
        # to verify inventory is same by both methods or no
        if ele1 == ele2:
            return ele1
        else:
            return "Error, please check manually"
    # in case of exception
    except NoSuchElementException:
        return "Not able to find Inventory"


# Applying function to each ASINs and concatening ASIN and flcp
hi = ds.apply(inventory)
df = pd.concat([ds, hi], axis=1)
df.columns = ["asin", "Net Inventory"]

# Getting Excel output
writer = pd.ExcelWriter("Inventory_output.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Inventory", index=False)
writer.save()

bot.quit()

end_time = time.time()
minutes = (end_time - start_time) // 60
seconds = (end_time - start_time) % 60
print(f"end time: {time.strftime('%x %X')}")
print(
    f"Approx. time taken to get all the values: {round(minutes)} minutes {round(seconds)} seconds"
)

