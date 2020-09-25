# Importing libraries
import pandas as pd
import os
import getpass
import calendar
from datetime import date
from pyxlsb import open_workbook as open_xlsb

# Getting username and week number
username = getpass.getuser()
"""
if calendar.day_name[date.today().weekday()] == "Sunday":
    wk = date.today().isocalendar()[1]
else:
    wk = date.today().isocalendar()[1] - 1
"""
wk = 52
fold = "wk" + str(wk)

# Importing raw data
os.chdir("C:/Users/" + username + "/Desktop/AVS Dashboard")
file_path = "AVS Dashboard - 2019.xlsb"

df = []

with open_xlsb(file_path) as wb:
    with wb.get_sheet("Raw Data") as sheet:
        for row in sheet.rows():
            df.append([item.v for item in row])

df = pd.DataFrame(df[1:], columns=df[0])


# Creating week folder on Desktop
source_dir = "C:/Users/" + username + "/Desktop"
os.chdir(source_dir)
if not os.path.exists(fold):
    os.makedirs(fold)
os.chdir(fold)


# Tasks pending from more than 50 days
df["Open Ageing"] = pd.to_numeric(df["Open Ageing"], errors="coerce")
ds_50 = df[
    (df["Task Classification"] == "Reactive")
    & (df["Ticket Status (Grouped)"] == "Open")
    & (df["Activity Owner"] == "RBS")
    & (df["Open Ageing"] >= 50)
]

ds_50 = ds_50.filter(
    [
        "case_id_short",
        "activity",
        "Account Manager",
        "Ticket Status",
        "assign_group_platform",
        "requester_email",
        "product_group_name",
        "arrived_datetime",
    ]
)

ds_50["Ageing"] = ""
ds_50["RBS Callout"] = ""
ds_50["Additional Comments"] = ""

cb = "50 days pending wk -" + str(wk) + ".xlsx"
writer = pd.ExcelWriter(cb, engine="xlsxwriter")
ds_50.to_excel(writer, sheet_name="pending for 50 days", index=False)
workbook = writer.book
worksheet = writer.sheets["pending for 50 days"]
format1 = workbook.add_format({"num_format": "mm/dd/yyyy hh:mm"})
worksheet.set_column("H:H", 18, format1)
writer.save()


# Filtering last 4 weeks data
df["Closed Wk"] = pd.to_numeric(df["Closed Wk"])
ds = df[
    (df["Task Classification"] == "Reactive")
    & (df["Closed Wk"] > (wk - 4))
    & (df["Ticket Status"] == "Closed")
    & (df["Activity Owner"] == "RBS")
    & (df["Closed Year"] == 2019)
]

ds = ds.filter(
    items=[
        "case_id_short",
        "activity",
        "sla_miss_reason",
        "SLA",
        "SLA Category",
        "FTR",
        "ftr_miss_bucket",
        "last_closed_reason_code",
        "closed_reason_code_breakdown",
        "Success Response",
        "Success Status",
        "Closed Wk",
        "Account Manager",
    ]
)

# Removing row lines where no. of tasks last week are less than 20
activity_count = ds[ds["Closed Wk"] == wk].groupby("activity")["case_id_short"].count()
activity_count = pd.DataFrame(
    {"activity": activity_count.index, "count of tasks": activity_count.values}
)
activity_count = activity_count[activity_count["count of tasks"] > 19]
activity_count = activity_count.iloc[:, 0]
ds = ds[ds["activity"].isin(activity_count)]

# Exporting the final raw data file
ds.to_excel("raw_data wk -" + str(wk) + ".xlsx", index=False)
