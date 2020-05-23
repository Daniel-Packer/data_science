import pandas as pd
import numpy as np
import ast
import matplotlib as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

data = pd.read_csv('magnus_nihal.csv')
data1 = data.copy()

print(data.time_pinned)


