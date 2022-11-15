# This script serves as script to produce nice plots of the binary growth results

#%%
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
cb = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']
matplotlib.rcParams.update({'font.size': 18})
#matplotlib.rcParams.update({'font.family': 'serif'})
matplotlib.rcParams['figure.dpi'] = 180
matplotlib.rcParams['savefig.dpi'] = 180
matplotlib.rcParams['errorbar.capsize'] = 5
matplotlib.rcParams['axes.linewidth'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.width'] = 2
#matplotlib.rcParams['xtick.minor.size'] = 10
matplotlib.rcParams['xtick.minor.width'] = 2

map = pd.read_csv('mapping.csv')
maps = {}
for entry in map['short']:

    strain_spe = {}
    pm=map[map['short']==entry]

    for strain in ['14','15','16','17']:
        st = pm.loc[pm['strain'].str.contains(strain, case=False)]

        conc = 'CGXII\n'
        if not st.empty:
            if st['minus'].values[0] is not np.nan:
                for ent in st['minus'].values[0].split(';'):
                    conc = conc + ' -' + ent
                conc = conc + '\n'
            if st['plus'].values[0] is not np.nan:
                for entr in st['plus'].values[0].split(';'):
                    conc = conc + ' +' + entr

            strain_spe[strain] = conc

    maps[entry] = strain_spe

path = 'CGXII_221028'
exp1 = pd.read_csv(path + '.csv')
for strain in ['16']:#, '15', '14', '17']:
    exp = exp1[['short', strain +'-1', strain +'-2', strain +'-3']].dropna()
    # exp = exp.replace({'short': {'-/-': maps['-/-'][strain], 
    #                       '-/+': maps['-/+'][strain],
    #                       '+/-': maps['+/-'][strain],
    #                       '+/+': maps['+/+'][strain]}})
    # try:
    #    exp = exp.replace({'short':{'-/++': maps['-/++'][strain],
    #                                '+/++': maps['+/++'][strain]}})
    # except:
    #    pass
    exp['mean'] = exp.mean(axis=1)
    err = exp.std(axis=1)
    ax = exp.plot.bar('short','mean',color=cb[6], rot=0, edgecolor='k', legend=False)#, marker='x', s=50, )
    plt.errorbar(exp['short'],exp['mean'], color='k', yerr=err, fmt='none', lw=2)
    ax.set_zorder(1)
    #plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
    #plt.legend(False)#loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(strain + ' ' + path[-6:])
    plt.ylabel('OD 600')
    plt.xlabel('')
    ax.set_ylim((0,0.5))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    #plt.yticks(np.arange(0, 1.3, 0.25))
    plt.tick_params(bottom=False)
    #plt.show()
    plt.savefig('growth_binary_figures/'+ path + '_' + strain + '.png', bbox_inches='tight')
    plt.close()

#%% test of sns stripplot
exp_14 = exp1[['short','14-1', '14-2', '14-3']].dropna()
exp_14 = exp_14.replace({'short': {'-/-': maps['-/-']['14'], 
                          '-/+': maps['-/+']['14'],
                          '+/-': maps['+/-']['14'],
                          '+/+': maps['+/+']['14']}})
exp_14['mean'] = exp_14.mean(axis=1)
exp_14 = exp_14.set_index('short').stack().reset_index()
exp_14.columns=['short','strain','data']
sns.stripplot(data=exp_14, x='short', y='data', hue='strain', palette='colorblind', jitter=True, s=10)
plt.xticks(rotation=45, horizontalalignment='right')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.ylabel('OD 600')
plt.xlabel('')
plt.ylim([0,0.2])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
#ax.spines['bottom'].set_visible(False)
plt.tick_params(bottom=False)

# %%
