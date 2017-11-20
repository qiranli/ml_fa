# Fundamental Data
# For balance_sheet, income_sheet, cashflow
import pandas as pd
import numpy as np

class fin_stats(object):

    def __init__(self,path):
        self.path = path
        self.df_fin_all = pd.read_csv(self.path)

        # Preprocess data
        # Remove rows with missing year information.
        missing_year = self.df_fin_all[self.df_fin_all['fyear'].isnull()].index.values.tolist()
        self.df_fin_all = self.df_fin_all.drop(self.df_fin_all.index[missing_year])
        self.df_fin_all = self.df_fin_all.reset_index(drop=True)

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
        revenue = ['sale']
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
            print("Tickr not found")
            return

        df_sheet = df_raw.transpose()
        df_sheet = df_sheet.reindex(name)
        df_sheet.columns = map(int,df_sheet.columns.tolist())

        return df_sheet
