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

