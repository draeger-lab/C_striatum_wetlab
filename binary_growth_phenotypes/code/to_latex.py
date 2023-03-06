#%%
import pandas as pd
class_list = ['TS', '1197', '1115', '1116']

def load_and_sort(path):
    df = pd.read_csv(path)
    df = df.set_index('strain')
    df = df.loc[class_list]
    df = df.reset_index()
    df['pval'] = df['pval'].round(decimals = 5)
    return df
# %%
print(load_and_sort('../data/agg/LB_sig_0to24.csv').to_latex(index=False))
#%%
print(load_and_sort('../data/agg/M9_sig_0to24.csv').to_latex(index=False))
#%%
print(load_and_sort('../data/agg/M9_sig_additives.csv').to_latex(index=False))
# %%
print(load_and_sort('../data/agg/RPMI_sig_0to24.csv').to_latex(index=False))
#%%
print(load_and_sort('../data/agg/CGXII_sig_0to24.csv').to_latex(index=False))
#%%
print(load_and_sort('../data/agg/CGXII_sig_additives.csv').to_latex(index=False))
# %%
df = pd.read_csv('../data/agg/LB_sig_adds.csv').append(pd.read_csv('../data/agg/RPMI_sig_adds.csv'))
df['pval'] = df['pval'].round(decimals = 5)
print(df.to_latex(index=False))
# %%
