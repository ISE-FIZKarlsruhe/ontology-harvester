import sys
import time
import pandas as pd
from datetime import datetime

#query
import rdflib#from rdflib import Graph#, Literal, URIRef, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib.plugins.sparql.update
#import owlrl.RDFSClosure

sys.path.insert(1, './lib')     #add local library path
import template_maker as tm

tm.hide_labels=True
tsv_prefer=True  #replaces commas to tabs, semicolons to commas also

df = pd.read_csv("Ontologies_MSE.csv", encoding='unicode_escape', keep_default_na=False)

outname = "template.csv"
if (tsv_prefer==True):
       outname="template.tsv"


#url,title,creator,gitlink,filelink,descr,license,contact,documentation,proj,vers,module,branch,otype,extens

titles=[]
uris=[]
vers=[]
repolinks=[]
filelinks=[]
extens=[]
variants=[]
descriptions=[]
cpoints=[]
creators=[]
doclinks=[]
licenses=[]
acronyms=[]
short_desc=[]

idpref="http://example.org/"
idsuf=-1 #changes with new onto
idpostf=0 #changes with each possible duplic. entity within onto

maxlines = 2

for x in df['title'][:]:
        titles.append(x)
for x in df['Link (URL/PID)'][:]:
        uris.append(x)
for x in df['Repository address'][:]:
        repolinks.append(x)
for x in df['Link inside repository'][:]:
        filelinks.append(x)
for x in df[' version'][:]:
        vers.append(x)
for x in df[' type'][:]:
        variants.append(x)
for x in df['extension'][:]:
        extens.append(x)
for x in df[' description'][:]:
        descriptions.append(x)
for x in df['contact'][:]:
        cpoints.append(x)
for x in df['creator'][:]:
        creators.append(x)
for x in df['documentation link'][:]:
        doclinks.append(x)
for x in df['License'][:]:
        licenses.append(x)
for x in df['Acronym'][:]:
        acronyms.append(x)
for x in df['Short description'][:]:
        short_desc.append(x)


#sort by titles
#titles,uris,repolinks,filelinks,vers,variants,extens,descriptions,cpoints,creators,doclinks,licenses,acronyms,short_desc = zip(*sorted(zip(titles,uris,repolinks,filelinks,vers,variants,extens,descriptions,cpoints,creators,doclinks,licenses,acronyms,short_desc)))

titles = list(titles)
uris = list(uris)
repolinks = list(repolinks)
filelinks = list(filelinks)
vers = list(vers)
variants = list(variants)
extens = list(extens)
descriptions = list(descriptions)
cpoints = list(cpoints)
creators = list(creators)
doclinks = list(doclinks)
licenses = list(licenses)
acronyms = list(acronyms)
short_desc = list(short_desc)

odk_lines=[]
odk_lines.append(tm.header1)
odk_lines.append(tm.header2)
odk_lines.append(tm.header3)
odk_lines.append(tm.header4)

def_version="main"
def_variant = "release"

curr_repo=""
curr_title=""
curr_vers=""

id_titles=[]  #remember ids of titles
unique_titles=[] #not to return to the same ontology
unique_viris=[] #uniqe vers. iris
skip_title=False
titles_finished=[] #if 0, then in process, 1=finished
unique_uris=[]
unique_vers=[]
unique_vars=[]  #for version!
unique_exts=[]  #for version + variant!

print(str(len(titles)) + " titles total")

for i in range(len(titles)):
  titles[i] = titles[i].replace(",",";").replace("\n","; ")
  short_desc[i] = short_desc[i].replace(",",";").replace("\n","; ")
  creators[i] =  creators[i].replace("<","(").replace(">",")").replace("[","(").replace("]",")").replace("{","(").replace("}",")")
  cpoints[i] =  cpoints[i].replace("<","(").replace(">",")").replace("[","(").replace("]",")").replace("{","(").replace("}",")")
  #print("i: "+str(i))
  if (titles[i]==''):
           continue
    #if ((curr_title==titles[i]) | (curr_repo==repolinks[i])):      #within the same title = ontology class  

    ############
    #manual csv import, tailored for a limited number of columns: license, acronym, short_description
    ###########
  if (repolinks[i]==""):
    #print(titles[i])
    curr_title = titles[i]      
    if (titles[i] not in unique_titles):    
        [onto_line,onto_id] = tm.get_ontology_line(curr_title,licenses[i],acronyms[i])
        odk_lines.append(onto_line)   #add onto line to odk
        odk_lines.append(tm.get_ontology_title_namespace_descript_lines(curr_title,titles[i],"",short_desc[i],onto_id)[0])

        repolinks[i] = uris[i]
        curr_repo = repolinks[i]  
        if (repolinks[i]!=""):
                if (repolinks[i] not in tm.used_repos):
                                [repo_line,repo_id] = tm.get_repository_line(onto_id,curr_title+" repository", curr_repo,"")
                                odk_lines.append(repo_line)  #currently only main version
                                tm.used_repos.append(repolinks[i])
                                tm.used_repos_id.append(repo_id)
                                #print("new repo for " + curr_title, "repo=" + repo_line)
                else:
                        repo_id = tm.used_repos_id[tm.used_repos.index(repolinks[i])]
                        tm.get_repository_line(onto_id,curr_title+" repository", curr_repo,repo_id)
                        #print("reuse repo for " + curr_title)
    else:
            i = unique_titles.index(titles[i])
            id_reuse = id_titles[i]
            [onto_line,onto_id] = tm.get_ontology_line(curr_title,licenses[i],acronyms[i],id_reuse)
            odk_lines.append(onto_line)   #add onto line to odk
            print("reuse  title for " + curr_title)
##############
    #main: harvester case
################
  else:
    #print("onto+repo: " + curr_title)
    line_vers = uris[i]
    if (line_vers==curr_vers):      
      i+=0                                                      
    else: #entering new repository
        #if (titles[i] not in unique_titles):             
        if (line_vers not in unique_viris):
                curr_vers = line_vers
                unique_viris.append(line_vers)
                skip_title=False
        else:
                skip_title=True
                #print("skipping "+titles[i])
                print("skipping "+line_vers)
                continue

        if (titles[i] not in unique_titles):             
                unique_titles.append(titles[i])
                skip_title=False
        else:
                skip_title=True
                #print("skipping "+titles[i])
                print("skipping title "+titles[i])
                continue
        
        onto_id=""
        vers_id=""
        variant_id=""
        serializ_id=""
        repo_id=""
        downl_id=""     
        ext_id=""
        contact_id=""
        creatorS_id=""
        contact_role_id=""
        idsuf+=1
        curr_repo = repolinks[i]       
        curr_title = titles[i]
        [onto_line,onto_id] = tm.get_ontology_line(curr_title,licenses[i],acronyms[i])
        odk_lines.append(onto_line)   #add onto line to odk
        id_titles.append(onto_id)

        if (repolinks[i] not in tm.used_repos):
                [repo_line,repo_id] = tm.get_repository_line(onto_id,curr_title+" repository", curr_repo,"")
                odk_lines.append(repo_line)  #currently only main version
                tm.used_repos.append(repolinks[i])
                tm.used_repos_id.append(repo_id)
        else:
               repo_id = tm.used_repos_id[tm.used_repos.index(repolinks[i])]
               tm.get_repository_line(onto_id,curr_title+" repository", curr_repo,repo_id)
               

        unique_uris=[]  
        unique_vers=[]
        unique_vars=[]
        unique_exts=[]

        odk_lines.append(tm.get_ontology_title_namespace_descript_lines(curr_title,titles[i],uris[i],descriptions[i],onto_id)[0])
        #doc
        if ((doclinks[i]!="") & (doclinks[i]!="no info")& (doclinks[i]!="no info ")):
                #print("doclinks="+doclinks[i])
                odk_lines.append(tm.get_documentation_line(curr_title,onto_id,doclinks[i])[0])

    #versions
    if ((variants[i]!="base") & (variants[i]!="reasoned") & (variants[i]!="inferred")):
            variants[i]=""

    var_title= variants[i]
    vers_title = vers[i] #def_version


  #      [var_line,variant_id] = tm.get_ontology_variant_line(curr_title+" v. "+def_version + " " +variants[i],vers_id,onto_id,variants[i])
 #       odk_lines.append(var_line)  #add variant
    
    #extensions
    if ((vers_title+"_"+var_title+"_"+extens[i]) not in unique_exts):    
        unique_exts.append(vers_title+"_"+var_title+"_"+extens[i])

        if ((vers_title+"_"+var_title) not in unique_vars):
                unique_vars.append((vers_title+"_"+var_title))
        else:
                var_title=""

        if (vers_title not in unique_vers):
                unique_vers.append(vers_title)
        else:
                vers_title=""

        odk_lines.append(tm.get_ontology_version_variant_extension_line(titles[i],repo_id,onto_id,vers_title,var_title, filelinks[i],extens[i]))
        #[ext_line,ext_id]=tm.get_ontology_extension_line(curr_title+" v. "+def_version + " " +variants[i] +"."+extens[i],repo_id,onto_id,vers_id,downl_id)
        #print("addline " + vers_title+"_"+var_title+"_"+extens[i])
        #odk_lines.append(ext_line)
        #odk_lines.append(downl_line)
        #odk_lines.append(tm.get_format_extension_lines(extens[i],ext_id)[0])
        idpostf+=1

    
           
    #contact point
    if ((cpoints[i]!="") & (cpoints[i]!="no info") & ( (cpoints[i]!="no info "))):
           if (contact_id==""):
                #print("cp="+cpoints[i])
                [contact_line,contact_id,contact_role_id]=tm.get_contact_role_process_line(curr_title,onto_id,cpoints[i])                
                odk_lines.append(contact_line)
                if (contact_id!=""): #we have info about this contact already
                        odk_lines.append(tm.get_contact_details_lines(curr_title,contact_id,contact_role_id,cpoints[i])[0])

                idsuf+=1


    #creator
    if (creators[i]!=""):
           #multiline handle
        if (creatorS_id==""):
                creatorS_id = creators[i]
                creation_proc_id=""
                for creator in (creators[i].split(";")):
                        if (len(creator.replace(" ",""))<2):
                                continue
                        [creator_line,creator_id,creation_proc_id]=tm.get_creator_role_process_line(curr_title,onto_id,creator,creation_proc_id)
                        odk_lines.append(creator_line)
                        if (creator_id!=""): #we have info about this creator already
                                odk_lines.append(tm.get_creator_details_lines(curr_title,creator_id,creator)[0])

                        idsuf+=1
                        
           

f = open(outname,'a', encoding="utf-8")
ind=0
for line in odk_lines:
      #print(line)
      # print("\n")
      if (len(line.split(","))<tm.nprops/2): #skip empty lines
              continue
      line+="\n"
      line=line.replace("\n\n","\n")
      if (ind>=4):
                newline = tm.append_annotations(line)
      else:
                newline = line

      if (tsv_prefer==True):
                newline = newline.replace(",","\t").replace(";",",")
                f.write(newline)
      else:
                f.write(newline)

      ind+=1

f.close()

