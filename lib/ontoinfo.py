from rdflib import BNode, URIRef, Literal, Graph, Namespace
from rdflib.collection import Collection
from rdflib.util import guess_format
from rdflib.namespace import RDF, XSD, RDFS, OWL, SKOS, DCTERMS, NamespaceManager
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime
from urllib.request import urlopen, pathname2url
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Tuple
import rdflib
import os
import glob
import re

ext_list = ["trix","ttl","turtle","trig","owl","rdf","n3","xml",
            "json","hext","html","nq","nt","ntriples","xsd",
            "jsd","rj","obo",".omn"]

classes = prepareQuery("SELECT ?entity ?class WHERE {?entity a ?class}") 
onto_lit=rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Ontology')
title_pur = rdflib.term.URIRef('http://purl.org/dc/terms/title')
creator_pur = rdflib.term.URIRef('http://purl.org/dc/terms/creator')
descript_pur = rdflib.term.URIRef('http://purl.org/dc/terms/description')
abstract_pur =  rdflib.term.URIRef('http://purl.org/dc/terms/abstract')
descr2 =  rdflib.term.URIRef('http://purl.org/dc/elements/1.1/description')
allq  = prepareQuery("SELECT ?s ?p ?o WHERE {?s ?p ?o}")

def path2url(path):
    return urljoin(
      'file:', pathname2url(os.path.abspath(path)))

def get_file_extension(filename):
    ext=""
    symb=""
    ind=-1
    while ((symb!=".")):
        symb=filename[ind]
        ind-=1
        ext+=symb
        if (len(ext)==len(filename)):
            return ""
    ext=ext[::-1][1:]
    
    return ext
    
def is_ontology_extension(extension):
    try:
        ind = ext_list.index(extension)
        return True
    except:
        return False
    
def is_ontology_file(filename):
    return is_ontology_extension(get_ontology_extension(filename))

def querry_successful(filename):
    try:
        this_ontology_url = path2url(filename)
        emtest=Graph()
        emtest.parse(this_ontology_url)
        names = []
        qres = emtest.query(classes)
        for row in qres:
            names.append(row.entity)

        names = list(dict.fromkeys(names))    
        if (len(names)>0):
            return True
        else:
            return False
    except Exception as e:
        print("error querrying " + filename + ": " + str(e))
        return False   

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
    if (len(descrs)>0):
        result[4]=descrs[0]
    
    gitlink="https://github.com" + lastname
    result[3]=gitlink
    print (gitlink)

    return result
    