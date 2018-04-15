""" Builds the time series cards and trend data for each company.
    Time series card and trend card are dicts with tickr as keys and dataframes
     as the value"""

import pandas as pd
import numpy as np
import pickle
import sys
sys.path.append("..")
import matplotlib.pyplot as plt
import seaborn as sns

from data.scripts.simplified_finance_stats.fin_stats import fin_stats
from data.scripts.simplified_finance_stats.fin_ratios import get_ratios
from data.scripts.simplified_finance_stats.fin_stats_2 import fin_stats_2
from report_13f.brk.company_13f import company_13f
from data.scripts.build_training_data.train_data import train_data
from data.scripts.simplified_finance_stats.stock_stats import stock_stats
from data.scripts.simplified_finance_stats.capture_trends import get_trend_data


def get_last_n_data(df,n):
    """Returns the trend data for last n years"""
    last_n_years = n
    # Tolerance for years
    tol = 2
    n_t = last_n_years + tol
    x = len(df.columns.tolist())

    # For every last_n_years, the number of years actually required varies. If
    # a company has more than n_t years, then last_n_years will be retrieved.
    # If the company has less than n_t years, the number of years to be retrieved
    # is based on the following cubic polynomial with coeffs in decreasing order.
    # coeffs = [ -1.87811680e-04,   1.61943357e-02,  -1.45728104e-01,2.30892148e+00]
    #
    # This ensures that the amount of data required scales with number of n_years
    # requested. For example, if last 15 years data is asked and only 12 is present,
    # last 10 years would still be reasonable to use after removing first two
    # years as outliers. If 40 years is asked, last 30 years would be reasonable.

    coeffs = np.array([ -1.87811680e-04,   1.61943357e-02,  -1.45728104e-01,
                        2.30892148e+00])

    p = np.poly1d(coeffs)
    diff = np.round(p(last_n_years))

    if x > n_t:
        # No change is required. Last n years is retrieved
        cols_to_keep = df.columns.tolist()[-1*last_n_years::]
    elif (x <= n_t) and (x >= last_n_years - diff):
        cols_to_keep = df.columns.tolist()[-1*(x-tol)::]
    else:
        #print("Not enough last n years data")
        return

    df = df[cols_to_keep]
    return df

def get_time_s_card(tick,time_s_card):
    """Returns the dictionary of company's time series data"""
    b = finances.get_sheet(tick,"balance_sheet")
    i = finances.get_sheet(tick,"income_sheet")
    c = finances.get_sheet(tick,"cashflow_sheet")
    o = fin_others.get_sheet(tick)
    mk = mkt_data.get_stock_data(tick)

    try:
        # combine all dataset
        all_fin_data = pd.concat([b,i,c,o,mk])
        # Add to dictionary
        time_s_card[tick] = all_fin_data

    except ValueError:
        time_s_card[tick] = None

    return time_s_card


def get_trend_card(tick,n_years,trend_card):
    """Returns the dictionary of company's trend data"""
    b = finances.get_sheet(tick,"balance_sheet")
    i = finances.get_sheet(tick,"income_sheet")
    c = finances.get_sheet(tick,"cashflow_sheet")
    o = fin_others.get_sheet(tick)
    mk = mkt_data.get_stock_data(tick)

    try:
        # combine all dataset
        all_fin_data = pd.concat([b,i,c,o,mk])

        df_ratios = get_ratios(b,i,c,o,mk)

        # Specify the timeline with last n years to get data from
        df_ratios = get_last_n_data(df_ratios,n_years)
        df_fin = get_last_n_data(all_fin_data,n_years)

        # Build the trend data
        d_trend_ratios = get_trend_data(df_ratios)
        d_trend_fin = get_trend_data(df_fin)

        # Add to dictionary
        trend_card[tick] = [d_trend_fin, d_trend_ratios]

    except ValueError:
        trend_card[tick] = None

    return trend_card

def build_time_s_data(time_s_card):
    """Builds the dataset for time series data for all equities and saves as pkl"""
    for i,tick in enumerate(equity_list['tick'].values):
        time_s_card = get_time_s_card(tick,time_s_card)
        print(("Finished %s. %2.2f of Total Completed")%(tick, (i*100.)/equity_list.shape[0]))

    # Save the dict in pickle format
    with open('time_s_card' + '.pkl', 'wb') as handle:
        pickle.dump(time_s_card, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return

def build_trend_data(trend_card):
    """Builds trend data set for all equitiies and saves a pkl"""
    for i,tick in enumerate(equity_list['tick'].values):
        trend_card = get_trend_card(tick,n_years,trend_card)
        print(("Finished %s. %2.2f of Total Completed")%(tick, (i*100.)/equity_list.shape[0]))

    # Save the dict in pickle format
    with open('trend_card_' + str(n_years) + '.pkl', 'wb') as handle:
        pickle.dump(trend_card, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':

    # Set path for data
    base_path = '../data/'
    sheets_path = 'combined_simplified/combined_all_us.csv'
    other_path = 'combined_simplified/others_all_us.csv'
    mkt_path = 'combined_simplified/stock_stats_all_us.csv'

    # setup all data
    finances = fin_stats(base_path + sheets_path)
    fin_others = fin_stats_2(base_path + other_path)
    mkt_data = stock_stats(base_path + mkt_path)

    # Equity list
    equity_list_path = '../equity_list/all_us_list.csv'
    equity_list = pd.read_csv(equity_list_path)

    # Initialize the dictionaries
    time_s_card = {}
    trend_card = {}

    # Last n years data
    n_years = 15

    # Build the trend dataset
    build_trend_data(trend_card)

    # Build the time series fin data set
    # To be run only once. If time_s_card.pkl exists, no need to run this.
    # build_time_s_data(time_s_card)
