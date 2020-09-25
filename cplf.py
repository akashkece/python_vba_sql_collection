# -*- coding: utf-8 -*-
"""
Created on Sat Jul 14 04:10:57 2018

@author: akmarmu
"""


# Importing packages
from selenium import webdriver
import pandas as pd
import time
from selenium.common.exceptions import NoSuchElementException

n = -1

# Reading the input file
ds = pd.read_excel("asins.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]
print(time.time())


# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
bot = webdriver.Chrome(chrome_options=option)

bot.get("https://midway.amazon.com")
time.sleep(20)

# Creating function to get CPLF value
def cplf(asin):
    global n
    n = n + 1
    print(n)
    try:
        bot.get(
            "https://pricingrules.amazon.com/item.html?legalEntityId=101&sku=" + asin
        )
        ele1 = bot.find_element_by_xpath(
            "(//*[text()='Forward Looking CP:']/following::*)[1]"
        ).text
        ele2 = (
            bot.find_element_by_class_name("item-details")
            .find_element_by_tag_name("tbody")
            .find_elements_by_tag_name("td")[1]
            .text
        )
        # to verify cplf is same by both methods or no
        if ele1 == ele2:
            return ele1
        else:
            return "Error, please check manually"
    # in case of exception
    except NoSuchElementException:
        return "Not able to find Forward Looking CP"


# Applying function to each ASINs and concatening ASIN and flcp
hi = ds.apply(cplf)
df = pd.concat([ds, hi], axis=1)
df.columns = ["asin", "CPLF"]

# Getting Excel output
writer = pd.ExcelWriter("CPLF_output.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Forward Looking CP", index=False)
writer.save()

bot.quit()
print(time.time())
