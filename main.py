#!/usr/bin/env python


from pymapd import connect
import cudf
from cuml.cluster import KMeans, DBSCAN
from geojson import Point, GeometryCollection
import time

start = time.time()

con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

print( con.get_tables())


#query = "SELECT count(*) FROM nyc_trees_2015_683k"
#query = "SELECT tree_dbh, user_type, longitude, latitude FROM nyc_trees_2015_683k ORDER BY created_at limit 10000"
query = "SELECT longitude, latitude FROM nyc_trees_2015_683k "

df = con.select_ipc_gpu(query)
# print('query data')
# print(df)


#x = df.drop(['tree_dbh', 'user_type'])
# print('Only Data')
# print(x)

kmeans = KMeans(n_clusters=100, max_iter=10, init='scalable-k-means++')
kmeans.fit(df)

# dbscan_float = DBSCAN(eps = 1, min_samples = 5)
# dbscan_float.fit(df)
# print(dbscan_float.labels_)

# print('labels')
# print(kmeans.labels_)

# print("cluster_centers:")
# print(kmeans.cluster_centers_)

# print(type(kmeans.cluster_centers_))
# print(dir(kmeans.cluster_centers_))

print("Iterate")
points = []
for item in kmeans.cluster_centers_.values.tolist():
    p = Point((item[0], item[1]))
    points.append(p)
#     # print(type(item))
#     # print(p)
#     # print(item[1])

collection = GeometryCollection(points)
print(collection)

#query = "show tables"
#df = con.execute(query)
#df.head()


end = time.time()
print(end - start)
print('END')
