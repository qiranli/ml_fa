# Get training data from a list of companies
import pandas as pd
import numpy as np
import sys
sys.path.append("..")
import os

from data.scripts.simplified_finance_stats.fin_stats import fin_stats
from data.scripts.simplified_finance_stats.fin_ratios import get_ratios
from data.scripts.simplified_finance_stats.fin_stats_2 import fin_stats_2
from data.scripts.simplified_finance_stats.stock_stats import stock_stats
from report_13f.company_13f import company_13f


class train_data(object):

    def __init__(self,c_df):
        # c_list is the company list
        self.c_df = c_df
        self.base_path = '../data/combined_simplified/'
        # Set up paths for data source
        self.fin_data1 = self.base_path + 'combined_all_us.csv'
        self.fin_data2 = self.base_path + 'others_all_us.csv'
        self.mrkt_data = self.base_path + 'stock_stats_all_us.csv'

        # Instantiate the all dataframe
        self.finances = fin_stats(self.fin_data1)
        self.other_fin = fin_stats_2(self.fin_data2)
        self.mrkt = stock_stats(self.mrkt_data)

    def get_hist_data(self,n_years):

        # Returns a dictionary with company symbols as keys and historical
        # data as values
        # n_years: Most recent history of n_years

        hist_data = {}

        c_list = self.c_df['ticker'].values
        c_year = self.c_df['r_year'].values
        print("\n")
        print("Getting Data for:")

        for i,c in enumerate(c_list):
            print c
            c_b = self.finances.get_sheet(c,"balance_sheet")
            c_i = self.finances.get_sheet(c,"income_sheet")
            c_c = self.finances.get_sheet(c,"cashflow_sheet")
            c_o = self.other_fin.get_sheet(c) # other data not in bic
            c_m = self.mrkt.get_stock_data(c) # market data of stocks
            c_fin_stats = pd.concat([c_b,c_i,c_c,c_o,c_m])
            c_ratio = get_ratios(c_b,c_i,c_c)
            c_df = pd.concat([c_fin_stats,c_ratio])

            # Replace missing with -1
            c_df = c_df.fillna(-1.)

            # select the last n_years data
            year = c_year[i]
            strt_year = year - n_years
            time_range  = range(strt_year,year+1)

            try:
                c_df = c_df[time_range]
                hist_data[c] = c_df
            except Exception as e:
                print e
                print("Data range requested %g to %g" %(strt_year,year))
                print("Data only available from %g to %g" \
                %(c_df.columns.tolist()[0],c_df.columns.tolist()[-1]))
                print("\n")

        return hist_data

    def transform_c_to_1d(self,hist_data):

        # Fits a polynomial to the time series data of features. First n
        # coefficients along with the current values of features are used
        # to create a matrix. The matrix is unrolled to form a 1d array.
        # This is one row of the input matrix

        c_data_list = []
        c_name_list = hist_data.keys()

        for c,hist_data in hist_data.iteritems():

            hist_data_T = hist_data.transpose()
            y = hist_data_T.as_matrix()
            x = np.array(hist_data_T.index.tolist())

            # Polynomial fit
            p = np.polyfit(x,y,3)
            # Get the attributes from the latest year
            current_year = np.array([hist_data_T.iloc[-1].values])

            inp_matrix = np.vstack((p,current_year))
            m,n = inp_matrix.shape
            row = np.reshape(inp_matrix,(m*n))
            # convert to list for appending
            row = row.tolist()
            c_data_list.append(row)

        c_data_mat = np.asarray(c_data_list,dtype=np.float32)

        return c_name_list,c_data_mat


if __name__ == '__main__':

    all_list_path = "D:\\FA\\data\\cash_flow\\cash_flow_all_us_list.csv"
    brk_path = "D:\\FA\\report_13f\\brk\\13f_brk.csv"
    c = company_13f(brk_path,all_list_path)
    y_2016 = c.get_no_change(2016)

    t_data = train_data(y_2016)

    inp_data_10 = t_data.get_hist_data(10)

    names,data = t_data.transform_c_to_1d(inp_data_10)

    print names
    print inp_data_10['WFC']
