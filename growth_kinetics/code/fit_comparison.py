#%%

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from scipy.optimize import curve_fit
import numpy as np
import math

def gompertz_model(t,a,b,c): #based on Franses94 and Korkmaz2020
    return a*np.exp(-b*np.exp(-c*t))

def gompertz_model_mod(t,A,lam,mu):#, alpha, t_shift): 
    return A*np.exp(-np.exp(((mu*math.e)/A)*(lam-t) + 1))# + A*np.exp(alpha*(t-t_shift))

def logistic(t, a, b, c):
    return a/(1+b*np.exp(-c*t))

def logistic_mod(t, K, N0, r): #asadi2020
    return K/(1+((K-N0)/N0)*np.exp(-r*t))

def huang(t, lam, y0, K, r): #from growthrate
    alpha = 4
    b = t + 1/alpha * np.log((1+ np.exp(-alpha * (t - lam)))/(1 + np.exp(alpha * lam)))
    #return np.exp(np.log(y0) + np.log(K) - np.log(y0 + (K-y0)*np.exp(-r*b)))
    return y0 + K - np.log(np.exp(y0) + (np.exp(K)-np.exp(y0))*np.exp(-r*b))


df = pd.read_csv('/Users/baeuerle/Organisation/Masterarbeit/C_striatum_wetlab/growth_kinetics/data/media_avg/2021-09-15_Cstr14_SNMVitcmp.csv')

fig, ax = plt.subplots(1, 1)

ax.plot(df['Time'], 
        df['SNM(+Vit)+cmp'],
        label='experimental data',
        marker='.',
        #markerfacecolor='None',
        linestyle = 'None',
        )

ax.set_yscale('log')
ax.set_xlabel('time [min]')
ax.set_ylabel('OD')
ax.set(xlim=(0, 1000))
ax.set_title('Strain 14 on SNM(+Vit)+cmp')

t = np.linspace(df['Time'].min(), df['Time'].max(), 96)

popts, pcovs = curve_fit(gompertz_model, df['Time'], df['SNM(+Vit)+cmp'], p0=np.asarray([0.5,0.05,0.005]))

fit_gompertz = pd.DataFrame(popts,
                                        #orient='index',
                                        index=['asymptote', 'displacement / lag', 'growth rate'], 
                                        columns=['gompertz']).T


plt.plot(t,gompertz_model(t, *popts),
         label='gompertz fit')

popts, pcovs = curve_fit(logistic_mod, df['Time'], df['SNM(+Vit)+cmp'], p0=np.asarray([0.5,0.05,0.005]))

plt.plot(t,logistic_mod(t, *popts),
         label='logistic fit')

fit_logistic = pd.DataFrame(popts,
                                        #orient='index',
                                        index=['asymptote', 'N0', 'growth rate'], columns=['logistic']).T

popts, pcovs = curve_fit(huang, df['Time'], df['SNM(+Vit)+cmp'])#, p0=np.asarray([0.5,0.05,0.005]))

plt.plot(t,huang(t, *popts),
         label='huang')

fit_huang = pd.DataFrame(popts,
                                        #orient='index',
                                        index=['displacement / lag', 'y0', 'asymptote', 'growth rate'], columns=['huang']).T

plt.legend()#(loc="lower right")

fit_gompertz['doubling time'] = np.log(2)/fit_gompertz['growth rate']
fit_logistic['doubling time'] = np.log(2)/fit_logistic['growth rate']
fit_huang['doubling time'] = np.log(2)/fit_huang['growth rate']
fit_gompertz.T['logistic'] = fit_logistic.T['logistic']
print(fit_gompertz.append(fit_logistic).append(fit_huang).T.to_latex())
print(fit_logistic.T)

#%%