# Importing packages
from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

n = 0

# Reading the input file
ds = pd.read_excel("vendor_codes.xlsx", sheet_name=0)
ds = ds.iloc[:, 0]


# Creating chrome driver using selenium
option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
bot = webdriver.Chrome(chrome_options=option)

# Creating function to get CPLF value
def VM(vendor_code):
    global n
    n += 1
    print("Working on " + str(n))
    try:
        bot.get(
            "https://vm.amazon.com/vm/jsp/VendorEditForm.jsp?vendorCode=" + vendor_code
        )
        return bot.find_element_by_xpath(
            "//*[contains(@id,'inventoryVendorTypeString')]//*[contains(@selected,'selected')]"
        ).text

    # in case of exception
    except NoSuchElementException:
        return "Not able to find"


# Applying function to each ASINs and concatening ASIN and flcp
hi = ds.apply(VM)
df = pd.concat([ds, hi], axis=1)
df.columns = ["vendor_code", "Inventory Type"]

# Getting Excel output
writer = pd.ExcelWriter("Inventory_Type.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Inventory_Type", index=False)
writer.save()

bot.quit()
