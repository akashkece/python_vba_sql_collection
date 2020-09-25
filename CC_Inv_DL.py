# Importing Libraries
import getpass
import glob
import math
import os
import re
import shutil
import sys
import time

from bs4 import BeautifulSoup
import pandas as pd
import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sg.change_look_and_feel("random_theme")
driver = 0
n = 0
username = getpass.getuser()
num_agid = 0


def getting_user_inputs():
    """
        Ask user for all the inputs required

        1. XLSX file with agreement ID
        2. Midway related details

        returns 1. path to XLSX file
                2. midway password
                3. midway usb key
    """
    # Setting Layout
    layout = [
        [sg.Text("Select the xlsx file with agreement IDs", font=("Helvetica", 12))],
        [sg.In(key="filepath"), sg.FileBrowse()],
        [
            sg.Text(
                "****************************************************************************************"
            )
        ],
        [
            sg.Text(
                "Enter Midway Authentication Details",
                justification="Centre",
                font=("Helvetica", 15),
            )
        ],
        [
            sg.Text("Enter midway password"),
            sg.InputText(key="mid_pass", default_text="", password_char="*"),
        ],
        [
            sg.Text("Press your usb Token key"),
            sg.InputText(key="mid_usb_key", default_text="", password_char="*"),
        ],
        [
            sg.Text(
                "****************************************************************************************"
            )
        ],
        [
            sg.Button("Submit"),
            sg.Cancel(button_text="Exit"),
            sg.Button("Reset all values"),
        ],
        [
            sg.Text(
                "****************************************************************************************"
            )
        ],
        [sg.Text("When this macro is running do not download any zip file or delete any zip file from Downloads folder",
                 size=(60, 2), font=("Verdana", 8))],
    ]
    # Create the Window
    window = sg.Window("Contra Cogs Invoice Download", layout)
    # Event Loop to process "events"
    while True:
        event, values = window.read()
        if event == "EXIT" or event is None:
            break  # exit button clicked
        elif event == "Submit":
            if (
                    values["filepath"] == ""
                    or values["mid_pass"] == ""
                    or values["mid_usb_key"] == ""
            ):
                sg.popup("You need to fill all three values or Exit")
            else:
                return values["filepath"], values["mid_pass"], values["mid_usb_key"]
        elif event == "Reset all values":
            window["filepath"].update("")
            window["mid_pass"].update("")
            window["mid_usb_key"].update("")
        else:
            break


def chrome():
    """
    This function returns a chrome instance
    """
    option = webdriver.ChromeOptions()
    option.add_argument("--ignore-certificate-errors")
    option.add_argument("--ignore-ssl-errors")
    option.add_argument("--safebrowsing-disable-download-protection")
    option.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=option)


def midway(chrome_instance, mid_pass, mid_usb_key):
    """Takes chrome instance as input and returns midway authenticated chrome instance
    """
    chrome_instance.get("https://midway.amazon.com")
    chrome_instance.find_element_by_id("user_name").send_keys(username)
    chrome_instance.find_element_by_id("password").send_keys(mid_pass)
    chrome_instance.find_element_by_id("verify_btn").send_keys(Keys.RETURN)
    WebDriverWait(chrome_instance, 10).until(EC.visibility_of_element_located((By.ID, "otp-field")))
    chrome_instance.find_element_by_id("otp-field").send_keys(mid_usb_key)
    chrome_instance.find_element_by_id("otp-submit-btn").send_keys(Keys.RETURN)
    WebDriverWait(chrome_instance, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                             "//*[contains(text(),'akmarmu')]")))
    if chrome_instance.find_element_by_xpath('//*[contains(text(), username)]').text\
            .find("Hi " + username + ', you\'re authenticated') != -1:
        return chrome_instance
    sys.exit(sg.popup("Midway Authentication Unsuccessful, Reset and start again"))


def file_values(filepath):
    global num_agid
    # Reading the input file and printing number of unique agreement IDs
    ds = pd.read_excel(filepath, sheet_name=0, usecols="A")
    ds = ds.iloc[:, 0]
    ds = ds.drop_duplicates()  # Removing duplicate agreement IDs
    num_agid = len(ds)
    # Changing Directory to input_file directory, creating a folder agreement
    os.chdir(os.path.dirname(os.path.abspath(filepath)))
    if not os.path.exists("agreement"):
        os.makedirs("agreement")
    return ds


def number_of_invoices(agreement_id):
    """returns number of invoices in a agreement ID. 
    Checking for all types of invoices like transaction.DAT, summary.xls, transaction.xls
    """
    global driver
    # Opening the contracogs link
    driver.get(
        "https://contra-cogs.aka.amazon.com/agreements/"
        + str(agreement_id)
        + "/booking-and-billing"
    )

    try:
        # Waiting for upto 50 seconds for page to display Booking and Billing Details
        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[text() = 'Booking and Billing Details']")
            )
        )
    except TimeoutException:
        return "TimeOut Error"
    except NoSuchElementException:
        return "Not able to find Agreement Id"
    except IndexError:
        return "Unknown Error"
    try:
        # It may take few seconds for invoices to load, waiting for 5 seconds
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[text() = 'Back Up Reports']")
            )
        )
        noi = int(
            re.findall(
                r"([0-9]+) amounts",
                driver.find_element_by_xpath(
                    "(//div['non-collapsed'][contains(text(),'Reports')]//following::*)[6]"
                ).text,
            )[0]
        )
    except NoSuchElementException:
        noi = 0
    except TimeoutException:
        noi = 0
    return noi


def create_agreement_folder(agreement_id):
    if not os.path.exists("agreement\\" + str(agreement_id)):
        os.makedirs("agreement\\" + str(agreement_id))
    else:
        files = glob.glob("agreement\\" + str(agreement_id) + "\\" + "*.zip")
        for f in files:
            os.remove(f)


def current_page():
    global driver
    # Getting the invoice table from contra cogs page
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    tab_data = soup.select("table")[3]

    # Creating Empty lists and appending the invoice table and invoice download links in them
    dataset = []
    links = []
    for items in tab_data.select("tr"):
        item = [elem.text for elem in items.select("th,td")]  # For invoice table
        dataset.append(", ".join(item))
        clr = [elm for elm in items.select("a")]  # For links table
        links.append(str(clr))

    # Changing list to dataframes and expanding to multiple columns
    dataset = pd.DataFrame.from_dict({'data': dataset})
    dataset = pd.concat(
        [dataset.data.str.split(", ", expand=True)], axis=1
    )  # Expanding to multiple columns
    links = pd.DataFrame.from_dict({'Links': links})
    links.columns = ["Links"]

    # Merging both dataframes
    dataset = pd.concat([dataset, links], axis=1, join="inner")

    # Creating new column name as concatenation of three columns from invoice table and word 'zip'
    dataset.columns = ["InvoiceId", "Period", "ReportType", "DownloadButton", "Links"]
    dataset["name"] = (
            dataset["InvoiceId"] + dataset["Period"] + dataset["ReportType"] + [".zip"]
    )
    dataset = dataset.replace(
        {" {2,9}": "-"}, regex=True
    )  # Replacing more than 1 space with a '-'
    dataset = dataset.replace(
        {"-+": "-"}, regex=True
    )  # Replacing multiple '-' to single '-'
    dataset = dataset.replace({" ": ""}, regex=True)  # Removing all single spaces
    dataset = dataset[
        ~dataset.Period.str.contains("Period")
    ]  # Removing first row which is actually the title from invoice table.
    # Removing extra data from links and keeping actual link only
    dataset = dataset.replace({r'\[<ahref="': ""}, regex=True)
    dataset = dataset.replace("\\n", "", regex=True)
    dataset = dataset.replace({'"target="_blank">Download</a>]': ""}, regex=True)

    # Keeping only two columns name and Links in final dataset
    return dataset.filter(["name", "Links"])


def invoice_download(dataset, noi, agreement_id):
    global driver, username
    for invoice in range(noi):
        zip_files = glob.glob(
            "C:/Users/" + username + "/Downloads/*.zip"
        )  # Checkin the count of zip files before download
        driver.find_element_by_tag_name("body").send_keys(
            Keys.CONTROL + "t"
        )  # Starting a new chrome tab
        driver.get(
            dataset.iat[invoice, 1]
        )  # Downloading the invoice url in second tab
        # Will wait upto 100 seconds
        test = 0
        while (
                len(zip_files) == len(glob.glob("C:/Users/" + username + "/Downloads/*.zip"))
                and test < 100
        ):
            time.sleep(1)
            test += 1
        if test == 100:
            pass
        zip_files = glob.glob("C:\\Users\\" + username + "\\Downloads\\*.zip")
        os.rename(
            max(zip_files, key=os.path.getctime),
            "agreement\\" + str(agreement_id) + "\\" + dataset.iat[invoice, 0],
        )


def download_decision(agreement_id):
    """
    This function will check if there are any invoice to download from contracogs or not for  'agreement_id'.
    If there is any invoice to download it will create agreement ID folder and download those invoices to this folder
    """
    global driver
    noi = number_of_invoices(agreement_id)

    # Display Progress Bar
    global n, num_agid
    sg.OneLineProgressMeter('Progress Bar', n, num_agid, 'key',
                            str(noi) + ' invoices in current agreement ID\n\nNumber of Agreement IDs completed')
    n += 1

    try:
        noi = int(noi)
        if noi == 0:
            pass
        elif 0 < noi < 999:
            create_agreement_folder(agreement_id)
            pages = math.ceil(noi / 20)
            dataset = pd.DataFrame(columns=["name", "Links"])
            while pages > 1:
                dataset = pd.concat([dataset, current_page()])
                driver.find_elements_by_class_name("forward-end-arrow")[1].click()
                pages -= 1
            dataset = pd.concat([dataset, current_page()])
            invoice_download(dataset, noi, agreement_id)
        else:
            pass
    except ValueError as verr:
        noi = str(noi) + " Value Error: " + str(verr)
    except TypeError as terr:
        noi = str(noi) + " Type Error: " + str(terr)

    return noi


def main():
    global driver, username
    filepath, mid_password, mid_usb_key = getting_user_inputs()
    driver = midway(chrome(), mid_password, mid_usb_key)
    ds = file_values(filepath)
    num_invoices = ds.apply(download_decision)
    df = pd.concat([ds, num_invoices], axis=1)
    df.columns = ["AgreementIds", "No. of Invoices"]

    # Closing Chrome
    driver.quit()

    # Getting Excel and ZIP output
    df.to_excel("Invoices_Download_Result.xlsx", sheet_name="Invoice Count", index=False)
    shutil.make_archive("agreement", "zip", "agreement")


if __name__ == "__main__":
    main()
