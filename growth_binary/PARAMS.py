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
cb = ['#377eb8', '#ff7f00', '#4daf4a','#f781bf', '#a65628', '#984ea3','#999999', '#e41a1c', '#dede00']
pat = ['x','x','x','x',".", ".", ".", ".", '+', '+','+','+']
colorstandards = {'14':'tab:cyan', '15':'g', '16':'darksalmon', '17': 'goldenrod'}
markers = ["D", "x", "o",  "H", "d", "p", "H",  "*"]