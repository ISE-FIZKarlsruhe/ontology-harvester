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

# Required positional argument - git user name
parser.add_argument('folder_arg', type=str,
                    help='A required string argument - folder with clones repositories')
# Optional argument
parser.add_argument('--output_filename', type=str,
                    help='Optional: name of the output csv file')


args = parser.parse_args()

folder=""

try:
    print("Folder to scan: " + args.folder_arg)
    folder = args.folder_arg
except:
    print("Error:provide a folder name with cloned repositories!")
    exit()

try:
    outname = args.output_filename
except:
    pass


if (outname==None):
        outname="Ontologies.csv"

print("Output file name: " + outname)

if (not os.path.isfile(outname)):
    print("creating output file")
    csv_io.create_csv(outname)
else:
     print("appending to the output file")    

def get_ai_model():
    from openai import AzureOpenAI
    ai_client = AzureOpenAI(
      azure_endpoint = "https://my-east.openai.azure.com/", 
      api_key="YOUR_API_KEY",   
      api_version="2023-05-15"
    )

    #modelName="Microsoft.CognitiveServicesOpenAI-20240111194907"
    #deployment_name='gpt-35'
    return ai_client

try:
    my_ai = get_ai_model()
except:
     my_ai=[]
     pass

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
                            
                            #LINK TO THE FILE (default branch)
                            x=fi[len(folder):].replace("\\","/")
                            inds = [x.start() for x in re.finditer('/',x)] #indexe of "/"
                            ind=inds[2]                     
                            branch = Repository(folder + x[:ind]).head.shorthand
                            print(x)
                            if ("more_branches" in fi):
                                s_ind = inds[3]
                                e_ind = inds[4]
                                n_ind = s_ind + len("more_branches/")
                                branch = x[s_ind+1:n_ind]
                                print("branch="+branch)
                                gitlink = x[:ind] + "/tree/"+branch + x[e_ind:]
                            else:
                                 gitlink = x[:ind] + "/tree/" + branch + x[ind:]

                            print(gitlink)

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
                            #gitlink = prefix + subfold

                            #extract information from ontology file
                            oinfo_fill = ontoinfo.extract_info(fi,gitlink)   
                            print(oinfo_fill)
                            #add to the csv file
                            if (oinfo_fill!=[]):
                                    csv_io.add_to_csv(outname,oinfo_fill[0],oinfo_fill[1],oinfo_fill[2],oinfo_fill[3],oinfo_fill[4],lic_info,read_info[1],read_info[0],read_info[2],inidate,lastdate,oinfo_fill[5],oinfo_fill[6],branch,onto_type,ext)
