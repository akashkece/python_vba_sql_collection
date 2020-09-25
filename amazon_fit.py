# Importing packages
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)


print("\n\n")


def chrome():
    """
    This function returns a chrome instance
    """
    option = webdriver.ChromeOptions()
    option.add_argument("--ignore-certificate-errors")
    option.add_argument("--ignore-ssl-errors")
    option.add_argument("--safebrowsing-disable-download-protection")
    return webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=option)


def fit(asin):

    try:
        driver.get("https://www.amazon.com/dp/" + asin)
        time.sleep(5)
        driver.find_element_by_xpath("//*[@id = 'fitRecommendationsSection']").click()
        grabbed_element = driver.find_element_by_xpath(
            "//*[@id = 'fitRecommendationsSupportingStatement']/following::*[@id = 'fitRecommendationHistogramTable']"
        ).text
        rt = re.findall(r"\n([,0-9]+)", grabbed_element)
        return rt

    except NoSuchElementException:
        try:
            driver.get("https://www.amazon.com/dp/" + asin)
            time.sleep(5)
            driver.find_element_by_xpath("//*[@id = 'pers_fit_link']").click()
            driver.find_element_by_xpath("//*[contains(text(),'Fit reviews')]").click()
            rt = re.findall(
                r"\n([,0-9]+)",
                driver.find_element_by_xpath(
                    "//*[@id = 'fitRecommendationHistogramTable']"
                ).text,
            )
            return rt
        except NoSuchElementException:
            try:
                driver.get("https://www.amazon.com/dp/" + asin)
                time.sleep(5)
                driver.find_element_by_xpath("//*[@id = 'HIF_link']").click()
                driver.find_element_by_xpath(
                    "//*[contains(text(),'Fit reviews')]"
                ).click()
                rt = re.findall(
                    r"\n([,0-9]+)",
                    driver.find_element_by_xpath(
                        "//*[@id = 'fitRecommendationHistogramTable']"
                    ).text,
                )
                return rt
            except NoSuchElementException:
                return ["Error", "Error", "Error", "Error", "Error"]
            except ElementClickInterceptedException:
                return ["click", "click", "click", "click", "click"]
            except:
                return ["others", "others", "others", "others", "others"]
        except ElementClickInterceptedException:
            return ["click", "click", "click", "click", "click"]
        except:
            return ["others", "others", "others", "others", "others"]

    except ElementClickInterceptedException:
        return ["click", "click", "click", "click", "click"]
    except:
        return ["others", "others", "others", "others", "others"]


start_time = time.time()
print(f"start time: {time.strftime('%x %X')}")
print("")

print("Reading the file, may take few minutes...........")
ds = pd.read_csv(r"C:\Users\akmarmu\Documents\python_projects\fit_analysis\asins.csv")
ds = ds.iloc[:, 0]
ds = ds.drop_duplicates()
print("\n", "Total unique ASINs to check: ", len(ds), "\n", end="\n \n")
driver = chrome()

hi = ds.apply(fit)

driver.quit()
ds = pd.concat([ds, hi], axis=1)
ds.to_csv("result.csv", index=True)

end_time = time.time()
minutes = (end_time - start_time) // 60
seconds = (end_time - start_time) % 60
print(f"end time: {time.strftime('%x %X')}")
print(
    f"Approx. time taken to get all the values: {round(minutes)} minutes {round(seconds)} seconds"
)
