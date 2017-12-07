# Market Data

import pandas as pd
import numpy as np

class stock_stats(object):
    """ Market Data. Market data is not present in the WRDS fundamental database.

        Get market information of stocks.

    """
    def __init__(self,path):
        self.path = path
        self.df_fin_all = pd.read_csv(self.path)

        # Preprocess data
        # Remove rows with missing year information.
        missing_year = self.df_fin_all[self.df_fin_all['fyear'].isnull()].index.values.tolist()
        self.df_fin_all = self.df_fin_all.drop(self.df_fin_all.index[missing_year])
        self.df_fin_all = self.df_fin_all.reset_index(drop=True)

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
            print("Tickr not found")
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

        return df_sheet
