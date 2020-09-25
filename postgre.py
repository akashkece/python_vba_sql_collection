# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 16:24:50 2019

@author: akmarmu
"""

import psycopg2
import pandas as pd
import numpy as np

con = psycopg2.connect(
    "dbname=test port=5432 user=" + "postgres" + " password=" + "123"
)

cursor = con.cursor()
cursor.execute("SELECT * FROM car")
# Getting query results into vendor_all dataframe
vendor_all = pd.DataFrame(np.array(cursor.fetchall()))
vendor_all.columns = [i[0] for i in cursor.description]
