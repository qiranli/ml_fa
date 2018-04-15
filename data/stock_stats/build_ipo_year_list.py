""" Builds the list of tickr symbols along with their IPO year. The data before
    that year is incomplete and not very uselful"""

import pandas as pd
import numpy as np
import sys

stock_stats_path = "stock_stats_all_us.csv"
df_mrkt_data = pd.read_csv(stock_stats_path)

missing_ix = df_mrkt_data[df_mrkt_data['prcc_c'].isnull()].index.tolist()

df_mrkt_data = df_mrkt_data.drop(df_mrkt_data.index[missing_ix])
df_mrkt_data = df_mrkt_data.reset_index(drop=True)

comp_list = list(set(df_mrkt_data['tic'].values))
# remove NaN values from the list
comp_list = [x for x in comp_list if pd.notnull(x)]

IPO_year = pd.DataFrame(columns=['tic','IPO_year'])

for i,name in enumerate(comp_list):
    df = df_mrkt_data[df_mrkt_data['tic']==name].reset_index(drop=True)
    year = int(df['fyear'].iloc[0])
    IPO_year.loc[i] = [name,year]

IPO_year.to_csv("IPO_year.csv",index = False)
