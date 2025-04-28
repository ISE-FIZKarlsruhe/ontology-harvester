import os
import glob
import re
import pandas as pd


def create_repos_csv(outname):
    try:
        os.remove(outname)
    except:
        pass
    f = open(outname,'a')
    line = ("#,link,number of ontology files, number of non-ontology rdf-like files, first commit, last commit")
    f.write(line)
    f.close()
def add_to_repo_csv(outname,link,onto_num,rdf_num,firstComm,lastComm):
    f = open(outname,'r')    
    count = sum(1 for line in f)
    f.close()     
    f = open(outname,'a')  
    num = count
    line = "\n"+str(count)+","
    line += link+","
    line += str(onto_num)+"," 
    line += str(rdf_num)+"," 
    line += firstComm+","
    line += lastComm+","
    f.write(line)
    f.close()    

def create_csv(outname):
    try:
        os.remove(outname)
    except:
        pass
    f = open(outname,'a')
    #line = ("#,title,Link (URL/PID),Link to repository,creator,description")
    line = ("#,title,Link (URL/PID),Repository address,Link inside repository,creator,license,contact,documentation link,related project, version, module, branch, type,extension, description")
    f.write(line)
    f.close()

def add_to_csv(outname,url,title,creator,gitlink,filelink,descr,license,contact,documentation,proj,vers,module,branch,otype,extens):
    maxlen=4000
    f = open(outname,'r')    
    count = sum(1 for line in f)
    f.close()     
    f = open(outname,'a')  
    num = count
    line = "\n"+str(count)+","
    title = title.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')
    line += title+","
    line += url+","
    line += gitlink+","       
    line += filelink+","
    creator= creator.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')
    if (len(creator)>maxlen):
        creator = creator[:maxlen]
    line += creator.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","   
    line += license.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    line += contact.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    line += documentation.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    line += proj.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    #no linebreaks in version
    vers_fixed = vers.split("\n")
    #print("VERSION=")
    #print(vers_fixed)
    line += vers_fixed[0].replace(',', ';')+","
    line += module+","
    line += branch+","
    line += otype+","
    line += extens+","
    
    descr = descr.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')
    if (len(descr)>maxlen):
        descr = descr[:maxlen]
    line += descr+"," 
    f.write(line)
    f.close()    