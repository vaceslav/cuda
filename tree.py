#!/usr/bin/env python

import numpy as np
import pandas as pd


def calculateTsi(df, nodeId):
    tsi = df.at[nodeId, "Tsi"]
    
    childs = df[df["Parent"] == nodeId]
    childsTsi = 0

    for index, child in childs.iterrows():
        childsTsi = childsTsi + calculateTsi(df, index)

    totalTsi = tsi + childsTsi
    df.at[nodeId, "TotalTsi"] = totalTsi

    return totalTsi


size = 10

data = {
        "Id": list(range(1, size+1)),
        "NodeId": np.random.choice(['layer1','layer2','layer3', 'layer4', 'layer5', 'layer6'], size=size),
        "Parent": np.random.choice(['layer2','layer3', 'layer4', 'layer5', 'layer6'], size=size),
        "Tsi": np.random.randint(25, 125, size=size)
        }

df = pd.DataFrame(data)
df = df.set_index("Id")


df["TotalTsi"] = np.NaN

roots = df[df["NodeId"] == 'layer1']

for index, item in roots.iterrows():
    calculateTsi(df, index)

print(df)
