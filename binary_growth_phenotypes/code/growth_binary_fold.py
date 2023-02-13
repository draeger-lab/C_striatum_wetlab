# This script serves as script to produce nice plots of the binary growth results
# run from this directory using python3 growth_binary.py 
#%%
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from PARAMS import *


csv_path = 'mapping.csv'
def get_mapping(csv_path):
    map = pd.read_csv(csv_path)
    date_maps = {}
    for date in map['date']:
        maps = {}
        date_map = map[map['date'] == date]
        for strain in date_map[date_map['short'] == '+/-']['strain'].str.split(';').values[0]:
            small_maps = {}
            short_map = date_map[date_map['strain'].str.contains(strain)]
            for short in short_map['short']:
                conc = 'CGXII'
                if short_map[short_map['short'] == short][['minus']].values[0][0] is not np.nan:
                    for ent in short_map[short_map['short'] == short][['minus']].values[0][0].split(';'):
                        conc = conc + ' - ' + ent
                    #conc = conc + '\n'
                if short_map[short_map['short'] == short][['plus']].values[0][0] is not np.nan:
                    for entr in short_map[short_map['short'] == short][['plus']].values[0][0].split(';'):
                        conc =  ' + ' + entr#conc +
                small_maps[short] = conc
            maps[strain] = small_maps
        date_maps[date] = maps
    return date_maps

mapping = get_mapping(csv_path)

for date in mapping.keys():
    if date >= 221209:
        try:
            os.makedirs('figures/' + str(date) + '/')
        except (FileExistsError):
            pass
        with open('figures/' + str(date) + '/CGXII_'+ str(date) + '_legend.csv', "w") as myfile:
            myfile.write('')

        path_to_data = 'data/'
        path = 'CGXII_' + str(date)
        exp1 = pd.read_csv(path_to_data + path + '.csv')
        for strain in mapping[date].keys():
            fig, ax = plt.subplots()
            exp_0 = exp1[[strain +'-0-1', strain +'-0-2', strain +'-0-3']].dropna()
            exp_24 = exp1[[strain +'-24-1', strain +'-24-2', strain +'-24-3']].dropna()
            exp_0 = exp_0.rename({strain +'-0-1': strain + '-1',
                                strain +'-0-2': strain + '-2',
                                strain +'-0-3': strain + '-3'}, axis=1)
            exp_24 = exp_24.rename({strain +'-24-1': strain + '-1',
                                strain +'-24-2': strain + '-2',
                                strain +'-24-3': strain + '-3'}, axis=1)
            exp_fold = exp_24.div(exp_0)
            exp_fold['short'] = exp1[['short']]
            exp_fold['label'] = exp_fold['short'].map(mapping[date][strain])
            exp_fold['mean'] = exp_fold.mean(axis=1)
            err = exp_fold.std(axis=1)
            exp_fold.plot.bar('label','mean',color=cb[6], rot=0, edgecolor='k', legend=False, ax=ax)
            plt.errorbar(exp_fold['label'],exp_fold['mean'], color='k', yerr=err, fmt='none')
            ax.set_zorder(1)
            #plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
            #plt.legend(False)#loc='center left', bbox_to_anchor=(1, 0.5))
            #plt.title(strain + ' ' + path[-6:])
            plt.ylabel(r'OD fold change')
            plt.xlabel('')
            if exp_fold['mean'].max() > 0.5:
                ax.set_ylim((0,27.5))
            else:
                ax.set_ylim((0,0.5))
            #plt.yticks(np.arange(0, 1.3, 0.25))
            plt.tick_params(bottom=False)
            #plt.show()
            plt.tight_layout()
            plt.savefig('figures/' + str(date) + '/' + path + '_' + strain + '.png', bbox_inches='tight')
            plt.close()
            with open('figures/' + str(date) + '/CGXII_'+ str(date) + '_legend.csv', "a") as myfile:
                myfile.write('strain ' + str(strain) + ' ' +str(date) + '\n')
                #myfile.write(pd.DataFrame(mapping[date][strain].items(), columns=['short', 'composition']).to_latex(header=False, index=False))
            pd.DataFrame(mapping[date][strain].items(), columns=['short', 'composition']).to_csv('figures/' + str(date) + '/CGXII_'+ str(date) + '_legend.csv', mode='a', sep='\t', header=False, index=False)


# %%
