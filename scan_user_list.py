import pandas as pd
import os
import glob
import re

df = pd.read_csv("MSE_ontologies.xlsx - All ontologies.csv")
unique_names=[]
for x in df['Homepage'][:]:
    try:
        ind=[x.start() for x in re.finditer('/',x)]
        cand = x[ind[2]+1:ind[3]]
    except:
        continue

    if (x[:ind[2]]=="https://github.com"):
            try:
                unique_names.index(cand)
            except:
                unique_names.append(cand)

print(unique_names)

N=0

for N in range(len(unique_names)):
     print ("N="+str(N))
     name = unique_names[N]
     print("name="+name)
     os.system("python scan_git.py " + name)
     print("end for user="+name)