import os
import glob
import re
import time
import pandas as pd
from datetime import datetime

#query
import rdflib#from rdflib import Graph#, Literal, URIRef, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib.plugins.sparql.update
#import owlrl.RDFSClosure


hide_labels=True
fake_id=False
tsv_prefer=True  #replaces commas to tabs, semicolons to commas also

creator_name="https://github.com/kgubaev/Github-Ontology-Harvester"
creator_version = "version 0.2"
creator_date = datetime.today().strftime('%Y-%m-%d')

namespace = "https://purls.helmholtz-metadaten.de/msekg/"
last_timestamp = int(time.time() * 1000)
counter=1

def get_new_id():
        global counter
        global last_timestamp
        #timestamp = time.time()
        #if (timestamp==last_timestamp):
        #      counter+=1
        #else:
        #      counter=1
        #      last_timestamp=timestamp
        #last_timestamp=timestamp
        result = namespace + str(last_timestamp) + str(counter)
        counter+=1
        return result

#print(last_timestamp)
#exit(0)

def commastring(n):
        result=""
        for i in range(n):
              result+=","
        return result

nprops=12 #number of object/data properties columns in csv template
#nannot=2 annotation properties
 
#os.system("ls")
df = pd.read_csv("example_test_1.csv", encoding='unicode_escape', keep_default_na=False)

outname = "template.csv"
if (tsv_prefer==True):
       outname="template.tsv"

header1="comment,id,class (the type of the instance),label,has file format,is continuant part of,is about,download URL,nfdicore:has_url,nfdicore:has_value,nfdicore:contact_point_of,nfdicore:creator_of,bearer_of,has_realization,participates_in,concretizes, dcterms:creator, dcterms:created"
header2=",ID,TYPE,LABEL,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000132,I http://purl.obolibrary.org/obo/BFO_0000176,I http://purl.obolibrary.org/obo/IAO_0000136 SPLIT=|,I http://www.w3.org/ns/dcat#downloadURL,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001008,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001007,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000113,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001028,I http://purl.obolibrary.org/obo/BFO_0000196,I http://purl.obolibrary.org/obo/BFO_0000054,I http://purl.obolibrary.org/obo/BFO_0000056,I http://purl.obolibrary.org/obo/BFO_0000059,A http://purl.org/dc/terms/creator,A http://purl.org/dc/terms/created"
#header1="comment,id,class (the type of the instance),label,has part,is part of,is about,download URL,description"
#header2=",ID,TYPE,LABEL,I http://purl.obolibrary.org/obo/BFO_0000051,I http://purl.obolibrary.org/obo/BFO_0000050,I http://purl.obolibrary.org/obo/IAO_0000136 SPLIT=|,I http://www.w3.org/ns/dcat#downloadURL,A http://purl.org/dc/terms/description SPLIT=|"
header3="has value property,https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001007,data property,has_value" + commastring(nprops+2)
header4="has url property,https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001008,data property,has_url"+ commastring(nprops+2)


def keep_label(label):
        if (hide_labels):
                return ""
        else:
                return label
        
def append_annotations(line):
        annot_line = creator_name + " " + creator_version +", " + creator_date + "\n"
        newline = line.replace("\n",annot_line)
        return newline

def get_ontology_line(label): #comment=label
       if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_ontology_"+str(idpostf)
       else:
                id = get_new_id()
       line=""
       line+=label+"," #comment
       line+=id+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000023," #type
       line+=keep_label(label)+","
       line+= commastring(nprops) #empty columns
       return [line,id]

def get_ontology_version_line(label,is_about_val): #comment=label, is_about ontology (line passed)
       #is_about_val = is_about.split(",")[1] #get id
       if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_version_"+str(idpostf)
       else:
                id = get_new_id()
       line=""
       line+=label+"," #comment
       line+=id+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000026," #type
       line+=keep_label(label)+","
       line+=",," #empty columns
       line+=is_about_val+","
       line+=commastring(nprops-3)
       return [line,id]

def get_ontology_variant_line(label,is_partof_val,is_about_val,variant_name): #comment=label, is_about ontology, is part of version
       #is_about_val = is_about.split(",")[1] #get id
       #is_partof_val = is_partof.split(",")[1] #get id
       if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_variant_"+str(idpostf)
       else:
                id = get_new_id()
       line=""
       line+=label+"," #comment
       line+=id+","

       if (variant_name=="base"):
        line+="http://purl.obolibrary.org/obo/IAO_8000001," #type
       elif ((variant_name=="reasoned") | (variant_name=="inferred")):
        line+="http://purl.obolibrary.org/obo/IAO_8000013,"
       else: #main release
        line+="http://purl.obolibrary.org/obo/IAO_8000003,"

       line+=keep_label(label)+","
       line+="," #empty columns
       line+=is_partof_val+","  
       line+=is_about_val+","
       line+=commastring(nprops-3)
       return [line,id]

def get_ontology_version_variant_extension_line(label,is_partof_val,is_about_onto_val,version_name,variant_name, download_url_val,sub_format): #label = onto title, #par of repository
       if (fake_id==True):
                id_vers=idpref+"_"+str(idsuf)+"_extens_"+str(idpostf)
                id_var=idpref+"_"+str(idsuf)+"_extens_"+str(idpostf)
                id_versnum=idpref+"_"+str(idsuf)+"_extens_"+str(idpostf)
                id_file=idpref+"_"+str(idsuf)+"_extens_"+str(idpostf)
                id_ext=idpref+"_"+str(idsuf)+"_extens_"+str(idpostf)
                id_downlink=idpref+"_"+str(idsuf)+"_extens_"+str(idpostf)
       else:
                id_vers=get_new_id()
                id_var=get_new_id() 
                id_versnum=get_new_id()
                id_file=get_new_id()
                id_ext=get_new_id()
                id_downlink=get_new_id()        
       #variant
       line=""
       if ((variant_name=="base") | (variant_name=="reasoned")| (variant_name=="inferred")):
                line+=""
                line+=label+" "+variant_name + " variant," #comment
                line+=id_var+","

                if (variant_name=="base"):
                        line+="http://purl.obolibrary.org/obo/IAO_8000001," #type
                elif ((variant_name=="reasoned") | (variant_name=="inferred")):
                        line+="http://purl.obolibrary.org/obo/IAO_8000013,"
                # else: #main release
                #  line+="http://purl.obolibrary.org/obo/IAO_8000003,"

                line+=keep_label(label+" "+variant_name + " variant")+","
                line+="," #empty columns
                line+=is_about_onto_val+","  #part of onto
                line+=","
                line+=commastring(nprops-3) + "\n"
       else:
               id_var=""
        #version
       if (version_name!=""):
                line+=""
                line+=label+" version " + version_name+ " ,"
                line+=id_vers+","
                line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000026," #type
                line+=keep_label(label+" version " + version_name)+ " ,"
                line+="," + is_about_onto_val + "," #part of onto
                line+=","
                line+=commastring(nprops-3) + "\n"
                #vers number
                IRI = (version_name[:4]=="http")  #is IRI or not
                #print(version_name[:4])
                if (not IRI):
                        line+=label+" version number = " + version_name+ " ,"
                        line+=id_versnum+","
                        line+="http://purl.obolibrary.org/obo/IAO_0000129," #version number
                        line+=keep_label(label+" version number = " + version_name)+ " ,"
                        line+=",," #empty columns
                        line+=id_vers+",,,"
                        line+=version_name
                        line+=commastring(nprops-5)+ "\n"
                else:
                        line+=label+" version IRI = " + version_name+ " ,"
                        line+=id_versnum+","
                        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001053," #version IRI
                        line+=keep_label(label+" version IRI = " + version_name)+ " ,"
                        line+=",," #empty columns
                        line+=id_vers+",,"
                        line+=version_name+"^^xsd::anyURI,"
                        line+=commastring(nprops-5)+ "\n"
    
        # file
       line+=""
       line+=label+" file," #comment
       line+=id_file+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000027," #type
       line+=keep_label(label+" file")+","
       line+=id_ext + "," #format
       line+=is_partof_val+","  
       line+=is_about_onto_val
       if (version_name!=""):
               line+=" | "+id_vers
       if (id_var!=""):
               line+=" | "+id_var
       line+=","+id_downlink+"," 
       line+=commastring(nprops-6+2) + "\n"
      # return [line,id]                 #return 

        #link
       if (True):
        label=label + " file download link"
        line+=""
        line+=label+"," #comment
        line+=id_downlink+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001034," #type
        line+=keep_label(label)+","
        line+=",," #empty columns
        line+=",,"
        line+=download_url_val.replace(" ","%20")+"^^xsd:anyURI"
        line+=commastring(nprops-7+3) + "\n"

        #format
        #subclass line
        sub_formline=""
        if (sub_format=="ttl"):
                sub_formline+="http://edamontology.org/format_3255" #type ttl
        elif (sub_format=="rdf"):
                sub_formline+="http://edamontology.org/format_3261" 
        elif (sub_format=="owl"):
                sub_formline+="http://edamontology.org/format_2197" 
        elif (sub_format=="n3"):
                sub_formline+="http://edamontology.org/format_3257" 
        elif (sub_format=="nt"):
                sub_formline+="http://edamontology.org/format_3256" 
        elif (sub_format=="nq"):
                sub_formline+="http://edamontology.org/format_3956" 
        else:
                sub_formline+="http://edamontology.org/format_2376" #RDF in wide sense               

        if (sub_formline!=""):
                sub_label=sub_format+"_format"
                line+=sub_label+"," #comment
                line+=id_ext+","
                line+=sub_formline+","
                line+=keep_label(sub_label)+","
                line+=",," #empty columns
                line+=id_file+","
                line+=commastring(nprops-6+3)


        return line
       
def get_repository_line(label,repolink): #comment=label, is_about ontology (line passed)
       if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_repolink_"+str(idpostf)
       else:
                id = get_new_id()
       line=""
       line+=label+"," #comment
       line+=id+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000030," #type
       line+=keep_label(label)+","
       line+=",," #empty columns
       line+=",,"
       line+=repolink+"^^xsd:anyURI"
       line+=commastring(nprops-4)
       return [line,id]

def get_documentation_line(filename,is_about,has_url): #comment=label, is_about ontology (line passed)
        label=filename + " documentation link"
        if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_downlink_"+str(idpostf)
        else:
                id = get_new_id()       
        line=""
        line+=label+"," #comment
        line+=id+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000022," #type
        line+=keep_label(label)+","
        line+=",," #empty columns
        line+=is_about + ",,"   
        line+=has_url+"^^xsd:anyURI"
        line+=commastring(nprops-4)
        return [line,id]

def get_ontology_title_namespace_descript_lines(label,title_val,namespace_val,descript_val,is_about_val): #comment=label, is_about ontology (line passed)
       #is_about_val = is_about.split(",")[1] #get id
       #title
       if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_title_"+str(idpostf)
       else:
                id = get_new_id()
       line=""
       line+=label+"_title," #comment
       line+=id+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001019," #type
       line+=keep_label(label+"_title")+","
       line+=",," #empty columns
       line+=is_about_val+",,,"
       line+=title_val+","
       line+=commastring(nprops-6) + "\n"

       #URI
       if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_uri_"+str(idpostf)
       else:
                id = get_new_id()
       line+=label+"_namespace," #comment
       line+=id+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001022," #type
       line+=keep_label(label+"_namespace")+","
       line+=",," #empty columns
       line+=is_about_val+",,"
       line+=namespace_val+"^^xsd:anyURI"
       line+=commastring(nprops-8+4)

       #description
       if (descript_val=="missing descr."):
               descript_val=""

       if (descript_val!=""):
                if (fake_id==True):
                                id=idpref+"_"+str(idsuf)+"_description_"+str(idpostf)
                else:
                                id = get_new_id()               
                line+= "\n"+label+"_description," #comment
                line+=id+","
                line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001018," #type
                line+=keep_label(label+"_description")+","
                line+=",," #empty columns
                line+=is_about_val+",,,"           
                line+=descript_val+","
                line+=commastring(nprops-6)

       return [line,id]

def get_contact_role_process_line(filename,contact_of,information):  #contact of ontology, role concretizes ontology
        if (fake_id==True):
                id_contact=idpref+"_"+str(idsuf)+"_contact_"+str(idpostf)
                id_process=idpref+"_"+str(idsuf)+"_contact-process_"+str(idpostf)
                id_role=idpref+"_"+str(idsuf)+"_contact-role_"+str(idpostf)
        else:
                id_contact = get_new_id()  
                id_process = get_new_id()
                id_role = get_new_id()

        fill_id_person = id_contact
        fill_id_role = id_role
        [firstname,familyname,orcid,email] = parse_personal_info(information)

        was_ind = check_intersecting_person_info(information)
        #print("search person " + str(was_ind))
        if (was_ind==-1):
                #MSE KG search
                #have different roles instances if csv line is not coinciding
               KG_person_id = check_MSE_person_existence(firstname,familyname,email,orcid)
               if (KG_person_id!=""):
                       fill_id_person=KG_person_id
                       id_contact=""
               used_persons_id.append(fill_id_person) 
               #used_contact_roles_id.append(id_role)
               used_persons.append(information)
        else:
               fill_id_person = used_persons_id[was_ind]
               #fill_id_role = used_contact_roles_id[was_ind]
               id_contact=""
               #used_contact_roles_id.append(fill_id_role)
               used_persons.append(information)
               used_persons_id.append(fill_id_person)

        #person
        label=filename + " contact person"
        line=""
        line+=label+"," #comment
        line+=fill_id_person+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000004," #type
        line+=keep_label(label)+","
        line+=commastring(6) #empty columns
        line+=contact_of+",,"
        line+=fill_id_role+",,"
        line+=id_process+",,"+ "\n" 
        #process
        label=filename + " contact process"
        line+=label+"," #comment
        line+=id_process+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000111," #type
        line+=keep_label(label)+","
        line+=commastring(12) + "\n" #empty columns
         #role
        label=filename + " contact role"
        line+=label+"," #comment
        line+=fill_id_role+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000114," #type
        line+=keep_label(label)+","
        line+=commastring(9) #empty columns
        line+=id_process+",,"
        line+=contact_of+","#concretizes ontology

        return [line,id_contact,fill_id_role]

#query persons
def check_MSE_person_existence(first_name,family_name,email,orcid):
        sparql = SPARQLWrapper(
        "https://sparql-nfdi-matwerk-02.web.vulcanus.otc.coscine.dev/"
        )
        sparql.setReturnFormat(JSON)

        log=True
        found_label=""
        found_id=""

        #print("name="+first_name+family_name)
        #print("mail="+email)
        #print("orcid="+orcid)

        query_start="""

        PREFIX nfdicore: <https://nfdi.fiz-karlsruhe.de/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX mwo: <http://purls.helmholtz-metadaten.de/mwo/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?person ?label 
        WHERE { """

        #orcid query
        if (orcid!=""):
                sparql.setQuery(query_start + """
                                
                ?person mwo:hasORCID ?orcid FILTER REGEX (?orcid,"{orcidid}","i") 
                ?person rdfs:label ?label
                """.format(orcidid=orcid)

                + """
                }
                """
                )

                try:
                        ret = sparql.queryAndConvert()
                        if len(ret["results"]["bindings"])>1:
                                raise Exception("More than one person found with ORCID "+orcid)
                        for r in ret["results"]["bindings"]:
                                found_id = r["person"]["value"]
                                found_label = r["label"]["value"]
                except Exception as e:
                        print(e)

                if (found_id!=""):
                        if (log==True):
                                print("found person " + found_label + " in MSE KG")
                        return found_id

        #email query
        if (email!=""):
                sparql.setQuery(query_start + """
                        
                ?person mwo:emailAddress ?email FILTER REGEX (?email,"{email}","i") 
                ?person rdfs:label ?label
                """.format(email=email)

                + """
                }
                """
                )
                try:
                        ret = sparql.queryAndConvert()
                        if len(ret["results"]["bindings"])>1:
                                raise Exception("More than one person found with email "+ email)
                        for r in ret["results"]["bindings"]:
                                found_id = r["person"]["value"]
                                found_label = r["label"]["value"]
                except Exception as e:
                        print(e)

                if (found_id!=""):
                        if (log==True):
                                print("found person " + found_label + " in MSE KG")
                        return found_id
                
        #name & surname query
        if ((first_name!="") | (family_name!="")):
                label=first_name+" "+family_name

                sparql.setQuery(query_start + """             
                ?person rdfs:label ?label FILTER REGEX (?label,"{label}","i") 
                """.format(label=label)

                + """
                }
                """
                )
                try:
                        ret = sparql.queryAndConvert()
                        if len(ret["results"]["bindings"])>1:
                                raise Exception("More than one person found with name "+ label)
                        for r in ret["results"]["bindings"]:
                                found_id = r["person"]["value"]
                                found_label = r["label"]["value"]
                except Exception as e:
                        print(e)

                if (found_id!=""):
                        if (log==True):
                                print("found person " + found_label + " in MSE KG")
                        return found_id

        return found_id

def check_intersecting_person_info(information):
        #returns index of found person
        [firstname,familyname,orcid,email] = parse_personal_info(information)          
        for i in range(len(used_persons)):
                [i_firstname,i_familyname,i_orcid,i_email] = parse_personal_info(used_persons[i])          
                if ((i_firstname+i_familyname==firstname+familyname)&(firstname+familyname!="")):
                        return i
                if ((i_orcid==orcid) & (orcid!="")):
                        return i
                if ((i_email==email) & (email!="")):
                        return i                
                
        return -1

def get_creator_role_process_line(filename,creator_of,information,process_id):  #creator of ontology
        if (fake_id==True):
                id_creator=idpref+"_"+str(idsuf)+"_creator_"+str(idpostf)
                id_process=idpref+"_"+str(idsuf)+"_creative-process_"+str(idpostf)
                id_role=idpref+"_"+str(idsuf)+"_creator-role_"+str(idpostf)
        else:
                id_creator = get_new_id()  
                id_process = get_new_id()
                if (process_id!=""):
                        id_process = process_id
                id_role = get_new_id()

        fill_id_person = id_creator
        fill_id_role = id_role
        [firstname,familyname,orcid,email] = parse_personal_info(information)

        was_ind = check_intersecting_person_info(information)
       # print("search person " + str(information))
        if (was_ind==-1):
                #MSE KG search
                #have different roles instances if csv line is not coinciding
               KG_person_id = check_MSE_person_existence(firstname,familyname,email,orcid)
               #print("KG_id="+KG_person_id)
               if (KG_person_id!=""):
                       fill_id_person=KG_person_id
                       id_creator=KG_person_id
               used_persons_id.append(fill_id_person) 
               #used_creator_roles_id.append(id_role)
               used_persons.append(information)
        else:
               fill_id_person = used_persons_id[was_ind]
              # fill_id_role = used_creator_roles_id[was_ind]
               id_creator=""
             #  used_creator_roles_id.append(fill_id_role)
               used_persons.append(information)
               used_persons_id.append(fill_id_person)

        #person
        label=filename + " creator person"
        line=""
        line+=label+"," #comment
        line+=fill_id_person+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000004," #type
        line+=keep_label(label)+","
        line+=commastring(7) #empty columns
        line+=creator_of+","
        line+=fill_id_role+",,"
        line+=id_process+",,\n"
        #process
        label=filename + " creation process"
        line+=label+"," #comment
        line+=id_process+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001025," #type
        line+=keep_label(label)+","
        line+=commastring(12) + "\n" #empty columns
         #role
        label=filename + " creation role"
        line+=label+"," #comment
        line+=fill_id_role+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001026," #type
        line+=keep_label(label)+","
        line+=commastring(9) #empty columns
        line+=id_process+",,"
        line+=creator_of+"," #concretizes ontology

        return [line,id_creator,id_process]

def parse_personal_info(info):
       if (info[0]==" "):
                info=info[1:]
       if (info[-1]==" "):
               info = info[:-1]
       fullname=""
       firstname=""
       familyname=""
       orcid=""
       email=""
       if type(info) is list:
        info=info[0]
       info=info.replace("\n","")
       if (info[-1]==" "):
               info=info[:-1]
        #agents = info.split
       sublines = info.split(" ")
       if (len(sublines)==1): #orcid or mail only
                if ("orcid" in info):
                        orcid=info
                elif ("@" in info):
                        email=info
       elif (len(sublines)>=2):
                if ("(" in info): #parenthesis info
                     j=0
                     while (sublines[j][0]!="("):
                            fullname+=sublines[j]+" "
                            j+=1
                     if ("orcid" in sublines[j]):
                        orcid=sublines[j][1:-1] # works for single info
                     elif ("@" in sublines[j]):
                        email=sublines[j][1:-1]                     
                else:
                       fullname=info

       if (fullname!=""):
                namepars=fullname.split(" ")
                firstname=namepars[0]
                familyname=fullname[len(firstname)+1:]

       #print(sublines, fullname)
       
       return [firstname,familyname,orcid,email]


def get_creator_details_lines(ontoname,is_about_val,information): #comment=label, is_about creator(s), information=content of csv cell
        [firstname,familyname,orcid,email] = parse_personal_info(information)
        #print(information)
        line="" 
        id=""
        if (firstname!=""):
                label=ontoname + " creator first name"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_creator-first-name_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0020016," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_val+",,,"
                line+=firstname
                line+=commastring(nprops-5)
        if (familyname!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " creator family name"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_creator-family-name_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0020017," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_val+",,,"
                line+=familyname
                line+=commastring(nprops-5)
        if (email!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " creator email"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_creator-email_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0000429," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_val+",,,"
                line+=email
                line+=commastring(nprops-5)
        if (orcid!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " creator orcid"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_creator-orcid_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0000708," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_val+",,,"
                line+=orcid
                line+=commastring(nprops-5)
        return [line,id]

def get_contact_details_lines(ontoname,is_about_contact_person,is_about_contact_role,information): #comment=label, is_about contact, information=content of csv cell
        [firstname,familyname,orcid,email] = parse_personal_info(information)
        line=""
        id=""
        if (firstname!=""):
                label=ontoname + " contact first name"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_contact_point-first-name_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0020016," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_contact_person+",,,"
                line+=firstname
                line+=commastring(nprops-5)
        if (familyname!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " contact family name"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_contact_point_family-name_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0020017," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_contact_person+",,,"
                line+=familyname
                line+=commastring(nprops-5)
        if (email!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " contact email"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_contact_point-email_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0000429," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_contact_role+",,,"
                line+=email
                line+=commastring(nprops-5)
        if (orcid!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " contact orcid"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_contact_point_orcid_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0000708," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_contact_person+",,,"
                line+=orcid
                line+=commastring(nprops-5)
        return [line,id]

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

idpref="http://example.org/"
idsuf=-1 #changes with new onto
idpostf=0 #changes with each possible duplic. entity within onto

maxlines = 29

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

odk_lines=[]
odk_lines.append(header1)
odk_lines.append(header2)
odk_lines.append(header3)
odk_lines.append(header4)

def_version="main"
def_variant = "release"

curr_repo=""
curr_title=""
curr_vers=""

unique_titles=[] #not to return to the same ontology
unique_viris=[] #uniqe vers. iris
skip_title=False
titles_finished=[] #if 0, then in process, 1=finished
unique_uris=[]
unique_vers=[]
unique_vars=[]  #for version!
unique_exts=[]  #for version + variant!

#to avoid dupl.
used_repos=[]
used_repos_id=[]
used_persons=[]
used_persons_id=[]
#onto_id="",vers_id="",variant_id="",serializ_id="",repo_id="",downl_id="",ext_id=""

for i in range(len(titles)):
    if (titles[i]==''):
           continue
    #if ((curr_title==titles[i]) | (curr_repo==repolinks[i])):      #within the same title = ontology class  

    line_vers = uris[i]
    if (line_vers==curr_vers):      
      i+=0                                                      
    else: #entering new repository
        #if (titles[i] not in unique_titles):             
        if (line_vers not in unique_viris):
                #unique_titles.append(titles[i])
                curr_vers = line_vers
                unique_viris.append(line_vers)
                skip_title=False
        else:
                skip_title=True
                #print("skipping "+titles[i])
                print("skipping "+line_vers)
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
        [onto_line,onto_id] = get_ontology_line(curr_title)
        odk_lines.append(onto_line)   #add onto line to odk

        if (repolinks[i] not in used_repos):
                [repo_line,repo_id] = get_repository_line(curr_title+" repository", curr_repo)
                odk_lines.append(repo_line)  #currently only main version
                used_repos.append(repolinks[i])
                used_repos_id.append(repo_id)
        else:
               repo_id = used_repos_id[used_repos.index(repolinks[i])]

        #[vers_line,vers_id] = get_ontology_version_line(curr_title+" v. "+def_version,onto_id)
        #odk_lines.append(vers_line)  #currently only main version     
        unique_uris=[]  
        unique_vers=[]
        unique_vars=[]
        unique_exts=[]
        #odk_lines.append(get_version_number_line(titles[i],vers[i],vers_id)[0])  #currently only main version     
        #title-dedcript-prefix
        odk_lines.append(get_ontology_title_namespace_descript_lines(curr_title,titles[i],uris[i],descriptions[i],onto_id)[0])
        #doc
        if ((doclinks[i]!="") & (doclinks[i]!="no info")& (doclinks[i]!="no info ")):
                #print("doclinks="+doclinks[i])
                odk_lines.append(get_documentation_line(curr_title,onto_id,doclinks[i])[0])

#     if (uris[i] not in unique_uris):     #uri should be 1 for each version-format
#            unique_uris.append(uris[i]) 
#     #if (vers[i] not in unique_vers):
#     if (len(unique_vers)==0):
#            unique_vers.append(vers[i]) 
#            odk_lines.append(get_version_number_line(vers[i],vers_id))  #currently only main version          

    #variants
    #if (variants[i]==""):
    #       variants[i]=def_variant
       
    #versions
    if ((variants[i]!="base") & (variants[i]!="reasoned") & (variants[i]!="inferred")):
            variants[i]=""

    var_title= variants[i]
    vers_title = vers[i] #def_version


  #      [var_line,variant_id] = get_ontology_variant_line(curr_title+" v. "+def_version + " " +variants[i],vers_id,onto_id,variants[i])
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

        odk_lines.append(get_ontology_version_variant_extension_line(titles[i],repo_id,onto_id,vers_title,var_title, filelinks[i],extens[i]))
        #[ext_line,ext_id]=get_ontology_extension_line(curr_title+" v. "+def_version + " " +variants[i] +"."+extens[i],repo_id,onto_id,vers_id,downl_id)
        #print("addline " + vers_title+"_"+var_title+"_"+extens[i])
        #odk_lines.append(ext_line)
        #odk_lines.append(downl_line)
        #odk_lines.append(get_format_extension_lines(extens[i],ext_id)[0])
        idpostf+=1

    
           
    #contact point
    if ((cpoints[i]!="") & (cpoints[i]!="no info") & ( (cpoints[i]!="no info "))):
           if (contact_id==""):
                [contact_line,contact_id,contact_role_id]=get_contact_role_process_line(curr_title,onto_id,cpoints[i])                
                odk_lines.append(contact_line)
                if (contact_id!=""): #we have info about this contact already
                        odk_lines.append(get_contact_details_lines(curr_title,contact_id,contact_role_id,cpoints[i])[0])

                idsuf+=1


    #creator
    if (creators[i]!=""):
           #multiline handle
        if (creatorS_id==""):
                creatorS_id = creators[i]
                creation_proc_id=""
                for creator in (creators[i].split(";")):
                        [creator_line,creator_id,creation_proc_id]=get_creator_role_process_line(curr_title,onto_id,creator,creation_proc_id)
                        odk_lines.append(creator_line)
                        if (creator_id!=""): #we have info about this creator already
                                odk_lines.append(get_creator_details_lines(curr_title,creator_id,creator)[0])

                        idsuf+=1
                        
           

f = open(outname,'a', encoding="utf-8")
ind=0
for line in odk_lines:
      # print("\n")
      # print(line)
      if (ind>=4):
                newline = append_annotations(line+"\n")
      else:
                newline = line + "\n"

      if (tsv_prefer==True):
                newline = newline.replace(",","\t").replace(";",",")
                f.write(newline)
      else:
                f.write(newline)

      ind+=1

f.close()

