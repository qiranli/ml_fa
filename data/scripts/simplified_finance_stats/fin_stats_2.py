# Fundamental Data
# Other financial data not included in fin_stats
import pandas as pd
import numpy as np
from data.scripts.data_cleaning_tools.data_cleaning import data_cleaning


class fin_stats_2(object):
    """ Get fundamental data which is not included in balance,income or cashflow sheets.


        Methods:
                get_sheet()


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
        self.df_fin_all = self.df_fin_all.fillna(0.)

        # Select financial statements variables
        self.others = ['re','wcapch','wcapc','unwcc','nim','citotal','cga',
                    'mrc1','mrc2','mrc3','mrc4','mrc5']

    def get_sheet(self,tickr):
        """ Returns data for other financials not included in balance,
        income or cash flow sheets """
        name = self.others

        # Subset company data set
        df_raw = self.df_fin_all[self.df_fin_all["tic"] == tickr]
        df_raw = df_raw[name].copy()

        # Check if tickr is not present
        if df_raw.shape[0] == 0:
            print("%s not found in other data"%tickr)
            return

        df_sheet = df_raw.transpose()
        df_sheet = df_sheet.reindex(name)
        df_sheet.columns = map(int,df_sheet.columns.tolist())

        # Remove all columns where the entire column has 0 entry
        df_sheet = df_sheet.loc[:, (df_sheet != 0).any(axis=0)]

        return df_sheet
