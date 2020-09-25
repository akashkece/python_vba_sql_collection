# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 08:41:57 2018

@author: akmarmu
"""

# Importing packages
from selenium import webdriver
import pandas as pd
import time

# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
bot = webdriver.Chrome(chrome_options=option)
bot.implicitly_wait(10000)

# Reading the input file
ds = pd.read_excel("asins.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]
vg = 377980


def vineEligibility(asin):
    bot.get(
        "https://vendorcentral-portal-us.amazon.com/gp/vendor/vine/eligibility.html"
    )
    bot.find_element_by_xpath(
        "(//*[text() = 'Check Vine Eligibility']//following::*)[4]"
    ).send_keys(asin)
    bot.find_element_by_xpath(
        "(//*[text() = 'Check Vine Eligibility']//following::*)[5]"
    ).send_keys(vg)
    bot.find_element_by_xpath(
        "(//*[text() = 'Check Vine Eligibility']//following::*)[6]"
    ).click()
    time.sleep(10)
    return bot.find_element_by_id("pageMessages").text


hi = ds.apply(vineEligibility)

df = pd.concat([ds, hi], axis=1)

writer = pd.ExcelWriter("Vine_Results.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Status", index=False)
writer.save()


bot.quit()
