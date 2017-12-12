import pandas as pd
import numpy as np
import gc
from sklearn.metrics import r2_score

def get_trend_data(df_t):
    """ Returns the trend data for a given time series data.
        1. Avg value
        2. Std. Dev
        3. Avg Growth Rate
        4. Polynomial coefficients """

    # df_t : df_time_series

    if df_t is None:
        return "Not enough last n years data"

    df = pd.DataFrame()

    # Recent value
    df['most_recent_value'] = df_t[[df_t.columns.tolist()[-1]]]
    # Mean and std_dev
    df['mean'] =  df_t.mean(axis=1)
    df['std']  = df_t.std(axis=1)

    # Avg growth rate
    cols = df_t.columns.tolist()
    # t+1 step
    df_t_copy = df_t.copy()
    df_t_1 = df_t.copy()
    df_t_1 = df_t_1.drop([cols[0]],axis=1).as_matrix()
    df_t_copy = df_t_copy.drop([cols[-1]],axis=1).as_matrix()

    df_growth = df_t_1 - df_t_copy

    df_growth_rate = np.divide(df_growth,df_t_copy)

    df['avg_growth_rate'] = np.mean(df_growth_rate, axis=1)

    # Linear regression line
    years = df_t.columns.tolist()
    #x = np.asarray([i-years[0] for i in years])
    x = np.asarray(years)
    df_t_T = df_t.transpose()
    y = df_t_T.as_matrix()

    # fit polynomial
    slope = {}
    constant = {}
    r_squared = {}
    for i,feature in enumerate(df_t_T.columns.tolist()):
        y = df_t_T[feature].values
        coeff = np.polyfit(x,y,1)
        p = np.poly1d(coeff)
        y_pred = p(x)
        slope[feature] = coeff[0]
        constant[feature] = coeff[1]
        try:
            r_squared[feature] = r2_score(y,y_pred)
        except ValueError:
            r_squared[feature] = float('nan')

    df['slope'] = pd.Series(slope)
    df['constant'] = pd.Series(constant)
    df['r2'] = pd.Series(r_squared)


    del df_t_1
    del df_t_copy
    del df_t
    gc.collect()

    return df
