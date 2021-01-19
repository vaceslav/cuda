#!/usr/bin/env python


import zipfile
from numpy.lib.function_base import insert
from pymapd import connect
import pygeohash as pgh
import numpy as np

import pandas as pd
import glob
import swifter
from shapely.geometry import Point
import geopandas


con = connect(user="admin", password="HyperInteractive",
              host="localhost", dbname="omnisci")


for filename in glob.glob('data/portfolios/*5m*.feather'):
    print(f'read file {filename}')
    df: pd.DataFrame = pd.read_feather(filename)

    # coors: pd.Series = df.swifter.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    # test = coors.to_list()
    # s = geopandas.GeoSeries(test)
    # df.insert(6, 'coor',  s)

    print(df.head())

    print(df.dtypes)

    for i in range(1):
        print(f"loop: {i}")

        portfolioNmae = f"{filename.split('/')[-1].split('.')[0]}_{i}"

        df['PortfolioName'] = portfolioNmae

        print('save data to db')
        #con.load_table_columnar("portfolios", df,  preserve_index=False)
        con.load_table("portfolios", df)
