#!/usr/bin/env python


import zipfile  
from pymapd import connect
import pygeohash as pgh
import numpy as np


buildings = ['office', 'hotel', 'casino', 'self-storage', 'theater', 'warehouse', 'datacenter']


con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

data = []
i = 0
with zipfile.ZipFile("./data/allCountries.zip", "r") as z:
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
               


