# This script serves as script to produce nice plots of the binary growth results with significance bars
# run from this directory using python3 growth_binary.py 
#%%
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from PARAMS import *
from statannotations.Annotator import Annotator