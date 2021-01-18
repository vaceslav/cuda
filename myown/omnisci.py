#!/usr/bin/env python


from cudf.core import dataframe
from pymapd import connect
import cudf
from cuml.cluster import KMeans


import numpy as np
import pandas as pd
import hdbscan
from pyproj import Proj, transform
import time
from datashader.utils import lnglat_to_meters as webm

from myown.filter import create_filter_where
from myown.dbutils import calcLevel, createWhere, count_rows, createCollection


class Omnisci:

    # default constructor
    def __init__(self):
        self.con = connect(
            user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

    def buildCluster(self, subset):
        kmeans = KMeans(n_clusters=30, max_iter=20, init='scalable-k-means++')
        kmeans.fit(subset)

        return (kmeans.cluster_centers_.astype('float64'), kmeans.labels_)

    def createClusterKMEans(self, where, geohash_level):

        query = f"""select
                        lat,
                        lon,
                        1 AS pcount
                        from portfolios
                    where {where}"""

        if geohash_level != None:
            query = f"""select
                        avg(lat) AS lat,
                        avg(lon) AS lon,
                        count(*) AS pcount
                    from portfolios
                    where {where}
                    group by geohash_{geohash_level}
                    """

        df = self.con.select_ipc_gpu(query)
        # cursor = self.con.execute(query)
        # only_points = df.drop(['tree_dbh', 'user_type'])

        subset = df[['lat', 'lon']]
        (cluster, labels) = self.buildCluster(subset)

        df['cluster_id'] = labels
        print(df)
        group = df.groupby(['cluster_id']).sum()
        print(group)
        print(cluster)

        clusterDf = pd.DataFrame(cluster, columns=['lat', 'lon'])
        print(clusterDf)
        clusterDf['count'] = group['pcount']
        print(clusterDf)
        items = clusterDf.values.tolist()
        print(items)

        # kmeans.fit(df)

        # print(kmeans.cluster_centers_)

        # result = list(currso)

        # print(type(cluster))

        return items

    def createClusterHDBScan(self, where, geohash_level, scale):
        query = f"""select
                    avg(lat) AS lat,
                    avg(lon) AS lon,
                    count(*) AS pcount
                from portfolios
                where {where}
                group by geohash_{geohash_level}
                """

        df = self.con.select_ipc(query)
        subset = df[['lat', 'lon']]

        print(subset)
        rad = np.radians(subset)
        print(rad)

        earth_radius_km = 6371
        epsilon = scale / 1000 / earth_radius_km  # calculate 5 meter epsilon threshold

        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='haversine',
                                    cluster_selection_epsilon=epsilon, cluster_selection_method='eom')

        # clusterer = hdbscan.HDBSCAN(metric='haversine')

        clusterer.fit_predict(subset)

        print(clusterer.labels_)
        df['cluster_id'] = clusterer.labels_
        print(df)
        groupSum = df.groupby(['cluster_id']).sum()
        print(groupSum)

        groupAvg = df.groupby(['cluster_id']).mean()
        print(groupAvg)

        result = pd.DataFrame(groupAvg, columns=['lat', 'lon'])
        result['count'] = groupSum['pcount']

        print(result)
        items = result.values.tolist()
        print(items)

        return items

        # x = np.array(clusterer.labels_)
        # unique, counts = np.unique(x, return_counts=True)
        # print(unique)
        # print(f'cluster count: {len(clusterer.labels_)}')

    def createCluster(self, where, scale):
        # return self.createClusterHDBScan(where, geohash_level, scale)
        # return self.createClusterKMEans(where, geohash_level)
        return self.clusterGeohash(where)

    def createNoCluster(self, where):
        query = f"""select
                        lat,
                        lon,
                        1 as pcount
                    from portfolios
                    where {where}"""

        df = self.con.select_ipc(query)
        # cursor = self.con.execute(query)
        # only_points = df.drop(['tree_dbh', 'user_type'])

        # subset = df[['lat', 'lon']]
        return df.values.tolist()

    def clusterGeohash(self, where):

        start = time.time()

        geohash_level = calcLevel(self.con, where, thresholdMin=5000, thresholdMax=7000)

        # buildingQuery = f"SELECT building, KEY_FOR_STRING(building), COUNT(*) from portfolios where {where}  GROUP BY building"

        # buildingGroupCursor = self.con.execute(buildingQuery)

        # buildingGroup = list(buildingGroupCursor)

        # KEY_FOR_STRING(building) AS building,
        #                 KEY_FOR_STRING(geohash_{geohash_level}) AS geohash

        query = f"""select
                        avg(Latitude) AS lat,
                        avg(Longitude) AS lon,
                        count(*) AS pcount,
                        sum(Sum_Insured) AS tsi
                    FROM portfolios
                    WHERE {where}
                    GROUP BY geohash_{geohash_level}
                    """
        df = self.con.select_ipc(query)

        # avg =  df.groupby(['geohash']).mean().values.tolist()
        # step1 = df.groupby(['geohash'])
        # step2 = step1['building']
        # #step3 = step2.apply(lambda x: list(np.unique(x)))
        # step3 = step2.agg(['unique'])
        #         .nunique().values.tolist()
        # nunique =  df.groupby(['geohash']).nunique().values.tolist()

        items = df.values.tolist()

        end = time.time()
        duration = end - start

        # print(items)
        return items, duration

    def request(self, portfolio, zoom, extent, scale, filter):

        # query = "SELECT tree_dbh, user_type, longitude, latitude FROM nyc_trees_2015_683k ORDER BY created_at limit 100000"
        #query = "SELECT longitude, latitude FROM nyc_trees_2015_683k"

        where = createWhere(portfolio, extent, filter)
        count = count_rows(self.con, where)

        #is_point_in_merc_view(lon, lat, {extent})

        print(f"count {count}")

        maxSingePoints = 250

        points = []
        duration = 12346879.0
        if count > maxSingePoints:
            points, duration = self.createCluster(where, scale)
        else:
            points = self.createNoCluster(where)

        # collection = createCollection(cluster.values.tolist())
        collection = createCollection(points)
        result = dict(items=collection, duration=duration)
        return result

    def requestImage(self, portfolio, extent, width, height, filter):

        extent_splt = extent.split(',')

        extent_splt = list(map(float, extent_splt))

        minLong, minLat = extent_splt[0], extent_splt[1]
        maxLong, maxLat = extent_splt[2], extent_splt[3]

        minLong, minLat = webm(minLong, minLat)
        maxLong, maxLat = webm(maxLong, maxLat)

        where = createWhere(portfolio, extent, filter)

        # inProj = Proj('epsg:3857')
        # outProj = Proj('epsg:4326')
        # minLong, minLat = transform(inProj, outProj, minLong, minLat)
        # maxLong, maxLat = transform(inProj, outProj, maxLong, maxLat)

        # where = f"""
        #                 lon >= {minLong} AND
        #                 lat >= {minLat} AND
        #                 lon <= {maxLong} AND
        #                 lat <= {maxLat}
        #           """

        #is_point_in_merc_view(lon, lat, {extent})
        with open('myown/vega.json', 'r') as file:
            vegaRequest = file.read()
            vegaRequest = vegaRequest.replace('{WHERE}', where).replace('{MIN_LONG}', str(minLong)).replace('{MAX_LONG}', str(maxLong))
            vegaRequest = vegaRequest.replace('{MIN_LAT}', str(minLat)).replace('{MAX_LAT}', str(maxLat))

            vegaRequest = vegaRequest.replace('{WIDTH}', str(width)).replace('{HEIGHT}', str(height))

            vegaRequest = vegaRequest.replace('\n', '')
            data = self.con.render_vega(vegaRequest)
            return data
