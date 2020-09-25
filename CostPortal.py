# -*- coding: utf-8 -*-
"""
Created on Fri May 17 17:37:25 2019

@author: akmarmu
"""

# Importing packages
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime as dt

# Print start time
timeAtStart = dt.now()
print("Start time : " + str(timeAtStart))

# Reading the input file
ds = pd.read_excel(r"C:\Users\akmarmu\Downloads\asins.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]

# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
option.add_argument("--safebrowsing-disable-download-protection")
bot = webdriver.Chrome(options=option)


dataset = []
color = []
color_result = []
for i in range(len(ds)):
    print(" checking for " + str(i + 1))
    try:
        bot.get(
            "https://cost.amazon.com/costManagement/costLookup/asin/" + ds.iloc[i, ] + "/showTerminated/false"
        )
        html = bot.page_source
        soup = BeautifulSoup(html, "lxml")
        tab_data = soup.select("table")[2]
        for items in tab_data.select("tr"):
            item = [elem.text for elem in items.select("th,td")]
            dataset.append(", ".join(item))
            clr = [elm for elm in items.select("th, td")]
            color.append(str(clr))
    except:
        print("Error for asin: " + ds.iloc[i, ])
bot.quit()

dataset = pd.DataFrame.from_dict(dataset)
dataset.columns = ["data"]
color = pd.DataFrame.from_dict(color)
color.columns = ["color"]
dataset = pd.concat([dataset, color], axis=1, join="inner")

dataset = dataset[~dataset.data.str.contains("Bulk Termination")]
dataset = dataset[~dataset.data.str.contains("Cost Record Search")]
dataset = dataset[~dataset.data.str.contains("Asin,")]
dataset = dataset[~dataset.data.str.contains("Vendor Code,")]
dataset = dataset[~dataset.data.str.contains("Show History,")]
dataset = dataset[
    ~dataset.data.str.contains("Vendor code against which cost is stored.")
]
dataset = dataset[~dataset.data.str.contains(", ,  , ")]
dataset = dataset[~dataset.data.str.contains(",  , ")]
dataset = dataset[
    ~dataset.data.str.contains(
        "Amazon.com CONFIDENTIAL | © 2008 Amazon.com. All rights reserved."
    )
]
dataset = dataset.reset_index(drop=True)
result = pd.concat([dataset.data.str.split(", ", expand=True)], axis=1)
result = result.iloc[:, 0:14]
result.columns = [
    "Vendor_code",
    "ASIN",
    "Qty",
    "Currency Code",
    "Unit_Cost",
    "VAT",
    "List_Price",
    "Discount%",
    "Start Date(UTC)",
    "End Date(UTC)",
    "Source",
    "Priority",
    "CQS_Vendor",
    "Created_By",
]


color = dataset.iloc[:, 1:2]

for cl in range(len(color)):
    color_result.append(
        str(
            re.findall('class="[a-zA-Z0-9]+? (highlighted)', str(color.iloc[cl, ])) == ["highlighted"]
        )
    )
color_result = pd.DataFrame.from_dict(color_result)
color_result.columns = ["data"]

final_result = pd.concat([result, color_result], axis=1, join="inner")


final_result.to_excel("costPortal.xlsx", index=False)

# Getting Excel output
writer = pd.ExcelWriter("costPortal.xlsx", engine="xlsxwriter")
final_result.iloc[:, 0:15].to_excel(writer, sheet_name="Sheet1", index=False)
workbook = writer.book
worksheet = writer.sheets["Sheet1"]
format1 = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
format2 = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})

worksheet.conditional_format(
    "O2:O100000",
    {"type": "cell", "criteria": "==", "value": '"True"', "format": format2},
)

worksheet.conditional_format(
    "O2:O100000",
    {"type": "cell", "criteria": "==", "value": '"False"', "format": format1},
)

writer.save()

# Print end time
timeAtEnd = dt.now()
print("EndTime: " + str(timeAtEnd))
print("Total time : " + str(timeAtEnd - timeAtStart))

input("Web scrapping complete, please close this window")
