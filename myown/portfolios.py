
from pymapd import connect
import pandas as pd
import cudf
import time

import tornado
from myown.filter import create_filter_where
from myown.dbutils import count_rows
import psycopg2


class Portfolios:

    # default constructor
    def __init__(self, usePsql):
        if usePsql:
            self.con = psycopg2.connect(
                host="localhost",
                database="geo",
                user="postgres",
                password="example",
            )
        else:
            self.con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

    def list(self):
        query = "select distinct PortfolioName from portfolios"

        df = pd.read_sql(query, self.con)

        result = list(df['PortfolioName'])
        return result

    def convert(self, s: cudf.Series):
        pandas: pd.Series = s.to_pandas()
        return dict(zip(pandas.index, pandas))

    def analyze_cude_frame(self, portfolio_name, filter):

        start = time.time()

        query = f"""select 
                        Sum_Insured,
                        Losses,
                        earthquake,
                        hail,
                        heat_wave,
                        tornado,
                        Building_Type,
                        CountryCode
                    FROM portfolios where PortfolioName = '{portfolio_name}'"""

        # if len(filter) > 0:
        #     query = query + " WHERE "

        query = query + create_filter_where(filter)

        df = self.con.select_ipc(query)
        gdf: cudf.DataFrame = cudf.DataFrame(df)

        sum = df[['Sum_Insured', 'Losses']].sum()
        tsiSum = sum["Sum_Insured"]
        lossesSum = sum["Losses"]

        building_count = gdf.groupby('Building_Type')["Sum_Insured"].count()

        earthquake_count = gdf.groupby('earthquake')["Sum_Insured"].count()
        hail_count = gdf.groupby('hail')["Sum_Insured"].count()
        heat_wave_count = gdf.groupby('heat_wave')["Sum_Insured"].count()
        tornado_count = gdf.groupby('tornado')["Sum_Insured"].count()
        country_count = gdf.groupby('CountryCode')["Sum_Insured"].count()

        end = time.time()
        duration = end - start

        # print(building_count)

        result = {
            'count': len(df.index),
            'tsiSum': tsiSum,
            'lossesSum': lossesSum,
            'building': self.convert(building_count),
            'countries': self.convert(country_count),
            'earthquake': self.convert(earthquake_count),
            'hail':  self.convert(hail_count),
            'heat_wave': self.convert(heat_wave_count),
            'tornado': self.convert(tornado_count),
            'duration': duration
        }

        return result

    def group_count(self, portfolio_name, group_name, where):

        group_name = group_name.lower()

        query = f"""select  
                        {group_name},
                        count(*) AS pcount
                    FROM portfolios 
                    WHERE portfolioname = '{portfolio_name}' 
                    {where}
                    GROUP BY {group_name}
                    """

        df_group = pd.read_sql(query, self.con)
        # print(df_group.head())

        # df_group.set_index(group_name)
        d = dict(zip(df_group[group_name], df_group['pcount']))

        # print(d)

        return d

    def analyze_sql(self, portfolio_name, filter):

        where = create_filter_where(filter)

        start = time.time()

        # sum
        query = f"""select 
                        SUM(Sum_Insured) AS tsi,
                        SUM(Losses) AS losses
                    FROM portfolios where PortfolioName = '{portfolio_name}'
                     {where}
                    """

        df_sum = pd.read_sql(query, self.con)
        print(df_sum)
        # unique values

        where_count = f" PortfolioName = '{portfolio_name}'  {where}"
        count = count_rows(self.con, where_count)

        # query = f"""select  count(*) FROM portfolios where PortfolioName = '{portfolio_name}'  {where}"""
        # cursor = self.con.execute(query)
        # count = list(cursor)[0][0]

        building_count = self.group_count(portfolio_name, 'Building_Type', where)
        countries_count = self.group_count(portfolio_name, 'CountryCode', where)

        earthquake_count = self.group_count(portfolio_name, 'earthquake', where)
        hail_count = self.group_count(portfolio_name, 'hail', where)
        heat_wave_count = self.group_count(portfolio_name, 'heat_wave', where)
        tornado_count = self.group_count(portfolio_name, 'tornado', where)

        end = time.time()
        duration = end - start

        print(f"Time: {duration}")

        result = {
            'count': count,
            'tsiSum': df_sum['tsi'].iloc[0],
            'lossesSum': df_sum['losses'].iloc[0],
            'building': building_count,
            'countries': countries_count,
            'earthquake': earthquake_count,
            'hail': hail_count,
            'heat_wave':  heat_wave_count,
            'tornado': tornado_count,
            'duration': duration
        }

        return result

        # # df_c: pd.DataFrame = self.con.select_ipc(query, release_memory=False)
        # df: cudf.DataFrame = self.con.select_ipc_gpu(query)

        # #df = cudf.DataFrame(df_c)

        # sum =  df[['Sum_Insured', 'Losses']].sum()
        # tsiSum = sum["Sum_Insured"]
        # losesSum = sum["Losses"]

        # hasLosses =  df.groupby('Has_Losses')['Sum_Insured'].count()
        # buildingTypeCount =  df.groupby('Building_Type')['Sum_Insured'].count()
        # sampleRatingCount =  df.groupby('Sample_Rating')['Sum_Insured'].count()

        # # self.con.deallocate_ipc(df)

        # print(buildingTypeCount)

        # print(f"Summen {tsiSum} {losesSum}")

    def analyze(self, portfolioName, filter):
        # return self.analyze_cude_frame(portfolioName, filter)
        return self.analyze_sql(portfolioName, filter)
