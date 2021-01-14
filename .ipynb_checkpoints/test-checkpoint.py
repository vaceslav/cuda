import numpy as np
import pandas as pd



df1 = pd.DataFrame({'lat': [2, 3, 4],
                   'lon': [4, 9, 16],
                   'type': ['office', 'office', 'fabric'],
                   'count': [1, 5, 1]
                   })
        
print(df1)

labels = np.array([0, 1, 0])

df1['cluster_id'] = labels

print(df1)

group =  df1.groupby(['cluster_id']).sum()

print(group)
print(group['count'])

def myApply(x, y):
    return x


geohashDf = pd.DataFrame({  'lat': [2, 3, 4, 4, 4],
                            'lon': [4, 9, 16, 7, 4],
                            'geohash':  [101,        100,    100,        102,     100],
                            'building': ['office', 'office', 'fabric',  'office', 'office'],
                            'count':    [1,         5,        1,         2,        2],
                            'tsi':      [42,        50,       584,       71,       85]
                            })
print(geohashDf)

res = geohashDf.groupby(['geohash', 'building'])['building'].count()
print(res)


res2 = geohashDf.groupby(['geohash'])['lat', 'lon'].mean()
print(res2)

res3 = geohashDf.groupby(['geohash'])['count', 'tsi'].sum()
print(res3)

res3['lat'] = res2['lat']
res3['lon'] = res2['lon']
res3['building'] = res['building']
print(res3)


