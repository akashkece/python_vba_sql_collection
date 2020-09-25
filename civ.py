# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 04:31:43 2018

@author: akmarmu
"""

# Importing packages
from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import time

n = -1

# Reading the input file
ds = pd.read_excel("asinsWithNegativeCPLF.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]

# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
bot = webdriver.Chrome(chrome_options=option)

# Creating function to get CIV value
def civ(asin):
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
            try:
                url = (
                    bot.find_element_by_class_name("even")
                    .find_elements_by_tag_name("a")[4]
                    .get_attribute("href")
                )
            except IndexError:
                url = "dummy"
            if url == "dummy":
                return bot.find_element_by_xpath(
                    '(//*[text() = "Failure Message"]/following::*)[5]'
                ).text
            else:
                bot.get(url)
                time.sleep(100)
                ele = bot.find_element_by_xpath(
                    '((//*[text() = "Profitability"])[1]/following::*)[160]'
                ).text
                return ele
        else:
            return "ASIN does not seem to be valid"
    # in case of exception
    except NoSuchElementException:
        return "Not able to find CIV value"


# Applying function to each ASINs and concatening ASIN and civ
hi = ds.apply(civ)
df = pd.concat([ds, hi], axis=1)
df.columns = ["asin", "CIV"]

# Getting Excel output
writer = pd.ExcelWriter("CIV_output.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="CIV Value", index=False)
writer.save()

bot.quit()
