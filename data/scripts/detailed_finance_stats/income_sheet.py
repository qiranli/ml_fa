# Fundamental Data
import pandas as pd
import numpy as np

class income_sheet(object):

    def __init__(self,all_income_sheet_path):
        self.all_income_sheet_path = all_income_sheet_path
        self.df_income_all = pd.read_csv(self.all_income_sheet_path)

        missing_year = self.df_income_all[self.df_income_all['fyear'].isnull()].index.values.tolist()
        self.df_income_all = self.df_income_all.drop(self.df_income_all.index[missing_year])

    def get_income_sheet(self,tickr):
        # Subset company data set
        df_raw = self.df_income_all[self.df_income_all["tic"] == tickr].copy()
        df_raw = df_raw.reset_index(drop=True)
        df_raw = df_raw.set_index('fyear')

        # Check if tickr is not present
        if df_raw.shape[0] == 0:
            print("Tickr not found")
            return

        # company info df
        info_features = ['gvkey','indfmt','consol','popsrc',
                            'datafmt','tic','conm','curcd',
                            'cik','costat']

        df_info = df_raw[info_features].iloc[0]

        f_to_drop = info_features + ['datadate']

        # income_sheet
        df_income = df_raw[df_raw.columns.difference(f_to_drop)]
        df_income = df_income.fillna(0.)
        df_income = df_income.transpose()

        # Income features
        revenue = ['revt','nfsr','sale']

        costs = ['xsga','xrent','xrd','xlr','stkco','batr','bct','bctr','cogs',
                'rcp','patr','tie','tii','xint','xnitb','xopr','xoprar','xpr',
                'xuwti','xt']

        oper = ['gp','oibdp','oiadp','opeps','opili','opiti','pi','initb',
                    'ib','ibki','idit','isgt','ivi','li','ipti','ptbl','txdi',
                    'txds','txfed','txfo','txt']

        net = ['ni','niint','niit','nit','nits','spce','epsfi','epspx','cga',
                    'cgti','citotal','nim']

        incm_sheet_list = revenue + costs + oper + net

        df_income = df_income.reindex(incm_sheet_list)

        return df_income
