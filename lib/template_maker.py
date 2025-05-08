import time
from datetime import datetime

#query
import rdflib#from rdflib import Graph#, Literal, URIRef, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib.plugins.sparql.update
#import owlrl.RDFSClosure

fake_id=False
hide_labels=True


creator_name="https://github.com/kgubaev/Github-Ontology-Harvester/releases/tag/"
creator_version = "1.0"
creator_date = datetime.today().strftime('%Y-%m-%d')

namespace = "https://purls.helmholtz-metadaten.de/msekg/"
last_timestamp = int(time.time() * 1000)
counter=1

#to avoid duplicates
used_repos=[]
used_repos_id=[]
used_persons=[]
used_persons_id=[]

def get_new_id():
        global counter
        global last_timestamp
        #timestamp = time.time()            #timestamp is now determined at start of the script
        #if (timestamp==last_timestamp):
        #      counter+=1
        #else:
        #      counter=1
        #      last_timestamp=timestamp
        #last_timestamp=timestamp
        result = namespace + str(last_timestamp) + str(counter)
        counter+=1
        return result

def commastring(n):
        result=""
        for i in range(n):
              result+=","
        return result

nprops=14 #number of object/data properties columns in csv template

header1="comment,id,class (the type of the instance),label,has file format,is continuant part of,is about,download URL,nfdicore:has_url,nfdicore:has_value,nfdicore:contact_point_of,nfdicore:creator_of,bearer_of,has_realization,participates_in,concretizes,nfdicore:has_license,nfdicore:has_acronym,dcterms:creator, dcterms:created"
header2=",ID,TYPE,LABEL,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000132,I http://purl.obolibrary.org/obo/BFO_0000176,I http://purl.obolibrary.org/obo/IAO_0000136 SPLIT=|,I http://www.w3.org/ns/dcat#downloadURL,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001008,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001007,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000113,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001028,I http://purl.obolibrary.org/obo/BFO_0000196,I http://purl.obolibrary.org/obo/BFO_0000054,I http://purl.obolibrary.org/obo/BFO_0000056,I http://purl.obolibrary.org/obo/BFO_0000059,I https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000142,A https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0010015,A http://purl.org/dc/terms/creator,A http://purl.org/dc/terms/created"
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
        annot_line = creator_name + creator_version +", " + creator_date + "\n"
        newline = line.replace("\n",annot_line)
        return newline

def get_ontology_line(label,license="",acronym="",id_onto=""): #comment=label
        #license
       line=""
       idlic=""
       if (license!=""):
                idlic = get_new_id()
                line+=license+"," #comment
                line+=idlic+","
                line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000141," #type
                line+=keep_label(label + " license")+","
                line+=",," #empty columns
                line+=",,,"           
                line+=license+","
                line+=commastring(nprops-6)+"\n" #empty columns

       if (fake_id==True):
                id=idpref+"_"+str(idsuf)+"_ontology_"+str(idpostf)
       else:
                if (id_onto==""):
                        id = get_new_id()
                else:
                        id = id_onto
       line+=label+"," #comment
       line+=id+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000023," #type
       line+=keep_label(label)+","
       line+= commastring(nprops-2) #empty columns
       line+= idlic+","
       line+= acronym + ","
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
       
def get_repository_line(onto_id,label,repolink,repo_id): #comment=label, is_about ontology (line passed)
       if (repo_id==""):
                if (fake_id==True):
                                id=idpref+"_"+str(idsuf)+"_repolink_"+str(idpostf)
                else:
                                id = get_new_id()
       else:
               id = repo_id

       line=""
       line+=label+"," #comment
       line+=id+","
       line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000030," #type
       line+=keep_label(label)+","
       line+=",," #empty columns
       line+=onto_id+",,"
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
       if (namespace_val!=""):
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
                line+=commastring(nprops-8+4)+"\n"

       #description
       if (descript_val=="missing descr."):
               descript_val=""

       if (descript_val!=""):
                if (fake_id==True):
                                id=idpref+"_"+str(idsuf)+"_description_"+str(idpostf)
                else:
                                id = get_new_id()               
                line+= label+"_description," #comment
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
        line+=id_process+",,,,"+ "\n" 
        #process
        label=filename + " contact process"
        line+=label+"," #comment
        line+=id_process+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000111," #type
        line+=keep_label(label)+","
        line+=commastring(14) + "\n" #empty columns
         #role
        label=filename + " contact role"
        line+=label+"," #comment
        line+=fill_id_role+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0000114," #type
        line+=keep_label(label)+","
        line+=commastring(9) #empty columns
        line+=id_process+",,"
        line+=contact_of+",,,"#concretizes ontology

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
        [firstname,familyname,orcid,email,cri] = parse_personal_info(information)          
        for i in range(len(used_persons)):
                [i_firstname,i_familyname,i_orcid,i_email,i_cri] = parse_personal_info(used_persons[i])          
                if ((i_firstname+i_familyname==firstname+familyname)&(firstname+familyname!="")):
                        return i
                if ((i_orcid==orcid) & (orcid!="")):
                        return i 
                if ((i_email==email) & (email!="")):
                        return i     
                if ((i_cri==cri) & (cri!="")):
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
        [firstname,familyname,orcid,email,cri] = parse_personal_info(information)

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
        line+=id_process+",,,,\n"
        #process
        label=filename + " creation process"
        line+=label+"," #comment
        line+=id_process+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001025," #type
        line+=keep_label(label)+","
        line+=commastring(14) + "\n" #empty columns
         #role
        label=filename + " creation role"
        line+=label+"," #comment
        line+=fill_id_role+","
        line+="https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001026," #type
        line+=keep_label(label)+","
        line+=commastring(9) #empty columns
        line+=id_process+",,"
        line+=creator_of+",,," #concretizes ontology

        return [line,id_creator,id_process]

def parse_personal_info(info):
       print(info)
       if (info[0]==" "):
                info=info[1:]
       if (info[-1]==" "):
               info = info[:-1]
       fullname=""
       firstname=""
       familyname=""
       orcid=""
       email=""
       cri=""         
       if type(info) is list:
        info=info[0]
       info=info.replace("\n","")
       if (info[-1]==" "):
               info=info[:-1]
        #agents = info.split
       sublines = info.split(" ")
       if (len(sublines)==1): #orcid or mail only, or  https://w3id.org/emmo#AdhamHashibon etc.
                if ("orcid" in info):
                        orcid=info
                elif ("@" in info):
                        email=info
                elif ("http" in info):
                        cri=info

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
                     elif ("http" in sublines[j]):
                        cri=sublines[j][1:-1]                     
                else:
                       fullname=info

       if (fullname!=""):
                namepars=fullname.split(" ")
                firstname=namepars[0]
                familyname=fullname[len(firstname)+1:]

       #print(sublines, fullname)
       
       return [firstname,familyname,orcid,email,cri]


def get_creator_details_lines(ontoname,is_about_val,information): #comment=label, is_about creator(s), information=content of csv cell
        [firstname,familyname,orcid,email,cri] = parse_personal_info(information)
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
        if (cri!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " creator identifier"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_creator-email_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0000578,"                       #"http://purl.obolibrary.org/obo/IAO_0000429," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_val+",,,"
                line+=cri
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
        [firstname,familyname,orcid,email,cri] = parse_personal_info(information)
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
        if (cri!=""):
                if (line!=""):
                       line+="\n"
                label=ontoname + " creator identifier"
                if (fake_id==True):
                        id=idpref+"_"+str(idsuf)+"_creator-email_"+str(idpostf)
                else:
                        id = get_new_id()
                line+=label+"," #comment
                line+=id+","
                line+="http://purl.obolibrary.org/obo/IAO_0000578,"                       #"http://purl.obolibrary.org/obo/IAO_0000429," #type
                line+=keep_label(label)+","
                line+=",," #empty columns
                line+=is_about_contact_person+",,,"
                line+=cri
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
