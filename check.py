import json

# import PySimpleGUI as sg
from pandas import DataFrame, read_excel
from selenium import webdriver


option = webdriver.ChromeOptions()
option.add_argument("--ignore-certificate-errors")
option.add_argument("--ignore-ssl-errors")
option.add_argument("--safebrowsing-disable-download-protection")
option.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=option)

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

users = read_excel("logins.xlsx")
for i in range(len(users)):
    driver.get("https://phonetool.amazon.com/users/" + users.iat[i, 0] + ".json")
    html = driver.page_source
    html = html.replace(
        '<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">',
        "",
    ).replace("</pre></body></html>", "")
    html = json.loads(html)





    phonetool_data.loc[i] = phonetool(users.iat[i, 0])

def phonetool(user):
    """This function scraps the phonetool data"""
    global driver
    bot.get("https://phonetool.amazon.com/users/" + user + ".json")
    html = bot.page_source
    html = html.replace(
        '<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">',
        "",
    ).replace("</pre></body></html>", "")

    html = json.loads(html)

    try:
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


phonetool_data.to_csv("phonetool_results.csv", index=False)
driver.quit()
