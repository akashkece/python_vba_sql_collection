import getpass
import json
import os
import sys

import PySimpleGUI as sg
from pandas import DataFrame, read_excel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def midway(chrome_instance, mid_pass, mid_usb_key):
    """Takes chrome instance as input and returns midway authenticated chrome instance
    """
    chrome_instance.get("https://midway.amazon.com")
    chrome_instance.find_element_by_id("user_name").send_keys(username)
    chrome_instance.find_element_by_id("password").send_keys(mid_pass)
    chrome_instance.find_element_by_id("verify_btn").send_keys(Keys.RETURN)
    WebDriverWait(chrome_instance, 10).until(
        EC.visibility_of_element_located((By.ID, "otp-field"))
    )
    chrome_instance.find_element_by_id("otp-field").send_keys(mid_usb_key)
    chrome_instance.find_element_by_id("otp-submit-btn").send_keys(Keys.RETURN)
    WebDriverWait(chrome_instance, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'akmarmu')]"))
    )
    if (
        chrome_instance.find_element_by_xpath(
            "//*[contains(text(), username)]"
        ).text.find("Hi " + username + ", you're authenticated")
        != -1
    ):
        return chrome_instance
    sys.exit(sg.popup("Midway Authentication Unsuccessful, Reset and start again"))


def getting_user_inputs():
    """
        Ask user for all the inputs required

        1. XLSX file with login IDs
        2. Midway related details

        returns 1. path to XLSX file
                2. midway password
                3. midway usb key
    """
    # Setting Layout
    layout = [
        [sg.Text("Select the xlsx file with login IDs", font=("Helvetica", 12))],
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
        [
            sg.Text(
                "This will provide all the details from phonetool",
                size=(60, 2),
                font=("Verdana", 8),
            )
        ],
    ]
    # Create the Window
    window = sg.Window("Phonetool Info Extractor", layout)
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
    # option.add_argument("--headless")
    # option.add_argument("--no-sandbox")
    # option.add_argument("--disable-gpu")
    return webdriver.Chrome(options=option)


def phonetool(user):
    """This function scraps the phonetool data"""
    global driver
    driver.get("https://phonetool.amazon.com/users/" + str(user) + ".json")
    html = driver.page_source
    html = html.replace(
        '<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">',
        "",
    ).replace("</pre></body></html>", "")

    try:
        html = json.loads(html)
        return [
            html["id"],
            html["login"],
            html["name"],
            html["first_name"],
            html["last_name"],
            html["department_number"],
            html["department_name"],
            html["job_title"],
            html["bar_raiser"],
            html["is_manager"],
            html["building"],
            html["city"],
            html["country"],
            html["phone_number"],
            html["mobile_number"],
            html["job_level"],
            html["hire_date"],
            html["tenure_days"],
            html["total_tenure_formatted"],
            html["manager"]["login"],
            len(html["direct_reports"]),
        ]
    except KeyError:
        return [
            "Not Found",
            user,
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
        ]
    except json.decoder.JSONDecodeError:
        return [
            "Bad Request",
            user,
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
            "Bad Request",
        ]


def file_values(filepath):
    global num_agid
    # Reading the input file and printing number of unique agreement IDs
    ds = read_excel(filepath, sheet_name=0, usecols="A")
    ds = ds.iloc[:, 0]
    ds = ds.drop_duplicates()  # Removing duplicate agreement IDs
    num_agid = len(ds)
    # Changing Directory to input_file directory, creating a folder agreement
    os.chdir(os.path.dirname(os.path.abspath(filepath)))
    return ds


# Program starting here
username = getpass.getuser()
filepath, mid_password, mid_usb_key = getting_user_inputs()
driver = midway(chrome(), mid_password, mid_usb_key)
phonetool_data = DataFrame(
    columns=[
        "emp_id",
        "login_id",
        "name",
        "first_name",
        "last_name",
        "department_id",
        "department_name",
        "job_title",
        "is_bar_raiser",
        "is_manager",
        "building",
        "city",
        "country",
        "phone_number",
        "mobile_number",
        "job_level",
        "hire_date",
        "tenure_days",
        "total_tenure_formatted",
        "manager",
        "people_managing",
    ]
)


def main():
    global phonetool_data
    users = file_values(filepath)

    for i in range(len(users)):
        phonetool_data.loc[i] = phonetool(users[i])

    phonetool_data.to_csv("phonetool_results.csv", index=False)
    driver.quit()


if __name__ == "__main__":
    main()
