from myown.filter import create_filter_where
from myown.dbutils import calcLevel, createWhere, count_rows, createCollection

import numpy as np
import pandas as pd

import psycopg2
import time


class Postg:

    # default constructor
    def __init__(self):
        self.con = psycopg2.connect(
            host="localhost",
            database="geo",
            user="postgres",
            password="example",
        )

    def clusterGeohash(self, where):

        start = time.time()

        geohash_level = calcLevel(self.con, where, thresholdMin=5000, thresholdMax=7000)

        query = f"""select
                        avg(Latitude) AS lat,
                        avg(Longitude) AS lon,
                        count(*) AS pcount,
                        sum(Sum_Insured) AS tsi
                    FROM portfolios
                    WHERE {where}
                    GROUP BY geohash_{geohash_level}
                    """

        df = pd.read_sql(query, self.con)
        # df = self.con.select_ipc(query)

        items = df.values.tolist()

        end = time.time()
        duration = end - start

        # print(items)
        return items, duration

    def request(self, portfolio, zoom, extent, scale, filter):

        where = createWhere(portfolio, extent, filter)
        count = count_rows(self.con, where)

        print(f"count {count}")

        maxSingePoints = 250

        points = []
        duration = 12346879.0
        if count > maxSingePoints:
            points, duration = self.clusterGeohash(where)
        else:
            points = self.createNoCluster(where)

        collection = createCollection(points)
        result = dict(items=collection, duration=duration)
        return result
