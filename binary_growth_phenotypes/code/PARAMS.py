# styling of plots
import matplotlib

matplotlib.rcParams['figure.titlesize'] = 18
matplotlib.rcParams['axes.linewidth'] = 2
matplotlib.rcParams['figure.dpi'] = 180
matplotlib.rcParams['savefig.dpi'] = 180
matplotlib.rcParams['lines.linewidth'] = 2 
matplotlib.rcParams['errorbar.capsize'] = 8
matplotlib.rcParams["axes.spines.right"] = False
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["xtick.major.width"] = 2
matplotlib.rcParams["ytick.major.width"] = 2
matplotlib.rcParams['axes.labelsize'] = 16
matplotlib.rcParams['legend.frameon'] = False
matplotlib.rcParams['legend.fontsize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 14
matplotlib.rcParams['ytick.labelsize'] = 14

# colors and patterns
cb = ['#999999',
        '#377eb8',
        '#dede00',  
        '#984ea3', 
        '#4daf4a',   
        '#ff7f00', '#a65628', '#e41a1c', '#f781bf']
pat = ['x','x','x','x',".", ".", ".", ".", '+', '+','+','+']
colorstandards = {'14':'tab:cyan', '15':'g', '16':'darksalmon', '17': 'goldenrod'}
markers = ["D", "x", "o",  "H", "d", "p", "H",  "*"]
greys = ['dimgrey', 'dimgrey', 'dimgrey','dimgrey', 'darkgrey', 'darkgrey', 'darkgrey', 'darkgrey', 'whitesmoke', 'whitesmoke', 'whitesmoke', 'whitesmoke']
greys_5 = ['black', 'dimgrey', 'darkgrey', 'lightgrey', 'whitesmoke']
# strain naming
STRAINS_LAB = {'14':'TS', 
            '15':'1197',
            '16':'1115',
            '17':'1116',
            }