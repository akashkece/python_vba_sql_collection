# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 18:16:27 2019

@author: akmarmu
"""

# Importing the libraries
import pandas as pd
import os
from tkinter import filedialog
import tkinter as tk


# Importing the SQl result
root = tk.Tk()
root.withdraw()
dataset = pd.read_excel(
    filedialog.askopenfilename(
        title="Select the macro result(Make sure you have included Task_ID and Vendor Code in first two columns)"
    ),
    sheet_name=0,
)

dataset = dataset.iloc[:, :]
dataset["file_name"] = dataset["Task_ID"].map(str) + "_" + dataset["Vendor Code"]
dataset = dataset.iloc[:, 2:]

dataset = dataset.sort_values(["file_name"], ascending=[True])

dirName = "Split Files by Vendor"

try:
    os.mkdir(dirName)
    print("Directory ", dirName, " Created ")
except FileExistsError:
    print("Directory ", dirName, " already exists")

os.chdir(dirName)

vend = dataset["file_name"].unique()

for i in vend:
    fName = i + ".xlsx"
    writer = pd.ExcelWriter(
        fName, engine="xlsxwriter", options={"strings_to_urls": False}
    )
    dataset.iloc[:, :-1][dataset["file_name"] == i].to_excel(
        writer, sheet_name="Sheet1", index=False
    )
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    n = str(len(dataset.iloc[:, :-1][dataset["file_name"] == i]))
    format1 = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
    worksheet.conditional_format(
        "W2:W" + n,
        {"type": "cell", "criteria": "==", "value": "FALSE", "format": format1},
    )
    worksheet.conditional_format(
        "X2:AC" + n,
        {"type": "cell", "criteria": "==", "value": "TRUE", "format": format1},
    )
    writer.save()
