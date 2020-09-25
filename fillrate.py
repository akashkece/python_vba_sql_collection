# -*- coding: utf-8 -*-
"""
Created on Sat Jul 14 04:10:57 2018

@author: akmarmu
"""

# Importing packages
from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime as dt
from datetime import timedelta as td

date1 = dt.now() - td(days=104)
date2 = dt.now() - td(days=14)
n = -1

# Reading the input file
ds = pd.read_excel("asins.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]

# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
bot = webdriver.Chrome(chrome_options=option)
# Creating function to catch PO details
def qtyPO(asin):
    global n
    n = n + 1
    print(n)
    try:
        if len(asin) == 10:
            bot.get(
                "https://buyingportal-us.amazon.com/gp/ors/asinstat/asinstat.html?asin="
                + asin
                + "&vendorCountry=101&iogFilter=-1&biblioFlag=on&marketplaceId=ATVPDKIKX0DER&inventoryFlag=on&distributorFlag=on&pendingFlag=on&zeroQtyConfFlag=on&unreceivedFlag=on&orderedFrom="
                + str(date1.month).zfill(2)
                + "%2F"
                + str(date1.day).zfill(2)
                + "%2F"
                + str(date1.year)
                + "&orderedTo="
                + str(date2.month).zfill(2)
                + "%2F"
                + str(date2.day).zfill(2)
                + "%2F"
                + str(date2.year)
            )
            qtySub = bot.find_element_by_xpath(
                "(//*[text() = 'Quantity Submitted']/following::*)[9]"
            ).text
            qtyRec = bot.find_element_by_xpath(
                "(//*[text() = 'Quantity Submitted']/following::*)[13]"
            ).text
            element = [asin, qtySub, qtyRec]
            if qtySub == "0":
                try:
                    err = bot.find_element_by_xpath(
                        "//*[text()='Error getting catalog data: BadArgs']"
                    ).text
                    return [
                        asin,
                        "ASIN does not seem to be valid - " + err,
                        "ASIN does not seem to be valid - " + err,
                    ]
                except:
                    return [asin, "0", "0"]
            else:
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
temp1 = []

for asin in ds:
    temp1.append(qtyPO(asin))
bot.quit()

df = pd.DataFrame(temp1, columns=["asin", "Quantity Submitted", "Quantity Received"])

# Getting column for fillrate
def fillrate(submit, received):
    if submit == "0":
        return 0
    elif submit == "ASIN does not seem to be valid":
        return "ASIN does not seem to be valid"
    elif submit == "Please check manually":
        return "Please check manually"
    elif (
        submit == "ASIN does not seem to be valid - Error getting catalog data: BadArgs"
    ):
        return "ASIN does not seem to be valid - Error getting catalog data: BadArgs"
    else:
        submit = pd.to_numeric(submit)
        received = pd.to_numeric(received)

        return received / submit


temp2 = []
for i in range(ds.count()):
    temp2.append(fillrate(df["Quantity Submitted"][i], df["Quantity Received"][i]))
df["fill rate"] = pd.DataFrame(temp2)

# Getting Excel output
writer = pd.ExcelWriter("FillRate_Output.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="fillrate", index=False)
workbook = writer.book
worksheet = writer.sheets["fillrate"]
format1 = workbook.add_format({"num_format": "0.00%"})
worksheet.set_column("A:A", 24)
worksheet.set_column("B:B", 35)
worksheet.set_column("C:C", 35)
worksheet.set_column("D:D", 35, format1)
writer.save()
