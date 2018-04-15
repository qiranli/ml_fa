# Fundamental Data
import pandas as pd
import numpy as np

class cashflow(object):

    def __init__(self,all_cashflow_path):
        self.all_cashflow_path = all_cashflow_path
        self.df_cashflow_all = pd.read_csv(self.all_cashflow_path)

        # Remove rows with missing year information.
        missing_year = self.df_cashflow_all[self.df_cashflow_all['fyear'].isnull()].index.values.tolist()
        self.df_cashflow_all = self.df_cashflow_all.drop(self.df_cashflow_all.index[missing_year])

    def get_cashflow(self,tickr):
        # Subset company data set
        df_raw = self.df_cashflow_all[self.df_cashflow_all["tic"] == tickr].copy()
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
        df_cashflow = df_raw[df_raw.columns.difference(f_to_drop)]
        df_cashflow = df_cashflow.fillna(0.)
        df_cashflow = df_cashflow.transpose()

        # cashflow features

        income = ['ibc']

        adjustments = ['depc','dpc','tdc','txbco','txbcof','txdc']

        changes_in_al = ['recch','txach','txpd','aoloch','apalch','aqc','capx',
                        'esubc','fopo','fopox','fopt','intpn','invch','oancf']

        invest_act = ['capxv','itcc','ivaco','ivch','ivstch','prstkcc',
                    'prstkpc','sppiv','siv','sppe','uaoloch','ivncf']

        finance_act = ['dlcch','dltis','dltr','exre','fiao','scstkc','spstkc',
                        'sstk','fincf']

        net_cash_change = ['chech']

        others = ['cdvc','dv','fsrct','fuset','tsafc','utfdoc','utfosc',
                    'uwkcapc','unwcc','wcapc','wcapch']

        cashflow_list = income + adjustments + changes_in_al + invest_act + \
                        finance_act + net_cash_change + others

        df_cashflow = df_cashflow.reindex(cashflow_list)

        return df_cashflow
