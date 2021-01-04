#!/usr/bin/env python

import urllib.request
import json  
import zipfile  
import dask.dataframe as dd
from pymapd import connect
import pygeohash as pgh
import numpy as np

print('Beginning file download')

buildings = ['office', 'hotel', 'casino', 'self-storage', 'theater', 'warehouse', 'datacenter']


#url = 'https://crisisnlp.qcri.org/covid_data/geo_files/geo_2020-02-01.zip'
#url = 'https://crisisnlp.qcri.org/covid_data/geo_files/geo_2020-02-02.zip'
#urllib.request.urlretrieve(url, 'tweets/geo_2020-02-02.zip')

# with zipfile.ZipFile("./tweets/geo_2020-02-01.zip", "r") as z:
#     for filename in z.namelist():
#         print(filename)
#         with z.open(filename) as f:
#             print("Using for loop") 
#             for line in f:
#                 d = json.loads(line)
#                 if d['geo']:
#                     "gfsgdf".lower() 
#                 print("Line{line}") 

con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

data = []
i = 0
with zipfile.ZipFile("./tweets/allCountries.zip", "r") as z:
    for filename in z.namelist():
        print(filename)
        with z.open(filename) as f:
            print("Using for loop") 
            for line in f:
                # print(type(line))
                splits = line.decode("utf-8").split('\t')
                id = int(splits[0])
                name = splits[1]
                latitude = float(splits[4])
                longitude = float(splits[5])
                item = (id,     latitude, 
                                longitude, 
                                pgh.encode(latitude, longitude, precision=1),
                                pgh.encode(latitude, longitude, precision=2),
                                pgh.encode(latitude, longitude, precision=3),
                                pgh.encode(latitude, longitude, precision=4),
                                pgh.encode(latitude, longitude, precision=5),
                                pgh.encode(latitude, longitude, precision=6),
                                pgh.encode(latitude, longitude, precision=7),
                                pgh.encode(latitude, longitude, precision=8),
                                np.random.uniform(0, 5456),  # tsi
                                buildings[int(np.random.randint(len(buildings)))]
                                )
                data.append(item)
                if i % 100000 == 0:
                    print(f"i:{i}")
                    con.load_table('portfolios', data)
                    data.clear()
                    print("Data saved")
                i += 1
               




# with open('tweets/lat_lon_data.csv') as f:
#     print("Using for loop")
#     i = 0
#     for line in f:
#         if i >= 5000001:
#             break
#         if i > 0:
#             splits = line.split(',')
#             id = int(splits[0])
#             latitude = float(splits[1])
#             longitude = float(splits[2])
#             item = (id,     latitude, 
#                             longitude, 
#                             pgh.encode(latitude, longitude, precision=1),
#                             pgh.encode(latitude, longitude, precision=2),
#                             pgh.encode(latitude, longitude, precision=3),
#                             pgh.encode(latitude, longitude, precision=4),
#                             pgh.encode(latitude, longitude, precision=5),
#                             pgh.encode(latitude, longitude, precision=6),
#                             pgh.encode(latitude, longitude, precision=7),
#                             pgh.encode(latitude, longitude, precision=8),
#                             np.random.uniform(0, 5456),  # tsi
#                             buildings[int(np.random.randint(len(buildings)))]
#                              )
#             data.append(item)
#             if i % 100000 == 0:
#                 print(f"i:{i}")
#         i += 1





# df = dd.read_csv('tweets/lat_lon_data.csv')
# f = df.head()
# "adsa".lower()
