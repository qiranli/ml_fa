# Market Data

import pandas as pd
import numpy as np
from data.scripts.data_cleaning_tools.data_cleaning import data_cleaning

class stock_stats(object):
    """ Market Data. Market data is not present in the WRDS fundamental database.

        Get market information of stocks.

    """
    def __init__(self,path):
        self.path = path
        self.df_fin_all = pd.read_csv(self.path)

        # Preprocess data
        # Clean the data
        dc = data_cleaning()
        # remove data with missing ticker symbols
        self.df_fin_all = dc.remove_missing_tic_data(self.df_fin_all)
        # remove pre IPO data
        IPO_path = "/Users/liqiran/Desktop/ml_fa/data/stock_stats/IPO_year.csv"
        self.df_fin_all = dc.remove_pre_IPO_data(IPO_path,self.df_fin_all)

        # Remove rows with missing year information.
        self.df_fin_all = dc.remove_missing_year_data(self.df_fin_all)

        self.df_fin_all = self.df_fin_all.set_index('fyear')

        # Select market data for the stock
        self.market_data = ['csho','mkvalt','prcc_c','prcc_f']

    def get_stock_data(self,tickr):
        """ Returns df with market data of the stocks """
        name = self.market_data

        # Subset company data set
        df_raw = self.df_fin_all[self.df_fin_all["tic"] == tickr]
        df_raw = df_raw[name].copy()

        # Check if tickr is not present
        if df_raw.shape[0] == 0:
            print("%s not found in mkt data"%tickr)
            return

        # Fill the market cap columns
        # If prcc_f is missing, prcc_c is used for approximation
        missing_prcc_f = df_raw[df_raw["prcc_f"].isnull()].index.values.tolist()
        df_raw['prcc_f'].loc[missing_prcc_f] = \
        df_raw["prcc_c"].loc[missing_prcc_f]

        df_raw["mkvalt"] = df_raw["csho"]*df_raw["prcc_f"]

        # Fill prcc_c na values from prcc_f
        missing_prcc_c = df_raw[df_raw["prcc_c"].isnull()].index.values.tolist()
        df_raw['prcc_c'].loc[missing_prcc_c] = \
        df_raw["prcc_f"].loc[missing_prcc_c]

        df_sheet = df_raw.transpose()
        df_sheet = df_sheet.reindex(name)
        df_sheet.columns = map(int,df_sheet.columns.tolist())

        # Remove all columns where the entire column has 0 entry
        df_sheet = df_sheet.loc[:, (df_sheet != 0).any(axis=0)]

        return df_sheet
