#%% plate reader
# Note: this is a script which does automatic exports to latex, 
# for an in-depth explanation pleasee refer to plate_reader_curves.ipynb

# imports
import pandas as pd
import numpy as np # for calculating standard deviation and mean
import scipy.stats as sp # for calculating standard error
import matplotlib.pyplot as plt
import matplotlib
from pylatex import Figure, NoEscape, Subsubsection
from pylatex.utils import italic
import os
from sklearn import metrics
from scipy.optimize.minpack import curve_fit
from datetime import datetime

# matplotlib.style.use('seaborn-whitegrid')
# matplotlib.use("pgf")
# matplotlib.rcParams.update({
#     "pgf.texsystem": "pdflatex",
#     'font.family': 'serif',
#     'text.usetex': True,
#     'pgf.rcfonts': False,
# })

from PARAMS import *
# functions

def double_std(array):
 return np.std(array) * 2

def gompertz_model(t,a,b,c): #based on Franses94
    return a*np.exp(-b*np.exp(-c*t))

def logistic_mod(t, K, N0, r): #asadi2020
    return K/(1+((K-N0)/N0)*np.exp(-r*t))

def add_time(df):
    m = [isinstance(i, datetime) for i in df['Time']]
    df['timedelta'] = pd.to_timedelta(df['Time'].astype(str), errors='coerce')
    df.loc[m, 'timedelta'] = df.loc[m, 'Time'].apply(lambda t: pd.Timestamp(str(t)) - pd.Timestamp('1899-12-31'))

    df['Time'] = (df['timedelta'] - df['timedelta'][0])
    df['Time'] = df['Time'].dt.total_seconds() / 60
    df['Time'] += 15
    return df.drop('timedelta', axis=1)

def extract_columns(df, conditions, bio_rep=False, bio_rep_name=''):#, strains):
    """transforms excel table to df where the technical triplicates are averaged

    Args:
        df (pandas-df): excel from plate reader loaded
        conditions (dict): plate_layout loaded with convert_layout()
    """

    triplicates = df.iloc[:,2:].groupby(np.arange(len(df.iloc[:,2:].columns))//3, axis=1).mean()

    blank = triplicates[triplicates.columns[3::4]]
    blank.columns = np.arange(8)
    #blank.loc[:,0] = df.iloc[:,2:].loc[:,'A10'].values #use when you only want the first column of blanks 01.02.2023

    left = triplicates[triplicates.columns[::4]]
    left.columns = np.arange(8)
    left = left - blank
    left = left.rename(columns=conditions)
    left = df.iloc[:,:1].join(left, how='outer')
    left = add_time(left)

    middle = triplicates[triplicates.columns[1::4]]
    middle.columns = np.arange(8)
    middle = middle - blank
    middle = middle.rename(columns=conditions)
    middle = df.iloc[:,:1].join(middle, how='outer')
    middle = add_time(middle)

    right = triplicates[triplicates.columns[2::4]]
    right.columns = np.arange(8)
    right = right - blank
    right = right.rename(columns=conditions)
    right = df.iloc[:,:1].join(right, how='outer')
    right = add_time(right)
    
    if bio_rep:
        df_concat = pd.concat((left, middle, right))
        by_row_index = df_concat.groupby(df_concat.index)
        df_means = by_row_index.mean()
        df_errors = by_row_index.agg([np.mean, double_std, sp.sem])
        return_dict = {conditions['A']:left,
                   conditions['B']:middle,
                   conditions['C']:right,
                   bio_rep_name: df_means}
    
    else:
        return_dict = {conditions['A']:left,
                   conditions['B']:middle,
                   conditions['C']:right}
        df_errors = None
    
    return  return_dict, df_errors

def extract_growthrate(df, fit_func):

    df_growth = pd.DataFrame()
    aucs = []
    popts = {}
    pcovs = {}
    for (columnName, columnData) in df.drop('Time', axis=1).iteritems():
        auc = metrics.auc(df['Time'], columnData.values)
        aucs.append(auc)
        try:
            popts[columnName], pcovs[columnName] = curve_fit(fit_func, df['Time'], df[columnName], p0=np.asarray([0.2,0.005,0.05]))#, bounds=[[0,-1.0,-1.0],[1.0,1.0,1.0]])
        except (RuntimeError):
            print('RuntimeError for ' + columnName + ' set popts to [0,0,0]')
            popts[columnName] = np.asarray([0,0,0])
    
    fit_parameters = pd.DataFrame.from_dict(popts,
                                                orient='index',
                                                columns=['a', 'b', 'r'])
    df_growth['r'] = fit_parameters['r']
    try:
        df_growth['dt'] = np.log(2)/fit_parameters['r']
    except (ZeroDivisionError):
        print('No dt could be calculated for ' + columnName)
        df_growth['dt'] = 0
    df_growth['AUC'] = aucs
    #print(df_growth)
    
    t = np.linspace(df['Time'].min(), df['Time'].max())#, 193)

    ax = df.plot(#grid=True, 
                x="Time",
                style = 'o',
                xlabel='time [min]',
                ylabel='OD$_{600}$',
                markerfacecolor = 'None',
                #logy=True,
                #logx=True
                )

    for idx, column in enumerate(df.set_index('Time').columns):
        try:
            plt.plot(t,fit_func(t, *fit_parameters.loc[column]),
                color='C{}'.format(idx))
        except (ZeroDivisionError):
            print('No fit available for ' + column)
    ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))#
    fig = ax.get_figure() 

    return df_growth, fig

def convert_layout(plate_layout_file = 'plate_layout.csv'):
    """converts csv layout file to work with other functions

    Args:
        plate_layout_file (str): Path to csv with layout. Defaults to 'plate_layout.csv'.

    Returns:
        dict: date as keys and layout as value (entry of the row)
    """
    layout = pd.read_csv(plate_layout_file)
    layout_dict = {}

    for entry in layout.to_dict('records'):
        new_dict = {}
        for k, v in entry.items():
            try: 
                k = int(k)
                new_dict[k] = v
            except(ValueError):
                new_dict[k] = v
        layout_dict[new_dict['date']] = new_dict
    
    return layout_dict

def export_tex(growth, date, nice_date, path_to_save, texfilepath, fit_func):
    sub = Subsubsection(NoEscape('Growth behaviour of \emph{C. striatum} strains on ' + nice_date))
    #sub.append(NoEscape('Individually added metabolites are denoted in the legend of the plots and the tables. The metabolites each had a concentration of ' + convert_layout()[int(date)]['added metabs']) + '.')
    for key, value in growth.items():
        key = str(key)
        growthrate, fig = extract_growthrate(value, fit_func)
        growthrate['r'] = growthrate['r'].round(4)
        growthrate['dt'] = growthrate['dt'].round(2)
        growthrate['AUC'] = growthrate['AUC'].round(2)
        growthrate = growthrate.reset_index().rename({'index':'medium'}, axis=1)
        label = date + '_Cstr_' + key
        capt = 'Growth behaviour of \emph{C. striatum} strain ' + key + ' on ' + nice_date
        captfig = '. The lines show a fitted logistic model used to determine the growth rate r, the doubling time dt and the area under curve AUC denoted in the table on the right.'#\\ref{tab:' + label + '}.'
        #capttab = '. The dt [min], and the r [$\\frac{OD}{min}$] were calculated with the data used to generate the grow curves shown in Figure \\ref{fig:' + label + '}.'
        lat = growthrate.to_latex(
                            #caption=(str(capt+capttab), str(capt)),
                            #label='tab:' + label,
                            index = False
                            )
        filefig = path_to_save + label + '.png' #'.pgf'
        fig.savefig(filefig, bbox_inches='tight')

        with sub.create(Figure(position='H')) as plot:
            plot.append(NoEscape(r'\begin{subfigure}{.62\textwidth}'))
            plot.append(NoEscape(r'\centering'))
            #plot.append(NoEscape(r'\resizebox{\textwidth}{!}{\import{' + os.getcwd() + '/' + path_to_save + '}{' + label + '.pgf}}' ))
            plot.append(NoEscape(r'\includegraphics[width=\textwidth]{' + os.getcwd() + '/' + path_to_save + label + '.png}' ))
            plot.append(NoEscape(r'\end{subfigure}'))
            plot.append(NoEscape(r'\begin{subfigure}{.37\textwidth}'))
            plot.append(NoEscape(r'\resizebox{\textwidth}{!}{%'))
            plot.append(NoEscape(lat))
            plot.append(NoEscape(r'}'))
            plot.append(NoEscape(r'\end{subfigure}'))
            plot.append(NoEscape('\caption['+  capt + ']{' + capt + captfig + '}'))
            plot.append(NoEscape('\label{fig:' + label + '}'))
        #sub.append(NoEscape(lat))
        tex = sub.dumps()

    with open(texfilepath + 'Cstr_' + date + '.tex', "w") as text_file:
        text_file.write(tex)


# inputs
path_to_excel = 'plate_reader_results/'

###
# you only need to modify this and denote layout in plate_layout.csv
excel_file = '230201_Cstr.xlsx' 
###

date = excel_file[:6]
nice_date = date[4:] + '.' + date[2:4] + '.20' + date[:2]
plate_layout = convert_layout()[int(date)]
nrows = 0 
if plate_layout['duration'] == 24.0:
    nrows = 96 #96 for 24
if plate_layout['duration'] == 48.0:
    nrows = 193 #193 for 48h
bio_rep_name = ''
if plate_layout['biological replicates']:
    bio_rep_name = str(int(plate_layout['strain']))

df = pd.read_excel(path_to_excel+excel_file, usecols="B:CU", skiprows=57, nrows=nrows)

growth, errors = extract_columns(df, plate_layout, plate_layout['biological replicates'], bio_rep_name)
#%
export_tex(growth, date, nice_date, 'growth_curves_figures/',  '/Users/baeuerle/Organisation/Masterarbeit/thesis/files/growth_curves/', logistic_mod)

plt.close('all')
# %%
