# Get company's timeline information i.e its existence
# This is useful for comparison with 13-f data
import pandas as pd
import numpy as np
import gc
import sys
from Levenshtein import distance


class company_13f(object):

    """ Extract a company's 13f fillings in a dataframe format.

        Outputs:
                    1. Company info for positive, negative or no_change within
                        the 13f filings for the stated year
                    2. Get a df for historical data


    """

    def __init__(self,path,fin_all_us_data_path):
        """ Instantiates with the required paths"""
        self.path = path
        self.df_13f_all = pd.read_csv(path)

        # Data Preprocessing
        # Fill the names of  missing ticker symbols
        # fin_all_us_data is used as a reference for full database to fill
        # the missing ticker symbols. Cashflow is preferred as it is smallest
        # in size
        fin_path = fin_all_us_data_path
        all_data = pd.read_csv(fin_path)
        all_names = all_data[['tic','conm']].copy()
        all_names = all_names.drop_duplicates()
        del all_data; gc.collect() # memory

        self.df_13f_all = self.df_13f_all.drop_duplicates().reset_index()
        self.df_13f_all = self.fill_missing(self.df_13f_all,all_names)

        # Add year column
        self.df_13f_all['r_year'] = pd.to_datetime(self.df_13f_all['rdate']).dt.year
        self.df_13f_all = self.df_13f_all.fillna(0)

        # Update decision vraibales  for buy, 0 for no change, -1 for sell
        self.df_13f_all['decision'] = 0
        self.df_13f_all['decision'].loc[self.df_13f_all['change']>0] =  1
        self.df_13f_all['decision'].loc[self.df_13f_all['change']==0] =  0
        self.df_13f_all['decision'].loc[self.df_13f_all['change']<0] =  -1

        # since the 13f data starts from 1980, no-change or 0 for 1980 will be
        # regarded as 1
        a = (self.df_13f_all['r_year']==1980) & (self.df_13f_all['decision']==0)
        self.df_13f_all['decision'].loc[a] = 1

        # define common column names
        self.cols = ['ticker','decision','r_year']

    def fill_missing(self,df_13f,df_all):
        """ Fills the missing tickr from company name """
        missing_ix = df_13f[df_13f['ticker'].isnull()].index.tolist()

        print("Status of dataframe before filling missing names:")
        print("No. of missing fields %g" %len(missing_ix))
        print("\n")

        # Ticks not found in the current database are removed from 13f database
        to_remove = []
        c_name_count = []

        for i in missing_ix:
            c_name = df_13f["stkname"].iloc[i]
            c_name_count.append(c_name)
            #c_tic = df_all["tic"][df_all["conm"]==c_name]
            c_tic = self.get_tic(df_all[['tic','conm']].copy(),c_name)

            #if  len(c_tic.values) == 0 :
            if c_tic == "NOT FOUND":
                if c_name_count.count(c_name) == 1:
                    print("Ticker not in the current database. Removing %s" %c_name)
                to_remove.append(i)

            else:
                #df_13f["ticker"].iloc[i] = c_tic.values[0]
                df_13f["ticker"].iloc[i] = c_tic

        df_13f = df_13f.drop(df_13f.index[to_remove])

        if df_13f["ticker"].isnull().sum() == 0:
            print("\n")
            print("All values Filled")
        else:
            print("%g values not filled" %df_13f["ticker"].isnull().sum())

        return df_13f

    def get_tic(self,df,inp_str):
        """Returns the tic symbol matching the name of the company
            using levenshtein distance in sequence.
            Starting with the first element and matching sequentially"""

        df = df.drop_duplicates().reset_index()
        df['conm'] = df['conm'].str.split()
        df_s = df['conm']
        inp_str_s = inp_str.split()

        len_inp = len(inp_str_s)

        # First check if there is an exact match before moving on
        # to levenshtein distance
        if [x==inp_str_s for x in df_s.values].count(True) == 1:
            idx_true = [x==inp_str_s for x in df_s.values].index(True)
            tic = df['tic'].iloc[idx_true]
            return tic


        for i in range(len_inp):
            test_str = inp_str_s[i]
            # Get nth element of the name
            # eg: ['KRAFT','HEINZ','GROUP']
            df_i = df_s.apply(lambda x: self.get_n_element(x,i))
            # Remove empty lists
            df_i = df_i[[x != [] for x in df_i.values]]
            # similarity check using Levenshtein distance
            df_dist = df_i.apply(lambda x: distance(x,test_str))
            min_dist = df_dist.min()
            idxmin_dist = df_dist.idxmin()
            # Compare the min distance
            idx_dist = df_dist[df_dist == min_dist].index

            if len(idx_dist) == 1 and min_dist < 3:
                tic_idx = idx_dist.values[0]
                tic = df['tic'].iloc[tic_idx]
                return tic

            elif len(idx_dist) == 1 and min_dist >= 3:
                #print("Company Not found")
                tic = "NOT FOUND"
                return tic

            if (i+1 == len_inp):
                #print("Multiple names found without exact match")
                tic = "NOT FOUND"
                return tic


    def get_n_element(self,l,n):
        try:
            return l[n]
        except:
            return []


    def get_positive(self,year):
        """ Returns the df with securities where the position was added from
            last year"""
        cols = self.cols
        df_year =  self.df_13f_all[cols][self.df_13f_all['r_year']==year]
        df_year_tmp = df_year[df_year['decision']==1]
        df_year_tmp = df_year_tmp.reset_index(drop=True)
        return df_year_tmp

    def get_no_change(self,year):
        """ Returns the df with securities where there was no change in position
            from last year"""
        cols = self.cols
        df_year =  self.df_13f_all[cols][self.df_13f_all['r_year']==year]
        df_year_tmp = df_year[df_year['decision']==0]
        df_year_tmp = df_year_tmp.reset_index(drop=True)
        return df_year_tmp

    def get_negative(self,year):
        """ Returns the df with securities where the position was reduced from
            last year"""
        cols = self.cols
        df_year =  self.df_13f_all[cols][self.df_13f_all['r_year']==year]
        df_year_tmp = df_year[df_year['decision']== -1]
        df_year_tmp = df_year_tmp.reset_index(drop=True)
        return df_year_tmp

    def get_list_all_hist(self,status):
        """ Returns df with all the histrocial data of the company """
        cols = self.cols
        df_all_hist = pd.DataFrame(columns = cols)
        year_list = self.df_13f_all.r_year.unique()
        for y in year_list:
            if status == 'positive':
                df_y_tmp = self.get_positive(y)
                df_all_hist = df_all_hist.append(df_y_tmp)
            elif status == 'no_change':
                df_y_tmp = self.get_no_change(y)
                df_all_hist = df_all_hist.append(df_y_tmp)
            elif status == 'negative':
                df_y_tmp = self.get_negative(y)
                df_all_hist = df_all_hist.append(df_y_tmp)
            else:
                print("Provide with a valid status of the security")
                print("Pick from positive, no_change or negative")

        df_all_hist = df_all_hist.drop_duplicates()
        return df_all_hist

if __name__ == '__main__':

    path = "D:\\FA\\report_13f\\brk\\13f_brk.csv"
    all_list_path = "D:\\FA\\data\\cash_flow\\cash_flow_all_us_list.csv"
    c = company_13f(path,all_list_path)
    y_2016 = c.get_positive(2016)
    #brk = c.get_list_all_hist("positive")
    print y_2016
