# Get company's timeline information i.e its existence
# This is useful for comparison with 13-f data
import pandas as pd
import numpy as np


class company_13f(object):

    def __init__(self,path):
        self.path = path
        self.df_13f_all = pd.read_csv(path)
        self.df_13f_all['r_year'] = pd.to_datetime(self.df_13f_all['rdate']).dt.year
        self.df_13f_all = self.df_13f_all.fillna(0)
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

    def get_positive(self,year):
        cols = self.cols
        df_year =  self.df_13f_all[cols][self.df_13f_all['r_year']==year]
        df_year_tmp = df_year[df_year['decision']==1]
        df_year_tmp = df_year_tmp.reset_index(drop=True)
        return df_year_tmp

    def get_no_change(self,year):
        cols = self.cols
        df_year =  self.df_13f_all[cols][self.df_13f_all['r_year']==year]
        df_year_tmp = df_year[df_year['decision']==0]
        df_year_tmp = df_year_tmp.reset_index(drop=True)
        return df_year_tmp

    def get_negative(self,year):
        cols = self.cols
        df_year =  self.df_13f_all[cols][self.df_13f_all['r_year']==year]
        df_year_tmp = df_year[df_year['decision']== -1]
        df_year_tmp = df_year_tmp.reset_index(drop=True)
        return df_year_tmp

    def get_list_all_hist(self,status):
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
    c = company_13f(path)
    y_2016 = c.get_positive(2016)
    #brk = c.get_list_all_hist("positive")
    print y_2016
