import numpy
from pandas.core.dtypes.missing import isnull
from pymapd import connect
from myown.filter import create_filter_where
import time
import cudf
import pandas as pd
import json


class Hierarchical:

    def __init__(self):
        self.con = connect(user="admin", password="HyperInteractive", host="localhost", dbname="omnisci")

    def create_hierarchical(self, item, df: pd.DataFrame):

        layerId = item.name

        childrenAll = df[df['ParentLayerId'] == layerId]

        child_tsi = 0
        child_losses = 0
        child_count = 0

        children = []

        for index, row in childrenAll.iterrows():
            childData = self.create_hierarchical(row, df)
            children.append(childData)
            child_tsi = child_tsi + childData['TSI']
            child_losses = child_losses + childData['Losses']
            child_count = child_count + childData['Count']

        result = {
            'name': f'Layer {layerId}',
            'TSI_Local': item['Sum_Insured'],
            'Losses_Local': item['Losses'],
            'Count_Local': item['count'],
            'children': children,
            'TSI': item['Sum_Insured'] + child_tsi,
            'Losses': item['Losses'] + child_losses,
            'Count': item['count'] + child_count,
        }

        return result

    def request(self, portfolio_name, filter):

        start = time.time()

        query = f"""select
                        p.LayerId,
                        model.LayerName,
                        model.ParentLayerId,
                        p.Sum_Insured,
                        p.Losses
                    FROM portfolios p
                    INNER JOIN model2layers model on model.Id = p.LayerId
                    WHERE  PortfolioName = '{portfolio_name}'
                    """

        query = query + create_filter_where(filter)

        df_cpu = self.con.select_ipc(query)

        gdf: cudf.DataFrame = cudf.DataFrame(df_cpu)

        group = gdf.groupby('LayerId')

        sum: pd.DataFrame = group[['Sum_Insured', 'Losses']].sum().to_pandas()
        parent = group[['ParentLayerId']].min().to_pandas()
        count = group[['LayerName']].count().to_pandas()

        all = sum.join(count)
        all = all.rename(columns={'LayerName': 'count'})
        all = all.join(parent)
        print(all.head())

        root = all[all['ParentLayerId'].isnull()].iloc[0]
        print(root)

        result = self.create_hierarchical(root, all)

        end = time.time()
        duration = end - start

        result['duration'] = duration

        return json.dumps(result)
