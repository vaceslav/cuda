#!/usr/bin/env python


from pymapd import connect
import cudf
from cuml.cluster import KMeans

from geojson import Point, GeometryCollection
import numpy as np
import pandas as pd
import hdbscan


class Omnisci:

    # default constructor
    def __init__(self):
        self.con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

    def count(self, where):
        query = f"SELECT COUNT(*) FROM portfolios WHERE {where}"
        cursor = self.con.execute(query)
        count = list(cursor)[0][0]
        return count

    def countGroup(self, where, level):
        query = f"SELECT COUNT(*) FROM (SELECT COUNT(*) FROM portfolios WHERE {where} GROUP BY geohash_{level})"
        cursor = self.con.execute(query)
        count = list(cursor)[0][0]
        return count

    def calcLevel(self, where, thresholdMin = 15000, thresholdMax = 20000):

        # target ca. 10K points
        # thresholdMin = 15000
        # thresholdMax = 20000
        # thresholdMin = 100
        # thresholdMax = 500

        count =  self.count(where)
        if count <= thresholdMax:
            return (count, None)

        level5 = self.countGroup(where, 5)

        if thresholdMin <= level5 <= thresholdMax:
            return (count, 5)                                        # 5
        # level 5 is too much?
        elif level5 > thresholdMax:
            level3 = self.countGroup(where, 3)
            if level3 > thresholdMax:
                level2 = self.countGroup(where, 2)
                if level2 > thresholdMax:
                    print(f"Level 2 is bigger that {thresholdMax} use level1")
                    return (count, 1)                                 # 1
                elif level2 > thresholdMin:
                    print(f"use level 2 with {level2} points")
                    return (count, 2)                                 # 2
            elif level3 > thresholdMin:
                print(f"use level 3 with {level3} points")
                return (count, 3)                                     # 3
            level4 = self.countGroup(where, 4)
            if level4 < thresholdMax:
                print(f"use level 4 with {level4} points")
                return (count, 4)                                     # 4
            print(f"use level 3 with {level3} points")
            return (count, 3)                                         #

        # level 5 is too less
        level7 = self.countGroup(where, 7)
        if thresholdMin <= level7 <= thresholdMax:
            print(f"use level 7 with {level7} points")
            return (count, 7)
        # level 7 is too much?
        elif level7 > thresholdMax:
            level6 = self.countGroup(where, 6)
            if level6 > thresholdMax:
                print(f"use level 5 with {level5} points")
                return (count, 5)
            print(f"use level 6 with {level6} points")
            return (count, 6)
        level8 = self.countGroup(where, 8)
        if level8 > thresholdMax:
            print(f"use level 7 with {level7} points")
            return (count, 7)
        print(f"use level 8 with {level8} points")
        return (count, 8)



        #     level3 = self.countGroup(where, 3)
        #     if level3 > threshold:
        #         level2 = self.countGroup(where, 2)
        #         if level2 > threshold:
        #             # smalest level
        #             return 1
        #         else:
        #             return 2
        #     else:
        #         # check level 4
        #         level4 = self.countGroup(where, 4)
        #         if level4 > threshold:
        #             # return level 3
        #             return 3
        #         else:
        #             return 4
        # else:
        #     level7 = self.countGroup(where, 7)
        #     if level7 < threshold:
        #         level8 = self.countGroup(where, 8)
        #         if level8 < threshold:
        #             # no clustering
        #             return None
        #         else:
        #             return 7
        #     else:
        #         return 6

    def createWhere(self, extent):
        extent_splt =  extent.split(',')
        where = f"""
                        lon >= {extent_splt[0]} AND
                        lat >= {extent_splt[1]} AND
                        lon <= {extent_splt[2]} AND
                        lat <= {extent_splt[3]}
                  """
        return where

    def createCollection(self, items):
        points = []
        for item in items:
        #for i in range(len(kmeans.cluster_centers_)):
            #item = kmeans.cluster_centers_[i]
            # t1 = float(item[1])
            # t2 = np.asscalar(item[1])
            p = Point((item[1], item[0]))
            p.properties =  {'count': item[2]}
            points.append(p)

        collection = GeometryCollection(points)

        return collection

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


        df = self.con.select_ipc(query)
        # cursor = self.con.execute(query)
        # only_points = df.drop(['tree_dbh', 'user_type'])

        subset = df[['lat', 'lon']]
        (cluster, labels) = self.buildCluster(subset)

        df['cluster_id'] = labels
        print(df)
        group =  df.groupby(['cluster_id']).sum()
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
        epsilon = scale / 1000/  earth_radius_km  #calculate 5 meter epsilon threshold

        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='haversine',
                                    cluster_selection_epsilon=epsilon, cluster_selection_method = 'eom')

        # clusterer = hdbscan.HDBSCAN(metric='haversine')

        clusterer.fit_predict(subset)

        print(clusterer.labels_)
        df['cluster_id'] = clusterer.labels_
        print(df)
        groupSum =  df.groupby(['cluster_id']).sum()
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


    def createCluster(self, where , geohash_level, scale):
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
        count, geohash_level =  self.calcLevel(where, thresholdMin=5000, thresholdMax=7000)

        query = f"""select
                        avg(lat) AS lat,
                        avg(lon) AS lon,
                        count(*) AS pcount
                    from portfolios
                    where {where}
                    group by geohash_{geohash_level}
                    """
        df = self.con.select_ipc(query)
        

        items = df.values.tolist()
        print(items)
        return items

    def request(self, zoom, extent, scale):

        # query = "SELECT tree_dbh, user_type, longitude, latitude FROM nyc_trees_2015_683k ORDER BY created_at limit 100000"
        #query = "SELECT longitude, latitude FROM nyc_trees_2015_683k"

        #is_point_in_merc_view(lon, lat, {extent})

        where = self.createWhere(extent)
        (count, geohash_level) =  self.calcLevel(where)
        print(f"count {count}")

        maxSingePoints = 250

        points = []
        if count > maxSingePoints:
            points = self.createCluster(where, geohash_level, scale)
        else:
            points = self.createNoCluster(where)



        # collection = self.createCollection(cluster.values.tolist())
        collection = self.createCollection(points)
        return collection