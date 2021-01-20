#!/usr/bin/env python


import zipfile
from pymapd import connect
import pygeohash as pgh
import numpy as np

import pandas as pd
import geopandas
import glob
import swifter
import time
from sklearn.datasets import make_regression
from sklearn.datasets import make_blobs
from sklearn.datasets import make_low_rank_matrix
import random
from shapely.geometry import Point


def generateGeohashesNew(row):

    geohash = pgh.encode(row['Latitude'], row['Longitude'], precision=8)

    return pd.Series(
        [
            geohash[0:1],
            geohash[0:2],
            geohash[0:3],
            geohash[0:4],
            geohash[0:5],
            geohash[0:6],
            geohash[0:7],
            geohash
        ])


def generateGeohashes(df):
    g1s, g2s, g3s, g4s, g5s, g6s, g7s, g8s = [], [], [], [], [], [], [], []

    for index, row in df.iterrows():
        geohash = pgh.encode(row['Latitude'], row['Longitude'], precision=8)
        g1s.append(geohash[0:1])
        g2s.append(geohash[0:2])
        g3s.append(geohash[0:3])
        g4s.append(geohash[0:4])
        g5s.append(geohash[0:5])
        g6s.append(geohash[0:6])
        g7s.append(geohash[0:7])
        g8s.append(geohash[0:8])

        if index % 100000 == 0:
            print(f"generateGeohashes {index}")

    df_result = pd.DataFrame({'geohash_1': g1s,
                              'geohash_2': g2s,
                              'geohash_3': g3s,
                              'geohash_4': g4s,
                              'geohash_5': g5s,
                              'geohash_6': g6s,
                              'geohash_7': g7s,
                              'geohash_8': g8s,
                              })

    return df_result


def read_csv(file):
    df = pd.read_csv(file, sep=';',
                     encoding="utf-8",
                     usecols=['ID',
                              'CountryCode',
                              "Latitude",
                              "Longitude",
                              "Income Group", "TSI Group", "Sum Insured", "Has Losses", "Losses", "Building Type", "Sample Rating"],
                     dtype={
                         'ID': np.int,
                         'Latitude': np.float,
                         'Longitude': np.float,
                         'Income Group': np.int32,
                         'Sum Insured': np.float,
                         'Has Losses': np.bool,
                         'Losses': np.float,
                         'CountryCode': np.str
                     }
                     )

    df.rename(columns={
        'Income Group': 'Income_Group',
        'TSI Group': 'TSI_Group',
        'Sum Insured': 'Sum_Insured',
        'Has Losses': 'Has_Losses',
        'Building Type': 'Building_Type',
        'Sample Rating': 'Sample_Rating'
    }, inplace=True)

    return df


def gen_array(size, parts):
    result = np.array([], dtype=np.int16)
    for index, p in enumerate(parts):
        count = int(size / 100 * p)
        a = np.full(count, index + 1, dtype=np.int16)
        result = np.append(result, a)

    # add 10 procent
    count = int(size / 100 * 10)
    a = np.full(count, 1, dtype=np.int16)
    result = np.append(result, a)

    result = result[:size]

    # np.random.shuffle(result)

    print(result)
    print(len(result))
    print(type(result))

    return result


for filename in glob.glob('data/portfolios/*100k*.csv'):
    print(f'read file {filename}')
    df = read_csv(filename)

    print(f'dataset has: {df.size}')

    # print(df.head())
    # print(df.dtypes)

    portfolioName = filename.split('/')[-1]

    df.insert(0, 'PortfolioName', portfolioName)
    df.insert(1, 'LayerId', np.random.randint(1, 21, size=len(df.index)))
    # df.insert(2, 'parent_layer_id', np.random.randint(1, 21, size=len(df.index)))

    # df.loc[df['LayerId'] == 1, 'parent_layer_id'] = -1

    # r = Point(150, 60)
    # print(r)

    # coors: pd.Series = df.swifter.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    # test = coors.to_list()

    # s = geopandas.GeoSeries(test)
    # print(s)

    # #import shapely
    # print(coors.head())

    # df.insert(6, 'coor', s)

    print('calculate geohash')

    start = time.time()
    df[[
        'geohash_1',
        'geohash_2',
        'geohash_3',
        'geohash_4',
        'geohash_5',
        'geohash_6',
        'geohash_7',
        'geohash_8'
    ]] = df.swifter.apply(lambda row: generateGeohashesNew(row), axis=1)

    print(f"Duration: {time.time() - start}")
    print(df.dtypes)
    print(df.head())

    # df['geohash_8'] = df.swifter.apply(lambda row: pgh.encode(row['Latitude'], row['Longitude'], precision=8), axis=1)

    # df['geohash_2'] = df[['geohash_8']].apply(lambda l8: l8[0:2], axis=1)

    # df['geohash_1'] = df.swifter.apply(lambda row: row['geohash_8'][0:1], axis=1)
    # df['geohash_2'] = df.swifter.apply(lambda row: row['geohash_8'][0:2], axis=1)
    # df['geohash_3'] = df.swifter.apply(lambda row: row['geohash_8'][0:3], axis=1)
    # df['geohash_4'] = df.swifter.apply(lambda row: row['geohash_8'][0:4], axis=1)
    # df['geohash_5'] = df.swifter.apply(lambda row: row['geohash_8'][0:5], axis=1)
    # df['geohash_6'] = df.swifter.apply(lambda row: row['geohash_8'][0:6], axis=1)
    # df['geohash_7'] = df.swifter.apply(lambda row: row['geohash_8'][0:7], axis=1)

    # df['earthquake'] =  np.random.randint(
    #     1, 5, size=len(df.index), dtype=np.int16)

    df['earthquake'] = gen_array(len(df.index), [25, 50, 5, 20])

    #df['hail'] = np.random.randint(1, 7, size=len(df.index), dtype=np.int16)
    df['hail'] = gen_array(len(df.index), [35, 15, 8, 2, 10, 30])
    # df['heat_wave'] = np.random.randint(
    #     1, 4, size=len(df.index), dtype=np.int16)
    df['heat_wave'] = gen_array(len(df.index), [60, 30, 10])

    #df['tornado'] = np.random.randint(1, 6, size=len(df.index), dtype=np.int16)
    df['tornado'] = gen_array(len(df.index), [10, 30, 40, 5, 15])

    print('save data to file')
    df.to_feather(f"data/portfolios/{portfolioName}_geohashes.feather")
    #con.load_table("portfolios2", df)
