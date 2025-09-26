import os
import glob
import re
import pandas as pd
import pygit2
from pygit2 import Repository
from pygit2.enums import SortMode
import time
from github import Github
from github import Auth

def get_user_repos(user,git):
    user = git.get_user(user) # target user
    repos = user.get_repos()
    
    useful = []
    for repo in repos:
        if repo.fork is False:
            useful.append(repo.name)
    
    print(useful)   
    return useful

def clone_repo(folder,user,repo_name):
    prefix="https://github.com/"
    prefix+="/"+user+"/"
    clone_subfold="/"+user+"/"+repo_name
    try:
        #print("link=" + prefix+repo_name)
        repoClone = pygit2.clone_repository(prefix+repo_name, folder+clone_subfold)    
        print("cloned " + repo_name)
    except Exception as e:
        print("error for " + repo_name + str(e))
        
def seconds_epoch_to_date(value):
    dt=time.gmtime(value)
    date = str(dt.tm_mday) + "." + str(dt.tm_mon) + "."+str(dt.tm_year) 
    print(date)
    return date
    
def extract_info(filename,lastname):
    this_ontology_url = path2url(filename)
    emtest=Graph()
    emtest.parse(this_ontology_url)
    
    names=[]
    titles = []
    descrs=[]
    abstrs=[]
    creators=[]
    descands=[]
    
    qres = emtest.query(allq)
    
    for row in qres:
        #names.append(row.entity)
        #print(row)
        if (row.o==onto_lit):
            names.append(row.s)
        if (row.p==title_pur):
            titles.append(row.o)
        if (row.p==descript_pur):
            descrs.append(row.o)
        if (row.p==creator_pur):
            creators.append(row.o)
        if (row.p==descript_pur):
            descands.append(row)
        if (row.p==abstract_pur):
            descands.append(row)
        if (row.p==descr2):
            descands.append(row)
    
    result = ["" for i in range(5)]      
    try:
        print(names[0])
        result[0]=names[0]
    except:
        print("no name")
        return []
        
    #try to get description
    for row in descands:
        if (row.p==descript_pur):
            if (row.s==names[0]):
                descrs.append(row.o)
        if (row.p==descr2):
            if (row.s==names[0]):
                descrs.append(row.o)
        if (row.p==abstract_pur):
            if (row.s==names[0]):
                descrs.append(row.o)


        
    if (len(titles)>0):
        print(titles[0])
        result[1]=titles[0]
    if (len(creators)>0):
        result[2]=creators[0]
        print(creators[0])
        
def get_first_last_commit(repo):
    i=0
    for commit in repo.walk(repo.head.target, SortMode.TOPOLOGICAL):
        if (i==0):
            d2=seconds_epoch_to_date(commit.commit_time)
        i+=1
    d1=seconds_epoch_to_date(commit.commit_time)
    return [d2,d1]

def extract_license(path):
    try:
        f = open(path+"\\LICENSE", 'r')
        lic = f.readline()
        return lic.replace('\n', '')
        f.close()
    except:
        return "no info"

def extract_readme(path,ai_client):
    try:
        with open(path+"\\README.md", 'r') as file:
            data = file.read().replace('\n', '')
    except:
        print("No readme!!")
        return ['no info','no info','no info']
    
    start_phrase = "Please read the following text and provide in separate lines, without additional symbols."
    
    start_phrase += "first line: link to the documentation, preceded by the phrase 'documentation link:'. If not available, write 'no info' instead of the link, "
    start_phrase += "second line: contact person information, preceded by the phrase 'contact person info:'. If not available, write 'no info' instead of the contact person information, "
    start_phrase += "third line: related grant or project information without line breaks, preceded by the phrase 'related project info:'. If not available, write 'no info'."
    
    start_phrase += " ." + data
    #start_phrase += ". In a separate last sentence provide the source."
    
    response = ai_client.chat.completions.create(
        model="gpt-35", # model = "deployment_name".
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": start_phrase}
        ]
    )
    #print(response.choices[0].message.content.format(1))
    #return(response.choices[0].message.content.format(1))
    wordlist=["ocumentation link:","person info:", "roject info:"]
    ind=0
    answers=[]
    ssp = response.choices[0].message.content.format(1).split('\n')
    for subline in ssp:
        print (subline)
        word = wordlist[ind]
        try:
            i = subline.index(word)
            #print(i)
            answers.append(subline[subline.index(word) + len(word)+1:])
            ind+=1
            if (ind==3):
                break
        except:
            pass
            
    if (len(answers)<3):
        return ['no info','no info','no info']
    return answers

