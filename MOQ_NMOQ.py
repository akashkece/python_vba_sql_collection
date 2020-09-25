# -*- coding: utf-8 -*-
"""
Created on Tue May 21 20:14:31 2019

@author: akmarmu
"""

# Importing packages
from selenium import webdriver
import pandas as pd


# Importing contacts
ds = pd.read_excel("ASIN_Vendor.xlsx", sheet_name=0)
ds = ds.iloc[:, 0:2]

# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
option.add_argument("--safebrowsing-disable-download-protection")
bot = webdriver.Chrome(chrome_options=option)

dataset = []
for i in range(len(ds)):
    bot.get(
        "https://vendorinfoportal.amazon.com/vip/via.jsp?merchantId=1&appMenu=via.jsp&vendorCode="
        + ds.iloc[i, 1]
        + "&asin="
        + ds.iloc[i, 0]
    )
    moq = bot.find_element_by_xpath(
        "(//*[text() = 'Carton Quantity']//following::*)[9]"
    ).text
    nmoq = bot.find_element_by_xpath(
        "(//*[text() = 'Carton Quantity']//following::*)[13]"
    ).text
    dataset.append([ds.iloc[i, 0], ds.iloc[i, 1], moq, nmoq])

bot.quit()

dataset = pd.DataFrame.from_dict(dataset)

dataset.columns = ["ASIN", "Vendor_code", "MOQ", "NMOQ"]

dataset.to_excel("moq_nmoq_output.xlsx", index=False)
