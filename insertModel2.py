#!/usr/bin/env python


import zipfile  
from pymapd import connect
import pygeohash as pgh
import numpy as np

import pandas as pd
import glob
import swifter


con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

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
                    encoding = "utf-8", 
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


def create_layers():
    layers = pd.DataFrame({
        "Id": list(range(1, 20+1)),                                   
        "ParentLayerId": [np.NaN, 1, 1, 2, 2, 2, 3, 3, 4, 5, 5, 6, 6, 6, 6, 7, 7, 8, 8, 8]
    })

    # layers.loc[0, "ParentLayerId"] = None

    layers["ParentLayerId"] = layers["ParentLayerId"].astype(np.float32)

    layers.insert(1, "LayerName", layers.apply(lambda row: f"Layer_{row['Id']}", axis=1))

    con.load_table("model2layers", layers)

    print(layers)
    print(layers.dtypes)


filename = "data/portfolios/FAB_SampleLocations_100k.csv_done"
print(f'read file {filename}')
df = read_csv(filename)

print(f'dataset has: {len(df.index)}')

# print(df.head())
# print(df.dtypes)

df.insert(1, 'LayerId', np.random.randint(1, 21, size=len(df.index)))

print('calculate geohash')
df['geohash_8'] = df.swifter.apply(lambda row: pgh.encode(row['Latitude'], row['Longitude'], precision=8), axis=1)
df['geohash_1'] = df.swifter.apply(lambda row: row['geohash_8'][0:1], axis=1)
df['geohash_2'] = df.swifter.apply(lambda row: row['geohash_8'][0:2], axis=1)
df['geohash_3'] = df.swifter.apply(lambda row: row['geohash_8'][0:3], axis=1)
df['geohash_4'] = df.swifter.apply(lambda row: row['geohash_8'][0:4], axis=1)
df['geohash_5'] = df.swifter.apply(lambda row: row['geohash_8'][0:5], axis=1)
df['geohash_6'] = df.swifter.apply(lambda row: row['geohash_8'][0:6], axis=1)
df['geohash_7'] = df.swifter.apply(lambda row: row['geohash_8'][0:7], axis=1)
#print(df.head())
#geohashcols = generateGeohashes(df)
#print('join geohashes')
#df = df.join(geohashcols)

df.to_csv(path_or_buf="data/portfolios/FAB_SampleLocations_100k_geohashes.csv", index=False)
df.to_feather("data/portfolios/FAB_SampleLocations_100k_geohashes.feather")

print('save data to db')
#con.load_table("model2locations", df)




