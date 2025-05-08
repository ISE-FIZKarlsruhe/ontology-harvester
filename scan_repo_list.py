import pandas as pd
import os
import glob
import re
import os.path
import shutil



df = pd.read_csv("UniqueIds - Ontologies.csv")
unique_names=[]
unique_repos=[]
for x in df['Homepage'][:]:
    try:
        ind=[x.start() for x in re.finditer('/',x)]
        cand = x[ind[2]+1:ind[3]]
        repo = x[ind[3]+1:]
    except:
        continue

    if (x[:ind[2]]=="https://github.com"):
            try:
                unique_names.index(cand)
                unique_repos.index(repo)
            except:
                unique_names.append(cand)
                unique_repos.append(repo)

print(unique_names)

N=0

check_fold="Downloads_prev"
check_f2 = "Old_downloads/TempClone_MSE"

for N in range(12,len(unique_names)):
     print ("N="+str(N))
     name = unique_names[N]
     repo = unique_repos[N]
     print("name="+name + ", repo=" + repo)
     if os.path.isdir(check_fold + "/" +name +"/"+repo):
          print("present!")
          os.system("mkdir " + " Downloads" + "\\" +name)
          os.system("cp -r " + check_fold + "\\" +name +"\\"+repo + " Downloads" + "\\" +name +"\\"+repo)
          #shutil.copy(check_fold + "/" +name +"/"+repo,"Downloads" + "/" +name +"/"+repo)
     elif os.path.isdir(check_f2 + "/" +name +"/"+repo):
          print("present2!")
          os.system("mkdir " + " Downloads" + "\\" +name)
          os.system("cp -r " + check_f2 + "\\" +name +"\\"+repo + " Downloads" + "\\" +name +"\\"+repo)
          #shutil.copy(check_fold + "/" +name +"/"+repo,"Downloads" + "/" +name +"/"+repo)
     else:
        os.system("python scan_git.py " + name +" --repo_name="+repo)
     print("end")