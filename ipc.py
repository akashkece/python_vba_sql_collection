# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 16:14:55 2019

@author: akmarmu
"""

# Importing packages
from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

n = -1

# Reading the input file
ds = pd.read_excel("asins.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]

# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
bot = webdriver.Chrome(chrome_options=option)
# Creating function to catch PO details
def IPC(asin):
    global n
    n = n + 1
    print(n)
    try:
        if len(asin) == 10:
            bot.get(
                "https://ipc-na.amazon.com/planning/AsinPlanReview?scopeId=AMAZON_US&asins="
                + asin
                + "&submit=Preview+Plans"
            )

            POType = bot.find_element_by_xpath(
                "(//*[text() = 'PO Type']/following::*)[26]"
            ).text
            BuyingIntent = bot.find_element_by_xpath(
                "(//*[text() = 'PO Type']/following::*)[27]"
            ).text
            element = [asin, POType, BuyingIntent]
            return element
        else:
            return [
                asin,
                "ASIN does not seem to be valid",
                "ASIN does not seem to be valid",
            ]
    # in case of exception
    except NoSuchElementException:
        return [asin, "Please check manually", "Please check manually"]


# Applying function to each ASINs and concatening ASIN and PO qtys
temp = []

for asin in ds:
    temp.append(IPC(asin))
bot.quit()

df = pd.DataFrame(temp, columns=["asin", "PO Type", "Buying Intent"])


# Getting Excel output
writer = pd.ExcelWriter("IPC_Output.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="IPC", index=False)
writer.save()
