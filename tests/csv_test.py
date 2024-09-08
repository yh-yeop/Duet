import pandas
import numpy
from pprint import pprint

df=pandas.read_csv("Duet/assets/level/test_level.csv")
df_list=[list(df.loc[i].to_dict().values()) for i in range(len(df))]
true_list=[i for i in df_list]
pprint(df_list)
print("\n\n\n\n")
pprint(true_list)
print("\n\n\n\n")
for i in true_list:
    for ii in i:
        print(ii,str(ii)=="nan")