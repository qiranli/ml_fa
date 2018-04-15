# Fundamental Data
import pandas as pd
import numpy as np

class balance_sheet(object):

    def __init__(self,all_blnc_sheet_path):
        self.all_blnc_sheet_path = all_blnc_sheet_path
        self.df_blnc_all = pd.read_csv(self.all_blnc_sheet_path)

        missing_year = self.df_blnc_all[self.df_blnc_all['fyear'].isnull()].index.values.tolist()
        self.df_blnc_all = self.df_blnc_all.drop(self.df_blnc_all.index[missing_year])
        self.df_blnc_all = self.df_blnc_all.reset_index(drop=True)

    def get_blnc_sheet(self,tickr):
        # Subset company data set
        df_raw = self.df_blnc_all[self.df_blnc_all["tic"] == tickr].copy()
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

        # balance_sheet
        df_blnc = df_raw[df_raw.columns.difference(f_to_drop)]
        df_blnc = df_blnc.fillna(0.)
        df_blnc = df_blnc.transpose()
        # assets
        assets_current = ['ch','chs','che','rect','arb','arc','artfs',
                            'iasti','iaui','iseq','istc','isut','tdst',
                            'islt','iati','rati','txr','xpp',
                            'aco','act']

        assets_rest = ['gdwl','ao','txndbl','rvti','intan','intano',
                        'invt','ivpt','ppegt','ppenb','ppenc','ppenme',
                        'ppent','ret','at']

        other_features = ['wcap','bkvlps','icapt','npat','lcat','pstk','re']

        # liabilities

        liabilities_current = ['ap','apb','apc','apofs','drc','txp','xacc',
                                'aedi','dlc','lco']

        liabilities_rest  = ['drlt','rlt','dclo','dcom','dcpstk','dcs','dcvsr',
                            'dcvt','dd','lo','cld2','cld3','cld4','cld5',
                            'txndba','clt','dd1','dd2','dd3','dd4','dd5',
                            'dxd2','dxd3','dxd4','dxd5','dlto','dltt','dptb',
                            'dptc','mrc1','mrc2','mrc3','mrc4','mrc5','mrcta',
                            'ceq','ceql','ceqt','lt','seq','lse']

        # combined list
        blnc_sheet_list = assets_current + assets_rest + liabilities_current + \
                        liabilities_rest + other_features

        df_blnc = df_blnc.reindex(blnc_sheet_list)

        return df_blnc
