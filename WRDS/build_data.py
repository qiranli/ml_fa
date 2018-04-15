"""
Builds the fundamental dataset for top 2000 market cap equitities from WRDS.
Requires WRDS account. Enter username and password when prompted.

Features: datadate,	gvkey,	year,  month,  mom1m,	mom3m,	mom6m,	mom9m,
        mrkcap,	entval,	saleq_ttm,	cogsq_ttm,	xsgaq_ttm,	oiadpq_ttm,
        niq_ttm,	cheq_mrq,	rectq_mrq,	invtq_mrq,	acoq_mrq,
        ppentq_mrq,	aoq_mrq,	dlcq_mrq,	apq_mrq,	txpq_mrq,
        lcoq_mrq,   ltq_mrq,	csho_1yr_avg

Takes about 40 minutes to build the complete dataset and outputs a csv
"""

import wrds
import pandas as pd
import datetime
import numpy as np
import pickle
from time import time
from wrds_data_processing import data_processing
import sys

start_time = time()

# Connect to WRDS data engine
db = wrds.Connection()

#############################################################################
#### SQL Query-----------------------------------------------------------####
#############################################################################

# Query to get list of companies with top 2000 market cap
q1 = ("select a.gvkey,a.latest,b.cshoq,b.prccq,b.mkvaltq,b.cshoq*b.prccq as market_cap,b.curcdq "
     "from "
        "(select gvkey,max(datadate) as latest "
         "from "
         "compm.fundq where datadate > '2017-01-01' "
         "group by gvkey) a inner join "
             "(select gvkey,datadate,mkvaltq,cshoq,prccq "
                "from compm.fundq where cshoq>0 and prccq>0 and curcdq='USD') b "
    "on a.gvkey = b.gvkey and a.latest=b.datadate "
     "order by market_cap desc "
    "limit 20")

mrk_df = db.raw_sql(q1)
top_20_eq_gvkey_list = mrk_df['gvkey'].values.tolist()
top_20_eq_gvkey = tuple(["'%s'"%str(i) for i in top_20_eq_gvkey_list])
top_20_eq_gvkey = ",".join(top_20_eq_gvkey)


# Query to get fundamental Data
q2 = ("select datadate,gvkey,tic,saleq,cogsq,xsgaq,oiadpq,niq,revtq,"
      "cheq, rectq, invtq, acoq, ppentq, aoq, dlcq, apq, txpq, lcoq, ltq, dlttq,cshoq,actq "
    "from compm.fundq "
     "where gvkey in (%s) ")%top_20_eq_gvkey
fundq_df = db.raw_sql(q2)
print("Shape of raw dataframe: %g,%g"%fundq_df.shape)
print('\n')

# Query to get price data
q3 = ("select gvkey,datadate,prccm "
     "from compm.secm "
     "where gvkey in (%s) ")%top_20_eq_gvkey
price_df_all = db.raw_sql(q3).sort_values('datadate')

# Query to get stock_split data
q4 = ("select gvkey,datadate,split "
     "from compm.sec_split "
     "where gvkey in (%s) ")%top_20_eq_gvkey
stock_split_df_all = db.raw_sql(q4).sort_values('datadate')

####--------------------------------------------------------------------------

# Build balance sheet features
blnc_sheet_list = ['cheq','rectq','invtq','acoq','ppentq','aoq',
                                'dlcq','apq','txpq','lcoq','ltq','dlttq','cshoq','actq']

# Build income sheet features
income_list = ['saleq','cogsq','xsgaq','oiadpq','niq','revtq']

gvkey_list = top_20_eq_gvkey_list
print len(gvkey_list)

df_all = fundq_df[['gvkey','datadate'] + income_list + blnc_sheet_list]

def reorder_cols():
    a = ['datadate','gvkey','year','month']
    mom = ['mom1m','mom3m','mom6m','mom9m']
    prc = ['mrkcap','entval']
    ttm_list_tmp = [x + '_ttm' for x in income_list]
    mrq_list_tmp = [x + '_mrq' for x in blnc_sheet_list]
    mrq_list_tmp.remove('cshoq_mrq')
    mrq_list_tmp.remove('dlttq_mrq')
    csho = ['csho_1yr_avg']

    new_order = a + mom + prc + ttm_list_tmp + mrq_list_tmp + csho
    return new_order

# Create empty df to be appended for each equity
df_all_eq = pd.DataFrame(columns=reorder_cols())

for key in gvkey_list:
    #print("GVKEY: %s"%key)
    df = df_all[df_all['gvkey'] == key].copy()
    df = df.sort_values('datadate')
    df = df.set_index('datadate',drop=False)
    df = df[~df.index.duplicated(keep='first')]
    #print("df shape:%g,%g"%df.shape)

    # get price_df for the current gvkey
    price_df = price_df_all[price_df_all['gvkey']==key].copy()
    #print("price df shape:%g,%g"%price_df.shape)

    # get stock_split_df for the current gvkey
    stock_split_df = stock_split_df_all[stock_split_df_all['gvkey']==key].copy()
    #print("stock split df shape:%g,%g"%stock_split_df.shape)
    #print("\n")

    # Start data processing
    dp = data_processing(lag=3)

    # Add the lag to the date index
    df = dp.add_lag(df)

    # Create new df with monthly frequency (empty)
    new_df_empty = dp.create_df_monthly(df)

    # Add ttm and mrq data
    ttm_mrq_df = dp.create_ttm_mrq(df,new_df_empty)

    # Adjust for stock split
    df_split_adjusted = dp.adjust_cshoq(ttm_mrq_df,stock_split_df)

    # Add price information
    df_w_price,price_df_for_mom = dp.add_price_features(df_split_adjusted,price_df)

    # Add momentum features
    df_w_mom = dp.get_mom(df_w_price,price_df_for_mom,[1,3,6,9])

    # Add csho_1_year average
    df_w_mom['csho_1yr_avg'] = df_w_mom['cshoq_mrq'].rolling(12,min_periods=1).mean()

    # Reorder column names
    new_order = reorder_cols()

    del df,price_df,stock_split_df

    df_out = df_w_mom[new_order]

    # Fill Nans with 0.0
    df_out = df_out.fillna(0.0)
    df_out = df_out.reset_index(drop=True)

    # Append the current df to the full_df
    df_all_eq = df_all_eq.append(df_out,ignore_index=True)

# Normalize the momentum features
dates = df_all_eq['datadate'].unique()

mom_f = ['mom1m','mom3m','mom6m','mom9m']

for date in dates:
    df_date = df_all_eq[mom_f][df_all_eq['datadate']==date]

    ix_dates = df_date.index
    df_norm = (df_date - df_date.min())/(df_date.max() - df_date.min())

    df_norm = df_norm.fillna(0.0)

    df_all_eq.loc[ix_dates,mom_f] = df_norm

    del df_date, df_norm

# Output the csv
df_all_eq.to_csv("top_20_eq_w_3mo_lag.csv")
exec_time = time() -start_time

print exec_time
