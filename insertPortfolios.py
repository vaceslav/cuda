#!/usr/bin/env python


import zipfile
from pymapd import connect
import pygeohash as pgh
import numpy as np

import pandas as pd
import glob
import swifter


con = connect(user="admin", password="HyperInteractive",
              host="localhost", dbname="omnisci")


for filename in glob.glob('data/portfolios/*.feather'):
    print(f'read file {filename}')
    df: pd.DataFrame = pd.read_feather(filename)

    # print(df.head())

    # print(df.dtypes)

    for i in range(1):
        print(f"loop: {i}")

        portfolioNmae = f"{filename.split('/')[-1].split('.')[0]}_{i}"

        df['PortfolioName'] = portfolioNmae

        print('save data to db')
        con.load_table("portfolios", df)
