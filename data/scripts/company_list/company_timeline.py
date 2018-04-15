"""Get company's timeline information i.e its existence
    This is useful for comparison with 13-f data"""

import pandas as pd
import numpy as np
import gc
#from tqdm import tqdm


class company_timeline(object):
    """Extracts the timeline of existence of the company"""
    def __init__(self,company_list_path):
        self.company_list_path = company_list_path
        self.df_all_data = pd.read_csv(self.company_list_path)

        # Preprocess data
        self.df_comp_time = self.df_all_data[['tic','fyear']].copy()
        del self.df_all_data # memory
        gc.collect()

    def get_timeline(self,tickr):
        """ Return the start year, last_active_year and number of years the stock
            has been listed on the exchange."""

        df_tmp = self.df_comp_time[self.df_comp_time['tic']==tickr].copy()

        if df_tmp.shape[0] == 0:
            print("Compnay: %s not found" %tickr)
            return 'Not found'

        df_tmp = df_tmp.reset_index(drop=True)
        n_years = df_tmp.shape[0]
        start_year = df_tmp['fyear'].iloc[0]
        last_active_year = df_tmp['fyear'] .iloc[n_years-1]

        del df_tmp # memory
        gc.collect()

        return [start_year, last_active_year, n_years]

if __name__ == '__main__':

    # Using cashflow data as it is the smallest. Can use any complete data.
    cash_path = 'D:\\FA\\data\\cash_flow\\cash_flow_all_us_list.csv'
    list_path = 'D:\\FA\\equity_list\\all_us_list.csv'
    c_list = pd.read_csv(list_path,header=None)[0].values
    ct = company_timeline(cash_path)
    cols = ['tic','start_year','Last_active_year','Num_of_years']
    df2 = pd.DataFrame(columns=cols)

    for c in c_list:
        print("Company: %s" %c)
        time_line = ct.get_timeline(c)
        if time_line != 'Not found':
            time_line = [c] + time_line
            df_tmp2 = pd.DataFrame([time_line],columns=cols)
            df2 = df2.append(df_tmp2,ignore_index=True)

    df2.to_csv("company_timeline.csv",index=False)
