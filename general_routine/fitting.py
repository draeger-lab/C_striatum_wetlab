#%%
import pandas as pd
import numpy as np
from scipy.optimize.minpack import curve_fit
import matplotlib.pyplot as plt
from sklearn import linear_model

def logistic_mod(t, K, y0, r): #asadi2020
    return K/(1+((K-y0)/y0)*np.exp(-r*t))

def logistic(t, a, b, c):
    return a/(1+b*np.exp(-c*t))

def gompertz_model(t,K,y0,r): #based on Franses94
    return K*np.exp(np.log(y0/K) * np.exp(-r*t))

def huang(t, lam, y0, K, r): #from growthrate
    alpha = 4
    b = t + 1/alpha * np.log((1+ np.exp(-alpha * (t - lam)))/(1 + np.exp(alpha * lam)))
    #return np.exp(np.log(y0) + np.log(K) - np.log(y0 + (K-y0)*np.exp(-r*b)))
    return y0 + K - np.log(np.exp(y0) + (np.exp(K)-np.exp(y0))*np.exp(-r*b))

def richards(t, K, beta, y0, r):
    return (-K*(1-np.exp(-beta * r * t)*(1-(y0/K)**-beta))**(-1/beta))

def baranyi(t, K, y0, h0, r):
    a = t + 1/r * np.log(np.exp(-r * t) + np.exp(-h0) - np.exp(-r * t - h0))
    #log_y <- y0 + mumax * A - log(1 + (exp(mumax * A) - 1)/(exp(K - y0)))
    return np.exp(np.log(y0) + r * a - np.log(1 + (np.exp(r * a) - 1) / np.exp(np.log(K) - np.log(y0))))

#%%
df = pd.read_excel('Growth rate liquid coculture.xlsx', 'WT', usecols="B:Q", skiprows=2, nrows=49)
df
#%%
df = pd.read_excel('Growth rate liquid coculture.xlsx', 'WT', usecols="T:AL", skiprows=2, nrows=47)
df
#%%
trip = df.iloc[:,1:].groupby(np.arange(len(df.iloc[:,1:].columns))//3, axis=1).mean()
trip.rename({5:'Time'}, axis=1, inplace=True)
trip
#%%
popts, pcov = curve_fit(gompertz_model, trip['Time'], trip[3])#, p0=np.asarray([0.2,0.005,0.05]))#, bounds=[[0,-1.0,-1.0],[1.0,1.0,1.0]])
t = np.linspace(trip['Time'].min(), trip['Time'].max())#, 193)
ax = trip.plot(grid=True, 
                x="Time",
                style = '.',
                xlabel='time [min]',
                ylabel='OD$_{600}$',
                #logy=True,
                #logx=True
                )

plt.plot(t,gompertz_model(t, *popts))
print(popts)
gr = np.log(2)/popts[2]
gr

#%%
t = np.linspace(trip['Time'].min(), trip['Time'].max())#, 193)
ax = trip.plot(grid=True, x="Time", style = '.', xlabel='time [min]',ylabel='OD$_{600}$')
popts, pcov = curve_fit(huang, trip['Time'], trip[0])
plt.plot(t,huang(t, *popts))
print(popts)
gr = np.log(2)/popts[4] #(np.log(2) * popts[1] * popts[2])/66.6
gr
#%%
p0 = np.asarray([0.5, 1, 0.05, 2])#y0 = 0.05, mumax = 5,   K = 0.5)
mod = baranyi
params = 4
curve = 0
t = np.linspace(trip['Time'].min(), trip['Time'].max())#, 193)
ax = trip.plot(grid=True, x="Time", style = '.', xlabel='time [min]',ylabel='OD$_{600}$')
popts, pcov = curve_fit(mod, trip['Time'], trip[curve])
plt.plot(t,mod(t, *popts))
print(popts)
gr = np.log(2)/popts[params] #(np.log(2) * popts[1] * popts[2])/66.6
gr
#%%
df = pd.read_excel('Growth rate liquid coculture.xlsx', 'sfasbn (2)')
df.dtypes

#%%
df.iloc[:,[3]]
df['Time [h]']
trip[0]
df
#%%
popts, pcov = curve_fit(baranyi, df['Time [h]'], df.iloc[:,1])#, p0=np.asarray([0.2,0.005,0.05]))#, bounds=[[0,-1.0,-1.0],[1.0,1.0,1.0]])
t = np.linspace(df['Time [h]'].min(), df['Time [h]'].max())#, 193)
ax = df.iloc[:,[0,1]].plot(grid=True, 
                x="Time [h]",
                style = '.',
                xlabel='time [h]',
                ylabel='OD$_{600}$',
                #logy=True,
                #logx=True
                )
ax.set_yscale('log')

plt.plot(t,baranyi(t, *popts), label='baranyi')
gr = np.log(2)/popts[-1]
print(popts)
print('baranyi: ' + str(gr))

popts, pcov = curve_fit(huang, df['Time [h]'], df.iloc[:,1])
print(popts)
gr = np.log(2)/popts[-1]
print('huang: ' + str(gr))
plt.plot(t,huang(t, *popts), label='huang')

popts, pcov = curve_fit(logistic_mod, df['Time [h]'], df.iloc[:,1])#,bounds=[[0.8, 0, 0.2],[1.5, 10, 0.9]])
gr = np.log(2)/popts[-1]
print(popts)
print('logistic_mod: ' + str(gr))
plt.plot(t,logistic_mod(t, *popts), label='logistic_mod')

popts, pcov = curve_fit(logistic, df['Time [h]'], df.iloc[:,1])
gr = np.log(2)/popts[-1]
print(popts)
print(popts[0]*popts[2]/np.exp(1))
print(pcov)
print('logistic: ' + str(gr))
plt.plot(t,logistic(t, *popts), label='logistic')

popts, pcov = curve_fit(gompertz_model, df['Time [h]'], df.iloc[:,1])
gr = np.log(2)/popts[-1]
print(popts)
print('gompertz_model: ' + str(gr))
plt.plot(t,gompertz_model(t, *popts), label='gompertz_model')
plt.legend()

#%%
df['der'] = pd.Series([0]).append(pd.Series(np.diff(df.iloc[:,1]) / np.diff(df['Time [h]'])), ignore_index=True)
df.iloc[:,[0,1]].plot(x="Time [h]")
df.loc[:,['Time [h]', 'der']].plot(x="Time [h]")
df.loc[:,['der']].idxmax()
df.loc[11]['Time [h]']