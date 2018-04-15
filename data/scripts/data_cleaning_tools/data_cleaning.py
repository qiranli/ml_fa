""" Data cleaning and pre-processing tools"""

import pandas as pd
import numpy as np
import sys


class data_cleaning(object):
    """ Methods to clean and pre-process data


    """

    def remove_missing_tic_data(self,df):
        """ Removes all data if tic is missing """

        missing_tic_ix = df[df['tic'].isnull()].index.tolist()
        df = df.drop(df.index[missing_tic_ix])
        df = df.reset_index(drop=True)

        return df

    def remove_missing_year_data(self,df):
        """Removes all data where fyear is missing"""

        missing_year = df[df['fyear'].isnull()].index.values.tolist()
        df = df.drop(df.index[missing_year])
        df = df.reset_index(drop=True)

        return df

    def remove_pre_IPO_data(self,IPO_year_path,df):
        """Removes data prior to IPO year. Make sure df contains 'fyear' and
            "tic" as column names

            Use the function before making fyear as the index."""

        df_IPO_year = pd.read_csv(IPO_year_path)
        comp_list = list(set(df['tic'].values))
        # remove NaN values from the list
        comp_list = [x for x in comp_list if pd.notnull(x)]

        # Initialize an empty remove list
        ix_to_rmv = []
        total_missing = 0
        missing_names = []

        for i,name in enumerate(comp_list):
            # Filter the tic data
            df_tmp = df[df['tic'] == name]

            try:
                year = int(df_IPO_year[df_IPO_year['tic']==name]['IPO_year'])
                # Will raise an exception if year is empty i.e it doesn't exist
                # in IPO data

            except:
                #print("Tick %s not in IPO_year list. Removing the subsequent data"%name)
                missing_names.append(name)
                ix_tick = df_tmp.index.tolist()
                ix_to_rmv.extend(ix_tick)
                total_missing += 1

            finally:
                ix_to_rmv.extend(df_tmp[df_tmp['fyear'] < year].index.tolist())

        print("Total Missing tickers: %i"%total_missing)
        #print("Missing Names:")
        #print(missing_names)

        df = df.drop(df.index[ix_to_rmv])
        df = df.reset_index(drop=True)

        return df

if __name__ == '__main__':
    # Test
    path = "/Users/liqiran/Desktop/ml_fa/data/stock_stats/data/cash_flow/cash_flow_all_us_list.csv"
    ipo_path = "/Users/liqiran/Desktop/ml_fa/data/stock_stats/IPO_year.csv"

    df = pd.read_csv(path)
    dc = data_cleaning(df)
    cleaned_df = dc.remove_missing_year_data()
    #cleaned_df = dc.remove_pre_IPO_data(ipo_path)
    cleaned_df.to_csv("test_del_me.csv",index=False)
