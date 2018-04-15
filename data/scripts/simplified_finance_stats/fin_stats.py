# Fundamental Data
# For balance_sheet, income_sheet, cashflow
import pandas as pd
import numpy as np
import sys
from data.scripts.data_cleaning_tools.data_cleaning import data_cleaning


class fin_stats(object):
    """ Get fundamental data of a company. Includes


        1. Balance sheet
        2. Income sheet
        3. Cash Flow sheet

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
        # Balance Sheet
        # Assets
        assets_current = ['che','rect','invt','aco','act']
        assets_rest = ['ppent','ivaeq','ivao','intan','ao','at']

        # Liabilities
        liabilities_current = ['dlc','ap','txp','lco','lct']
        liabilities_rest = ['dltt','txditc','lo','lt','mib','pstk','ceq','seq']

        self.b_sheet = assets_current + assets_rest + liabilities_current + \
                    liabilities_rest

        # Income Statement
        revenue = ['revt']
        costs = ['cogs','xsga']
        operations = ['oibdp','oiadp','xint','nopi']
        income = ['spi','pi','txt','ib','niadj','epspx','epsfx']

        self.i_sheet = revenue + costs + operations + income

        # Cash Flow Statement
        cash_oper = ['ibc','xidoc','dpc','txdc','esub','sppiv','fopo','recch',
                    'invch','apalch','txach','aoloch','oancf']

        cash_investment = ['ivch','siv','ivstch','capx','sppe','aqc','ivaco',
                            'ivncf']

        cash_finance = ['sstk','txbcof','prstkc','dv','dltis','dltr','dlcch',
                        'fiao','fincf']

        self.c_sheet = cash_oper + cash_investment + cash_finance

    def get_sheet(self,tickr,sheet_name):
        """ Returns the specified sheet for a company with tickr symbol """

        if sheet_name == "balance_sheet":
            name = self.b_sheet
        elif sheet_name == "income_sheet":
            name = self.i_sheet
        elif sheet_name == "cashflow_sheet":
            name = self.c_sheet
        else:
            print("Name Error: Provide a valid sheet name")

        # Subset company data set
        df_raw = self.df_fin_all[self.df_fin_all["tic"] == tickr]
        df_raw = df_raw[name].copy()

        # Check if tickr is not present
        if df_raw.shape[0] == 0:
            print("%s not found in %s"%(tickr,sheet_name))
            return

        df_sheet = df_raw.transpose()
        df_sheet = df_sheet.reindex(name)
        df_sheet.columns = map(int,df_sheet.columns.tolist())

        # Remove all columns where the entire column has 0 entry
        df_sheet = df_sheet.loc[:, (df_sheet != 0).any(axis=0)]

        return df_sheet
