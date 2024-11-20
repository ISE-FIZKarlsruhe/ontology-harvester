import os
import glob
import re
import pandas as pd


  
def create_csv(outname):
    try:
        os.remove(outname)
    except:
        pass
    f = open(outname,'a')
    #line = ("#,title,Link (URL/PID),Link to repository,creator,description")
    line = ("#,title,Link (URL/PID),Link to repository,creator,license,contact,documentation link,related project,first commit date,last commit date,description")
    f.write(line)
    f.close()

def add_to_csv(outname,url,title,creator,gitlink,descr,license,contact,documentation,proj,firstComm,lastComm):
    maxlen=200
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
    creator= creator.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')
    if (len(creator)>maxlen):
        creator = creator[:maxlen]
    line += creator.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","   
    line += license.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    line += contact.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    line += documentation.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    line += proj.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')+","
    line += firstComm+","
    line += lastComm+","

    descr = descr.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace(',', ';')
    if (len(descr)>maxlen):
        descr = descr[:maxlen]
    line += descr+"," 
    f.write(line)
    f.close()    