# Importing required libraries
import concurrent.futures
import re
import time

import pandas as pd
import requests

# Recording code execution start time
start_time = time.time()
print(f"start time: {time.strftime('%x %X')}")

# Reading asins from excel file and creating a list
asins = pd.read_excel("asins.xlsx")
asins.columns = ['asins']
asins = asins['asins'].to_list()

# Creating variable with url initial text
url_part = 'https://www.amazon.com/gp/customer-reviews/widgets/average-customer-review/popover/ref=dpx_acr_pop_' \
           '?contextId=dpx&asin='

# Creating compiled regular expression objects
ratings_pattern = re.compile(r"[1-5][.]?[0-9]? out of 5")
reviews_pattern = re.compile(r"[0-9,]+  customer ratings")

# Creating empty lists to hold the results and asins with error
error_list, result_list = ([], [])


def reviews_ratings(asin):
    """
    This takes an asin as argument and returns ratings and reviews of that asin
    """
    url = url_part + asin
    try:
        f = requests.get(url)
        if f.status_code == 200:
            ratings = ratings_pattern.findall(str(f.content))[0]
            reviews = reviews_pattern.findall(str(f.content))[0]
            result_list.append([asin, ratings, reviews])
        else:
            error_list.append(str(asin))
    except IndexError:
        error_list.append(asin)


# Using Threadpool for implementing multithreading
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(reviews_ratings, asins)

# exporting result
result_list = pd.DataFrame(result_list)
result_list.columns = ['asin', 'rating', 'NumOfReviews']
result_list.to_csv("reviews_ratings.csv", index=False)
if len(error_list) == 0:
    pass
else:
    error_list = pd.DataFrame(error_list)
    error_list.columns = ["failed_asin"]
    error_list.to_csv("failed_asins.csv", index=False)


# Recording code execution end time and calculating total execution time
end_time = time.time()
minutes = (end_time - start_time) // 60
seconds = (end_time - start_time) % 60
print(f"end time: {time.strftime('%x %X')}")
print(f"Time taken to get details of {len(asins)} the asins : {round(minutes)} minutes {round(seconds)} seconds")

#input()


