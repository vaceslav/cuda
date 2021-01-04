#!/usr/bin/env python


from pymapd import connect
import cudf
from cuml.cluster import KMeans, DBSCAN
from geojson import Point, GeometryCollection
import time
import pygeohash as pgh

start = time.time()

con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

print( con.get_tables())


#query = "SELECT count(*) FROM nyc_trees_2015_683k"
query = "SELECT latitude, longitude FROM nyc_trees_2015_683k"
#query = "SELECT longitude, latitude FROM nyc_trees_2015_683k "

df = con.execute(query)
# print('query data')
# print(df)

result = list(df)

insertData = []

print("Iterate")
#for item, index in result:
for i in range(len(result)):
    item = result[i]
    l = list(item)
    l.insert(0, i)
    l.append(pgh.encode(item[0], item[1], precision=1))
    l.append(pgh.encode(item[0], item[1], precision=2))
    l.append(pgh.encode(item[0], item[1], precision=3))
    l.append(pgh.encode(item[0], item[1], precision=4))
    l.append(pgh.encode(item[0], item[1], precision=5))
    l.append(pgh.encode(item[0], item[1], precision=6))
    l.append(pgh.encode(item[0], item[1], precision=7))
    l.append(pgh.encode(item[0], item[1], precision=8))
    t = tuple(l)
    insertData.append(t)
    # print( pgh.encode(item[0], item[1]))
    # print(item)


con.load_table('portfolios', insertData)


#query = "show tables"
#df = con.execute(query)
#df.head()


end = time.time()
print(end - start)
print('END')
