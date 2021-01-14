#!/usr/bin/env python

import pandas as pd

df =  pd.read_csv("./statistics.txt", sep="|")

size = df["total_data_file_size"].sum() / 1024.0 / 1024 / 1024.0

print(f"Total size: {size} GB")

