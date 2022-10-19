#%% plate reader
from audioop import add
from distutils import extension
from tkinter import Label
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pylatex import Subsection, Tabular, Figure, NoEscape, Subsubsection
from pylatex.utils import italic
import os
from sklearn import metrics
from IPython.display import display, HTML
from scipy.stats import gompertz
from scipy.optimize.minpack import curve_fit
from scipy.integrate import trapz


matplotlib.style.use('seaborn-whitegrid')

def extract_columns(df, conditions):#, strains):
    """transforms excel table to df where the technical triplicates are averaged

    Args:
        df (pandas-df): excel from plate reader loaded
        conditions (dict): plate_layout loaded with convert_layout()
    """
    
    def add_time(df):
        df['Time']= pd.to_timedelta(df['Time'].astype(str))
        df['Time'] = (df['Time'] - df['Time'][0])
        df['Time'] = df['Time'].dt.total_seconds() / 60
        df['Time'] += 15
        return df

    triplicates = df.iloc[:,2:].groupby(np.arange(len(df.iloc[:,2:].columns))//3, axis=1).mean()

    blank = triplicates[triplicates.columns[3::4]]
    blank.columns = np.arange(8)

    left = triplicates[triplicates.columns[::4]]
    left.columns = np.arange(8)
    left = left - blank
    left = left.rename(columns=conditions)
    left = df.iloc[:,:1].join(left, how='outer')
    #for col in left.columns:
    #    if col == 'Time':
    #        pass
    #    else:
    #        left[col] = left[col].apply(lambda x: np.log(x))
    left = add_time(left)
    #print(left.drop('Time', axis=1).diff().eval('Time'))
    #print((left['TSB'].diff()/15.0).idxmax()*15)
    #print((left['TSB'].diff()/15.0).max())
    #(left['TSB'].diff()/15.0).plot()

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
    
    return_dict = {conditions['A']:left,#strains[0]:left, 
                   conditions['B']:middle,#strains[1]:middle,
                   conditions['C']:right}#strains[2]:right}
    
    return  return_dict

#plt.savefig('growth_curves/growth_210831_14.png',bbox_inches='tight', dpi=300)

def extract_growthrate(df, t1, t2, strain):
    #slope, intercept = np.polyfit(np.log(df[medium]), np.log(df['Time']), 1)

    od1 = df.loc[df['Time']==t1].drop('Time', axis=1).values[0]
    od2 = df.loc[df['Time']==t2].drop('Time', axis=1).values[0]
    
    mark1 = df.index[df['Time']==t1].tolist()[0]
    mark2 = df.index[df['Time']==t2].tolist()[0]

    
    #growth_rate = np.log(od2)-np.log(od1)
    #n = growth_rate/np.log(2)
    #doubling_time = (t2-t1) / n
    
    def gompertz_model(x,a,b,c): #based on Franses94
        return a*np.exp(-b*np.exp(-c*x))
    
    cols = list(df.columns.values)[1:]

    df_growth = pd.DataFrame()#growth_rate, doubling_time).reset_index().T
    #df_growth.set_axis(cols, axis=1,inplace=True)
    #df_growth.rename(index={'index':'doubling time', 0:'growth rate'}, inplace=True)
    aucs = []
    popts = {}
    pcovs = {}
    for (columnName, columnData) in df.drop('Time', axis=1).iteritems():
        auc = metrics.auc(df['Time'], columnData.values)
        aucs.append(auc)
        popts[columnName], pcovs[columnName] = curve_fit(gompertz_model, df['Time'], df[columnName], p0=np.asarray([0.5,100.0,0.005]))
    
    fit_parameters = pd.DataFrame.from_dict(popts,
                                                orient='index',
                                                columns=['a', 'b', 'growth rate'])
    df_growth['growth rate'] = fit_parameters['growth rate']
    df_growth['doubling time'] = np.log(2)/fit_parameters['growth rate']
    df_growth['AUC'] = aucs
    #fit_parameters.drop(['a', 'b'], axis=1, inplace=True)
    #fit_parameters.append(pd.Series(aucs, index = fit_parameters.columns), ignore_index=True).fillna(0).set_index('index').rename(index={0: 'AUC'}).rename_axis(None).drop(['a', 'b'], axis = 1)
    #print(fit_parameters)
    
    t = np.linspace(df['Time'].min(), df['Time'].max(), 96)

    #fig, ax = plt.subplots()
    ax = df.plot(grid=True, 
                x="Time",
                style = '.',
                #markevery=[mark1, mark2],
                #marker='o', 
                #title=r'$\it{C. striatum}$ ' + str(strain) + ' growth',
                xlabel='time [min]',
                ylabel='OD$_{600}$',
                #logy=True,
                #logx=True
                )
    
    #print(fit_parameters)
    for idx, column in enumerate(df.set_index('Time').columns):
        plt.plot(t,gompertz_model(t, *fit_parameters.loc[column]),
                color='C{}'.format(idx))
    ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))#
    fig = ax.get_figure() 
        
    #df_growth = df_growth.reset_index().append(pd.Series(aucs, index = df_growth.columns), ignore_index=True).fillna(0).set_index('index').rename(index={0: 'AUC'}).rename_axis(None)
    print(df_growth)
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
#%
path_to_excel = 'plate_reader_results/'
excel_file = '220615_Cstr.xlsx'
date = excel_file[:6]
nice_date = date[4:] + '.' + date[2:4] + '.20' + date[:2]
#print(nice_date)

df = pd.read_excel(path_to_excel+excel_file, usecols="B:CU", skiprows=57, nrows=96)

growth = extract_columns(df, convert_layout()[int(date)])

#%%
for key, value in growth.items():
    key = str(key)
    growthrate, fig = extract_growthrate(value, 225.0, 300.0, key)
    print(growthrate)

#%

def export_tex(growth, t1, t2, date, nice_date, path_to_save, texfilepath):
    sub = Subsubsection(NoEscape('Growth behaviour of \emph{C. striatum} strains on ' + nice_date))
    sub.append(NoEscape('Individually added metabolites are denoted in the legend of the plots and the tables. The metabolites each had a concentration of ' + convert_layout()[int(date)]['added metabs']) + '.')
    for key, value in growth.items():
        key = str(key)
        growthrate, fig = extract_growthrate(value, t1, t2, key)
        #print(growthrate.to_markdown())
        #display(HTML(growthrate.round(2).to_html()))
        growthrate['growth rate'] = growthrate['growth rate'].round(4)
        growthrate['doubling time'] = growthrate['doubling time'].round(2)
        growthrate['AUC'] = growthrate['AUC'].round(2)
        growthrate = growthrate.reset_index().rename({'index':'medium'}, axis=1)
        label = date + '_Cstr_' + key
        capt = 'Growth behaviour of \emph{C. striatum} strain ' + key + ' on ' + nice_date
        captfig = '. The lines show a fitted gompertz model used to determine the growth rate and the doubling time which is denoted in Table \\ref{tab:' + label + '}.'
        capttab = '. The doubling time [min], and the growth rate [$\\frac{OD}{min}$] were calculated with the data used to generate the grow curves shown in Figure \\ref{fig:' + label + '}.'
        #growthrate.to_latex(path_to_save + 'Cstr_' + key + '_' + date + '.tex', 
        #                    caption= str(capt),
        #                    label='tab:' + label,
        #                    index = False)
        lat = growthrate.to_latex(
                            caption=(str(capt+capttab), str(capt)),
                            label='tab:' + label,
                            index = False
                            )
        filefig = path_to_save + label + '.png'
        fig.savefig(filefig, bbox_inches='tight')
        #plt.show()
        
        #sub.append('Strain '+ key)
        with sub.create(Figure(position='htbp')) as plot:
            plot.add_image(os.path.abspath(os.getcwd()) + '/' + filefig)
            plot.append(NoEscape('\caption['+  capt + ']{' + capt + captfig + '}'))
            #plot.add_caption(NoEscape(capt + captfig))
            plot.append(NoEscape('\label{fig:' + label + '}'))
        sub.append(NoEscape(lat))
        tex = sub.dumps()
        #print(tex)

    with open(texfilepath + 'Cstr_' + date + '.tex', "w") as text_file:
        text_file.write(tex)
            
export_tex(growth, 225.0, 300.0, date, nice_date, 'growth_curves/',  '../thesis/files/growth_curves/')

#%%
df = growth[14]
slope, intercept = np.polyfit(np.log(df['SNM(+Vit)+cmp']), np.log(df['Time']), 1)
print(slope)

#%%
import pandas as pd
import curveball

def growth_model(x,y,model_name=None,save=False,filename="growthcurve.png"):
    """This function takes the provided (preprocessed) data to plot a growthcurve.


    The model parameter takes an element of curveball.baranyi_roberts_model.
    More information here: https://curveball.yoavram.com/models

    Args:
        x (list): x values (in this case time)
        y (list): y values (in this case optical density)
        model_name (optional): The model parameter takes an element of curveball.baranyi_roberts_model. More information here: https://curveball.yoavram.com/models. Defaults to None.
        save (boolean, optional): if True, the generated figure will be saved. Defaults to False.
        filename (string), optional): filename of the saved figure. Figure will only be saved if save=True. Defaults to "growthcurve.png".
    """
    df = pd.DataFrame(list(zip(x,y)), columns=["Time","OD"])
    print(df.head())
    df = df.dropna()
    models, fig, ax = curveball.models.fit_model(df,PLOT=True,
    PRINT=False, models=model_name)
    if save: fig.savefig(filename)
    
#%%
res, fig, ax = curveball.models.fit_model(growth[14].rename({'SNM(+Vit)+cmp':'OD'}, axis=1),PLOT=True,PRINT=False)
print(curveball.models.find_max_growth(res[0]))
#%%
growth[14]#.rename({'SNM(+Vit)+cmp':'OD'}, axis=1)
growth[14]['Time']
#%%
auc = metrics.auc(growth[14]['Time'], growth[14].drop('Time', axis=1))
auc

#%%
from matplotlib.pyplot import figure, show
from numpy import pi, sin, linspace, exp, polyfit

growth = extract_columns(df, convert_layout()[int(date)])

for key, value in growth.items():


    x = value['Time']
    y = value['SNM(+Vit)+cmp']
    
    for j in range(0, len(value['Time'])-10):
        if value['SNM(+Vit)+cmp'].iloc[j+10] - value['SNM(+Vit)+cmp'].iloc[j] > 0.05:
            break
    
    
    for i in range(0, len(value['Time'])-20):
        if value['SNM(+Vit)+cmp'].iloc[i+20] - value['SNM(+Vit)+cmp'].iloc[i] < 0.02:
            break
    
    j = j+10
    print(value['Time'].iloc[j], value['Time'].iloc[i])
    coefs = polyfit(x.iloc[j:i],y.iloc[j:i],1)
    y_linear = x.iloc[j:i] * coefs[0] + coefs[1]

    fig = figure()
    ax = fig.add_subplot(111)
    ax.plot(x,y,'ro')
    ax.plot(x.iloc[j:i],y_linear,'b-')
    print(coefs[0]*1000)
    
#%%
import math
from scipy.optimize import curve_fit
def gompertz_model(x,a,b,c): #based on Franses94
    return a*np.exp(-b*np.exp(-c*x))

def logistic(x, A, mu, lam):
    return A/(1+np.exp(((4*mu)/A)*(lam-x)+ 2))

df = growth['16'].set_index('Time')

def fit_to_dataframe(df, function, parameter_names):
    popts = {}
    pcovs = {}

    for c in df.columns:
        popts[c], pcovs[c] = curve_fit(function, df.index, df[c], p0=np.asarray([0.5,100.0,0.005]))

    fit_parameters = pd.DataFrame.from_dict(popts,
                                            orient='index',
                                            columns=parameter_names)
    
    fit_parameters['doub'] = np.log(2)/fit_parameters['growth']
    return fit_parameters

fit_parameters = fit_to_dataframe(df, gompertz_model, parameter_names=['asymp', 'versch', 'growth'])
print(fit_parameters)

def plot_fit_results(df, function, fit_parameters):
    NUM_POINTS = 50
    t = np.linspace(df.index.values.min(), df.index.values.max(), NUM_POINTS)
    df.plot(style='.')
    for idx, column in enumerate(df.columns):
        plt.semilogx(t,
                 function(t, *fit_parameters.loc[column]),
                 color='C{}'.format(idx),
                 )
    plt.show()

plot_fit_results(df, gompertz_model, fit_parameters.drop('doub', axis=1))