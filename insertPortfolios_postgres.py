#!/usr/bin/env python

import psycopg2
import glob
import pandas as pd
from sqlalchemy import create_engine

connection = psycopg2.connect(
    host="localhost",
    database="geo",
    user="postgres",
    password="example",
)

cursor = connection.cursor()


engine = create_engine('postgresql://postgres:example@localhost:5432/geo')

for filename in glob.glob('data/portfolios/*5m*.feather'):
    print(f'read file {filename}')
    df: pd.DataFrame = pd.read_feather(filename)

    portfolioNmae = f"{filename.split('/')[-1].split('.')[0]}_0"
    df['PortfolioName'] = portfolioNmae

    df.columns = df.columns.str.lower()
    df.columns

    print(df.head())

    df.to_sql("portfolios", con=engine, index=False, if_exists="append")


cursor.close()
connection.close()
