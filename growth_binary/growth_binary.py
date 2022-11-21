# This script serves as script to produce nice plots of the binary growth results
# run from this directory using python3 growth_binary.py 

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
                        conc = conc + ' + ' + entr
                small_maps[short] = conc
            maps[strain] = small_maps
        date_maps[date] = maps
    return date_maps

mapping = get_mapping(csv_path)

for date in mapping.keys():
    try:
        os.makedirs('growth_binary_figures/' + str(date) + '/')
    except (FileExistsError):
        pass
    with open('growth_binary_figures/' + str(date) + '/CGXII_'+ str(date) + '_legend.csv', "w") as myfile:
        myfile.write('')

    path_to_data = 'growth_binary_results/'
    path = 'CGXII_' + str(date)
    exp1 = pd.read_csv(path_to_data + path + '.csv')
    for strain in mapping[date].keys():
        fig, ax = plt.subplots()
        exp = exp1[['short', strain +'-1', strain +'-2', strain +'-3']].dropna()
        exp['mean'] = exp.mean(axis=1)
        err = exp.std(axis=1)
        exp.plot.bar('short','mean',color=cb[6], rot=0, edgecolor='k', legend=False, ax=ax)
        plt.errorbar(exp['short'],exp['mean'], color='k', yerr=err, fmt='none')
        ax.set_zorder(1)
        #plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
        #plt.legend(False)#loc='center left', bbox_to_anchor=(1, 0.5))
        plt.title(strain + ' ' + path[-6:])
        plt.ylabel(r'OD$_{600}$')
        plt.xlabel('')
        if exp['mean'].max() > 0.5:
            ax.set_ylim((0,2.2))
        else:
            ax.set_ylim((0,0.5))
        #plt.yticks(np.arange(0, 1.3, 0.25))
        plt.tick_params(bottom=False)
        #plt.show()
        plt.tight_layout()
        plt.savefig('growth_binary_figures/' + str(date) + '/' + path + '_' + strain + '.png', bbox_inches='tight')
        plt.close()
        with open('growth_binary_figures/' + str(date) + '/CGXII_'+ str(date) + '_legend.csv', "a") as myfile:
            myfile.write('strain ' + str(strain) + ' ' +str(date) + '\n')
            #myfile.write(pd.DataFrame(mapping[date][strain].items(), columns=['short', 'composition']).to_latex(header=False, index=False))
        pd.DataFrame(mapping[date][strain].items(), columns=['short', 'composition']).to_csv('growth_binary_figures/' + str(date) + '/CGXII_'+ str(date) + '_legend.csv', mode='a', sep='\t', header=False, index=False)

