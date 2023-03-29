#!/usr/bin/env python
""" Data aggregation for binary growth phenotypes

This script will aggregate the data of interest from 'binary_growth_phenotypes/data/raw/' 
and do significance testing to produce the files located in 'binary_growth_phenotypes/data/agg/'

Note: This is not a generalized script and can only be used from this folder since the paths are hardcoded.

"""

import pandas as pd
import numpy as np
from PARAMS import STRAINS_LAB
from scipy.stats import ttest_ind, ttest_rel
from itertools import combinations

__author__ = "Famke Baeuerle"

def agg_and_save_CGXII():
    datasets = [
    '../data/raw/2023-01-11_CGXII_14.csv', # 14
    '../data/raw/2023-01-12_CGXII-16.csv', # 16
    ]
    frames = [pd.read_csv(df).set_index('short').drop(['not c', '+Trace not c', '+Sacc not c', '+Tween+Sacc c']).reset_index() for df in datasets] 
    frames = frames + [pd.read_csv('../data/raw/2023-01-24_CGXII_15.csv').set_index('short').drop(['not c', '+Trace not c', '+Sacc not c', '+CasA not c', '+Tween+Sacc c']).reset_index()] #15
    #strain 17, remove CasA results from 1701 and use from 2301
    frames = frames + [pd.read_csv('../data/agg/CGXII_OD_17_manual.csv')]
    frames_new = [frame.replace({
        '+Tween c':'CGXII+Tween',
        '+Tween+Trace c':'CGXII+Tween+Trace',
        '+Tween+CasA c': 'CGXII+Tween+CasA'
    }) for frame in frames]  
    datasets2 = [
        '../data/raw/2023-02-09_CGXII_all.csv',
        '../data/raw/2023-02-10_CGXII_all.csv',
        '../data/raw/2023-03-28_CGXII_15-16-17.csv'
    ]
    frames2 = [pd.read_csv(df) for df in datasets2]
    data = pd.concat(frames_new, axis=1)
    data = data.loc[:,~data.columns.duplicated()].copy()
    data = data.append(frames2)
    # use stack() to bring short and measurment into rows
    new = pd.DataFrame(data.set_index('short').sort_index().T.stack()).reset_index().rename({0:'OD'}, axis=1)
    # split strain description
    new[['strain', 'time', 'sample']] = new.level_0.str.split('-', expand=True)
    new['strain'].replace(STRAINS_LAB, inplace=True)
    new.rename({'level_0':'lab_mapping'}, axis=1, inplace=True)
    new.to_csv('../data/agg/CGXII_OD.csv', index=False)
    
def agg_and_save_M9():
    datasets = [
    '../data/raw/2023-02-03_M9_all.csv', # 14
    '../data/raw/2023-02-09_M9_all.csv', # 16
    '../data/raw/2023-03-29_M9_all.csv'
    ]
    # read csv files
    frames = [pd.read_csv(df) for df in datasets] 
    # add all frames to one frame
    data = pd.concat(frames, axis=0)
    # use stack() to bring short and measurment into rows
    new = pd.DataFrame(data.set_index('short').sort_index().T.stack()).reset_index().rename({0:'OD'}, axis=1)
    # split strain description
    new[['strain', 'time', 'sample']] = new.level_0.str.split('-', expand=True)
    new['strain'].replace(STRAINS_LAB, inplace=True)
    new.rename({'level_0':'lab_mapping'}, axis=1, inplace=True)
    new.to_csv('../data/agg/M9_OD.csv', index=False)
    
def agg_and_save_RPMI_LB():
    data = pd.read_csv('../data/raw/2023-02-15_RPMI-LB_all.csv')
    # use stack() to bring short and measurment into rows
    new = pd.DataFrame(data.set_index('short').sort_index().T.stack()).reset_index().rename({0:'OD'}, axis=1)
    # split strain description
    new[['strain', 'time', 'sample']] = new.level_0.str.split('-', expand=True)
    new['strain'].replace(STRAINS_LAB, inplace=True)
    new.rename({'level_0':'lab_mapping'}, axis=1, inplace=True)
    med = [v for k, v in new.groupby('short')]
    lb = med[0].append(med[1])
    lb.to_csv('../data/agg/LB_OD.csv', index=False)
    rpmi = med[2].append(med[3])
    rpmi.to_csv('../data/agg/RPMI_OD.csv', index=False)
    
def significance(entry):
    if entry <= 1.00e+00 and entry > 5.00e-02:
        return 'ns'
    elif  entry <= 5.00e-02 and entry > 1.00e-02:
        return '*'
    elif  entry <= 1.00e-02 and entry > 1.00e-03:
        return '**'
    elif  entry <= 1.00e-03 and entry > 1.00e-04:
        return '***'
    elif  entry <= 1.00e-04:
        return '****'
    
def test_between_0_and_24(df):
    test = {}
    for v, gr in df.groupby('strain'):
        for vi, gro in gr.groupby('short'):
            group1 = gro[gro['time'] == 0]
            group2 = gro[gro['time'] == 24]
            stat, res = ttest_rel(group1['OD'], group2['OD'])
            test[v, vi] = [res]
    ttest_res = pd.DataFrame(pd.DataFrame(test).unstack()).reset_index().rename({'level_0':'strain', 'level_1':'short', 0: 'pval'}, axis=1).drop('level_2', axis=1)
    ttest_res['significance'] = ttest_res['pval'].apply(significance)
    return ttest_res

def test_between_media(df):
    time = [v for k, v in df.groupby('time')]
    change = time[1]
    change['OD fold change'] = time[1]['OD'].values / time[0]['OD'].values
    change.drop(['OD', 'time'], axis=1, inplace=True)
    test = {}
    for v, gr in change.groupby('strain'):
        grps = gr['short'].unique()
        combs = combinations(grps, 2)
        ttests = {
        (c1, c2): ttest_ind(
            gr.loc[gr['short'] == c1, 'OD fold change'], 
            gr.loc[gr['short'] == c2, 'OD fold change']
            ).pvalue for c1, c2 in combs
        }
        test[v] = ttests

    ttest_res = pd.DataFrame(test).reset_index().rename({'level_0': 'group1', 'level_1':'group2'}, axis=1)
    ttest_res = pd.DataFrame(ttest_res.set_index(['group1', 'group2']).stack()).reset_index().rename({'level_2':'strain', 0: 'pval'}, axis=1)
    ttest_res['significance'] = ttest_res['pval'].apply(significance)
    ttest_res = ttest_res.set_index('strain').sort_index().reset_index()

    return ttest_res

if __name__ == '__main__':
    agg_and_save_CGXII()
    test_between_0_and_24(pd.read_csv('../data/agg/CGXII_OD.csv')).to_csv('../data/agg/CGXII_sig_0to24.csv', index=False)
    test_between_media(pd.read_csv('../data/agg/CGXII_OD.csv')).to_csv('../data/agg/CGXII_sig_additives.csv', index=False)
    agg_and_save_M9()
    test_between_0_and_24(pd.read_csv('../data/agg/M9_OD.csv')).to_csv('../data/agg/M9_sig_0to24.csv', index=False)
    test_between_media(pd.read_csv('../data/agg/M9_OD.csv')).to_csv('../data/agg/M9_sig_additives.csv', index=False)
    agg_and_save_RPMI_LB()
    test_between_0_and_24(pd.read_csv('../data/agg/RPMI_OD.csv')).to_csv('../data/agg/RPMI_sig_0to24.csv', index=False)
    test_between_media(pd.read_csv('../data/agg/RPMI_OD.csv')).to_csv('../data/agg/RPMI_sig_adds.csv', index=False)
    test_between_0_and_24(pd.read_csv('../data/agg/LB_OD.csv')).to_csv('../data/agg/LB_sig_0to24.csv', index=False)
    test_between_media(pd.read_csv('../data/agg/LB_OD.csv')).to_csv('../data/agg/LB_sig_adds.csv', index=False)

