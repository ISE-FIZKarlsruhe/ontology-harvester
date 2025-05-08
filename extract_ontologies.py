import time
from github import Github
from github import Auth
from pygit2 import Repository
import glob
import re
import os
import os.path
from rdflib import BNode, URIRef, Literal, Graph, Namespace
from rdflib.collection import Collection
from rdflib.util import guess_format
from rdflib.namespace import RDF, XSD, RDFS, OWL, SKOS, DCTERMS, NamespaceManager
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime
from urllib.request import urlopen, pathname2url
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Tuple
import argparse
import sys
sys.path.insert(1, './lib')  #path to local libraries
import csv_io
import ontoinfo
import gitcrawl

# Instantiate the parser
parser = argparse.ArgumentParser(description='Scans all the repositories inside the folder and outputs a CSV file with found ontologies')

# Required positional argument - folder argument
parser.add_argument('folder_arg', type=str,
                    help='A required string argument - folder with clones repositories')
# Optional argument
parser.add_argument('--ontology_filename', type=str,
                    help='Optional: name of the output csv file for ontologies')
# Optional argument
parser.add_argument('--repositories_filename', type=str,
                    help='Optional: name of the output csv file for repositories')

args = parser.parse_args()

folder=""

try:
    print("Folder to scan: " + args.folder_arg)
    folder = args.folder_arg
except:
    print("Error:provide a folder name with cloned repositories!")
    exit()

try:
    ooutname = args.ontology_filename
except:
    pass

try:
    routname = args.repositories_filename
except:
    pass

if (ooutname==None):
        ooutname="Ontologies.csv"
if (routname==None):
        routname="Repositories.csv"

print("Ontologies output file name: " + ooutname)
print("Repositories output file name: " + routname)

if (not os.path.isfile(ooutname)):
    print("creating ontology output file")
    csv_io.create_csv(ooutname)
else:
     print("appending to the ontology output file")    

if (not os.path.isfile(routname)):
    print("creating repositories output file")
    csv_io.create_repos_csv(routname)
else:
     print("appending to the repositories output file")   

def get_ai_model():
    from openai import AzureOpenAI
    ai_client = AzureOpenAI(
      azure_endpoint = "https://my-east.openai.azure.com/", 
      api_key="XXX",   #add your own key
      api_version="2023-05-15"
    )

    #modelName="Microsoft.CognitiveServicesOpenAI-20240111194907"
    #deployment_name='gpt-35'
    #return ai_client       
    return []  #uncomment above for ai usage

try:
    my_ai = get_ai_model()
except:
     my_ai=[]
     pass

gitlinks=[]
user_folders = [ f.name for f in os.scandir(folder) if f.is_dir() ]
print("These Git users are found inside " + folder + " directory:")
print(user_folders)

for user in user_folders:
    repo_list = [ f.name for f in os.scandir(folder + "/" + user) if f.is_dir() ]
    print("These Git repositories are found for user " + user + ":")
    print(repo_list)
    for repo in repo_list:
            time.sleep(1)
            print("NEXT REPOSITORY")
            try:
                n_onto=0
                n_rdf=0
                branches=[]
                prefix="https://github.com"
                subfold="/"+user+"/"+repo
                print("link=" + prefix + subfold)
                repath = folder+subfold 
                    
                try:
                    repobj = Repository(repath)
                except:
                    print("repo failed to found?")
                    continue

                #INFO FROM REPOSITORY ITSELF
                [lastdate,inidate] = gitcrawl.get_first_last_commit(repobj)   #first.вфіе commit date

                if (my_ai!=[]):
                    read_info = gitcrawl.extract_readme(repath,my_ai)        #parse README.md if available (with AI currently)
                else:
                    read_info = ["no info","no info","no info"]       #otherwise no info - contact point, related project, documentation link
            
                lic_info = gitcrawl.extract_license(repath)        #get first line of the LICENSE file
            
                #looking for onto files
                onto_infos=[]
                scores=[]
                maxscore=-1
                for ext in ontoinfo.ext_list:  #check all ontology extensions
                        files = glob.glob(repath + '/**/*.' + ext, recursive=True)
                        for fi in files:
                            success = ontoinfo.querry_successful(fi)  #test querryability of the file
                            if (success):
                                n_rdf+=1
                                #LINK TO THE FILE (default branch)
                                x=fi[len(folder):].replace("\\","/")
                                inds = [x.start() for x in re.finditer('/',x)] #indexe of "/"
                                ind=inds[2]                     
                                branch = Repository(folder + x[:ind]).head.shorthand
                                print("head="+x)
                                if ("more_branches" in fi):
                                    s_ind = inds[3]
                                    e_ind = inds[4]
                                    n_ind = s_ind + len("more_branches/")
                                    branch = x[s_ind+1:n_ind]
                                    print("branch="+branch)
                                    filelink = x[:ind] + "/tree/"+branch + x[e_ind:]
                                else:
                                    filelink = x[:ind] + "/tree/" + branch + x[ind:]

                                if (branch not in branches):
                                    branches.append(branch)

                               # print(filelink)

                                just_filename=x[inds[-1]+1:]
                                print(just_filename)
                                onto_type = ""
                                if ("_base" in just_filename) | ("-base" in just_filename):
                                    onto_type="base"
                                if ("_edit" in just_filename) | ("-edit" in just_filename):
                                    onto_type="edit"
                                if ("_inferred" in just_filename) | ("-inferred" in just_filename):
                                    onto_type="inferred"
                                if ("_full" in just_filename) | ("-full" in just_filename):
                                    onto_type="full"
                                if ("_simple" in just_filename) | ("-simple" in just_filename):
                                    onto_type="simple"
                                if ("_export" in just_filename) | ("-export" in just_filename):
                                    onto_type="export"
                                if ("_import" in just_filename) | ("-import" in just_filename):
                                    onto_type="import"
                                if ("_simple" in just_filename) | ("-simple" in just_filename):
                                    onto_type="simple"

                                #print("type="+onto_type)
                                    
                                # LINK TO REPOSITORY
                                gitlink = prefix + subfold

                                #extract information from ontology file
                                oinfo_fill = ontoinfo.extract_info(fi,filelink)   
                              #  print(oinfo_fill)
                                #add to the csv file
                                if (oinfo_fill!=[]):
                                        n_onto+=1
                                        csv_io.add_to_csv(ooutname,oinfo_fill[0],oinfo_fill[1],oinfo_fill[2],gitlink,oinfo_fill[3],oinfo_fill[4],lic_info,read_info[1],read_info[0],read_info[2],oinfo_fill[5],oinfo_fill[6],branch,onto_type,ext)
            
                if (n_onto>=0):
                    if (gitlink not in gitlinks):
                        gitlinks.append(gitlink)
                        csv_io.add_to_repo_csv(routname,gitlink,n_onto,n_rdf-n_onto,inidate,lastdate)

            except Exception as inst:
                    print(inst)  

                    continue 
