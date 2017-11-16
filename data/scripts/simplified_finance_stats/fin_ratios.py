# Fundamental Data
# Financial ratios
import pandas as pd
import numpy as np

def get_ratios(b_sheet,i_sheet,c_sheet):

    # s: df_stats
    s = pd.concat([b_sheet,i_sheet,c_sheet])
    # r: df_ratios
    r = pd.DataFrame(columns = s.columns.tolist())

    # Gross Margin
    r.loc['gross_mrgn'] = (1.*s.loc['sale'] - s.loc['cogs'])/s.loc['sale']
    # Profit Margin
    r.loc['prft_mrgn'] = (1.*s.loc['niadj']/s.loc['sale'])
    # Pre-tax operating margin
    r.loc['oper_mrgn'] = (1.*s.loc['oiadp']/s.loc['sale'])
    # Capx to revenue
    r.loc['capx_to_rev'] = (1.*s.loc['capx']/s.loc['sale'])
    # net investment to revenue
    r.loc['ni_to_rev'] = (1.*(s.loc['capx']-s.loc['dpc'])/s.loc['sale'])
    # ROE
    r.loc['roe'] = (1.*s.loc['niadj']/s.loc['seq'])
    # ROA
    r.loc['roa']=(1.*s.loc['niadj']/s.loc['at'])
    # Return on oeprating assets
    r.loc['rooa']=(1.*s.loc['niadj']/(s.loc['at']-s.loc['intan']-\
                    s.loc['che'] - s.loc['ivaeq'] - s.loc['ivao']))
    # sale to assets (capital intensity)
    r.loc['sale_to_asts']=(1.*s.loc['sale']/s.loc['at'])
    # ROC
    r.loc['roc'] = (1.*s.loc['niadj']/(s.loc['dltt']+s.loc['seq']))
    # ROIC
    invested_cap = s.loc['act'] - s.loc['lct'] - s.loc['che'] - s.loc['ivaeq']
    r.loc['roic']=(1.*s.loc['niadj']/invested_cap)
    # tax rate
    r.loc['tax_rate']=(1.*s.loc['txt']/s.loc['pi'])

    return r
