This is a Python tool to scan GitHub repositories and extract data from the ontology files.

# Table of Contents  

[How to use](#How-to-use)  

[Procedure description](#Procedure-description)  

[Contact](#Contact)

# How to use
### 1. Cloning repositories for scanning:
execute the scan_git.py file:
```
python scan_git.py git_username --repository_name --clone_path
```
The first argument is mandatory which is the Github username.</br>
The second argument is arbitrary and specify the certain repository otherwise all user repositories are scanned.</br>
the third argument names the folder in which repositories will be cloned. By default its "Downloads" folder.</br>

### 2. Scanning cloned repositories for the ontology files and extracting the info:
execute the extract_ontologies.py file:
```
python extract_ontologies.py folder_name --output_filename
```
The first argument is mandatory which is the folder with cloned repositories from the previous script. Downloads should be specified by default.</br>
The second argument is arbitrary and specify the filename with information about the found ontologies. Ontologies.csv is the default name.</br>

# Procedure description
### 1. Cloning repositories:

- forked repositories are ignored.
  
- each branch is cloned, except the ones having "gh-pages" or "issue" in the name, thus ignoring the website and issue-specific branches.

- no user API key is needed.

### 2. Scanning repositories for ontology files:

- extensions list to be checked: ["trix","ttl","turtle","trig","owl","rdf","n3","xml","json","hext","html","nq","nt","ntriples","xsd","jsd","rj","obo",".omn"].

- for each user and for each repository the corresponding folder is scanned for files with the above extensions. These are "ontology candidates" files.

- for each ontology candidate file the test query is performed querying the list of classes. If success, it is a valid file for further actions. Otherwise skip the file.

- since we are aiming for extracting the ontologies information, using the SPARQL querying (via rdflib library) we are searching for the (s,p,o) rdf-triples. First we search for the object:
    - 'http://www.w3.org/2002/07/owl#Ontology', subject is the ontology PID. If it is NOT empty, we continue. Otherwise, skip the file.
- then we search for the following predicates:
    - 'http://purl.org/dc/terms/title', subject is the ontology title. If it is NOT empty, we continue. Otherwise, skip the file.
    - 'http://purl.org/dc/terms/description', subject is the ontology description. If empty:
      - 'http://purl.org/dc/terms/abstract', use subject (abstract) as the description. If empty:
          - 'http://purl.org/dc/elements/1.1/description', use subject as the desciprtion.
    - 'http://purl.org/dc/terms/creator', subject is the ontology creator
    - 'owl:versionIRI', subject is the version description. If empty:
        - 'owl:versionInfo', subject is the version description.
     
  - any of the above fields can be empty except title and PID of the ontology.
 
  - next we create a line in the CSV file corresponding to the ontology file, adding the following columns:
      - path to the file on the GitHub,
      - file extension,
      - branch of the repository containing this file,
      - if the filename contains any of [base, simple, inferred, edit, full, import, export], with "_" or "-" at the beginning, we add this info into the "ontology type" column.
        
    Next we use Microsoft OpenAI (API key is needed) to parse README.md and LICENCE files (if exist) for the following columns:
    
      - contact information,
      - documentation link,
      - related project info,
      - license information.
   
  - the line is appended to the CSV file. It is created if not existing at the start of the script.
 
  Also, the csv-file for git repositories is created to store the information about the repositories, having the following columns:
  - link to the repository
  - list of branches
  - number of rdf-like files (files with triplets)
  - number of ontology files (describing an ontology)
  - first and last commit to the repository.

# Contact

Dr. Konstantin Gubaev (Kostiantyn Hubaiev)

ORCID ID: https://orcid.org/0000-0003-2612-8515</br>
work e-mail: kostiantyn.hubaiev@fiz-karlsruhe.de</br>
personal e-mail: yamir4eg@gmail.com</br>
