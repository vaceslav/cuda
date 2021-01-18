from pyproj import Proj, transform
from myown.filter import create_filter_where

import pandas as pd

from geojson import Point, GeometryCollection


def count_rows(con, where):
    query = f"SELECT COUNT(*) as pCount FROM portfolios WHERE {where}"

    df = pd.read_sql(query, con)

    print(df)

    count = df.iloc[0, 0]

    # cursor = con.execute(query)
    # count = list(cursor)[0][0]

    return int(count)


def countGroup(con, where, level):
    query = f"SELECT COUNT(*) as pCount FROM (SELECT COUNT(*) FROM portfolios WHERE {where} GROUP BY geohash_{level}) as sub"
    df = pd.read_sql(query, con)
    # cursor = con.execute(query)
    # count = list(cursor)[0][0]
    count = df.iloc[0, 0]
    return count


def createCollection(items):
    points = []
    for item in items:
        # for i in range(len(kmeans.cluster_centers_)):
        #item = kmeans.cluster_centers_[i]
        # t1 = float(item[1])
        # t2 = np.asscalar(item[1])
        p = Point((item[1], item[0]))
        p.properties = {'count': item[2], 'tsi': item[3]}
        points.append(p)

    collection = GeometryCollection(points)

    return collection


def calcLevel(con, where, thresholdMin=15000, thresholdMax=20000):

    # target ca. 10K points
    # thresholdMin = 15000
    # thresholdMax = 20000
    # thresholdMin = 100
    # thresholdMax = 500

    # if count <= thresholdMax:
    #     return (count, None)

    level5 = countGroup(con, where, 5)

    if thresholdMin <= level5 <= thresholdMax:
        return 5                                        # 5
    # level 5 is too much?
    elif level5 > thresholdMax:
        level3 = countGroup(con, where, 3)
        if level3 > thresholdMax:
            level2 = countGroup(con, where, 2)
            if level2 > thresholdMax:
                print(f"Level 2 is bigger that {thresholdMax} use level1")
                return 1                                 # 1
            elif level2 > thresholdMin:
                print(f"use level 2 with {level2} points")
                return 2                                 # 2
        elif level3 > thresholdMin:
            print(f"use level 3 with {level3} points")
            return 3                                     # 3
        level4 = countGroup(con, where, 4)
        if level4 < thresholdMax:
            print(f"use level 4 with {level4} points")
            return 4                                     # 4
        print(f"use level 3 with {level3} points")
        return 3                                         #

    # level 5 is too less
    level7 = countGroup(con, where, 7)
    if thresholdMin <= level7 <= thresholdMax:
        print(f"use level 7 with {level7} points")
        return 7
    # level 7 is too much?
    elif level7 > thresholdMax:
        level6 = countGroup(con, where, 6)
        if level6 > thresholdMax:
            print(f"use level 5 with {level5} points")
            return 5
        print(f"use level 6 with {level6} points")
        return 6
    level8 = countGroup(con, where, 8)
    if level8 > thresholdMax:
        print(f"use level 7 with {level7} points")
        return 7
    print(f"use level 8 with {level8} points")
    return 8

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


def createWhere(portfolio, extent, filter, trans=False):

    extent_splt = extent.split(',')

    extent_splt = list(map(float, extent_splt))

    minLong, minLat = extent_splt[0], extent_splt[1]
    maxLong, maxLat = extent_splt[2], extent_splt[3]

    if trans:
        inProj = Proj('epsg:3857')
        outProj = Proj('epsg:4326')
        minLong, minLat = transform(inProj, outProj, minLong, minLat)
        maxLong, maxLat = transform(inProj, outProj, maxLong, maxLat)

    where = f"""
                    longitude >= {minLong} AND
                    latitude >= {minLat} AND
                    longitude <= {maxLong} AND
                    latitude <= {maxLat} AND
                    portfolioname = '{portfolio}'
                """

    where = where + create_filter_where(filter)
    return where
