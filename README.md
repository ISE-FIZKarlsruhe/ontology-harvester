# GitHub Ontology Harvester

A Python tool to scan GitHub repositories and extract ontology metadata from ontology files.
It is designed to support ontology discovery, metadata curation, and repository documentation in line with the NFDIcore ontology metadata description principles.

# Table of Contents  

[How to use](#How-to-use)  
 - [Cloning repositories][#cloning-repositories-for-scanning:]
 - Extracting Ontologies
 - Creating the template file
 - Asserting the individuals
   
[Procedure description](#Procedure-description)  

[Ontology metadata scheme based on NFDIcore](#NFDIcore-ontology-metadata)

[Contact](#Contact)

# How to use
### 1. Cloning repositories for scanning:
execute the scan_git.py file:
```
python scan_git.py git_username --repo_name XXX --clone_path YYY
```
The first argument is mandatory which is the Github username.</br>
The second argument is arbitrary and specify the certain repository otherwise all user repositories are scanned.</br>
the third argument names the folder in which repositories will be cloned. By default its "Downloads" folder.</br>

### 2. Scanning cloned repositories for the ontology files and extracting the info:
execute the extract_ontologies.py file:
```
python extract_ontologies.py YYY --output_filename ZZZ
```
The first argument is mandatory which is the folder with cloned repositories from the previous script. Downloads should be specified by default.</br>
The second argument is arbitrary and specify the filename with information about the found ontologies. Ontologies.csv is the default name.</br>

### 3. Creating the ODK robot template file (tsv), for the next step:

```
python csv_to_odk.py 
```

This takes as input the "Ontologies_MSE.csv" from the step 2 and outputs the "template.tsv" file, which is a ODK robot (https://incatools.github.io/ontology-development-kit/) template, containing all the class instantiations, IRIs, and relations between the instances.

### 4. Asseting the extracted information into the ontology file:
use the ODK robot tool (see the "robot.bat" file) to transform the template file from the previous step into the instances asserted into the "nfdicore-full.owl" file, which is the full version of NFDIcore 3.0 ontology (https://ise-fizkarlsruhe.github.io/nfdicore/).

Command should be modified according to your ODK/Java installation and looks like:
```
java  -jar C:\Windows\robot.jar template --merge-before --input .\nfdicore-full.owl --template .\template.tsv --output nfdi-out-tsv.owl
```
It produces the "nfdi-out-tsv.owl" file, containing the instances extracted from the clonned repositories, and asserted into the full version of the NFDIcore ontology.

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
   
    The above information is then verified while reviewing the CSV file.
   
  - the line is appended to the CSV file. It is created if not existing at the start of the script.
 
  Also, the csv-file for git repositories is created to store the information about the repositories, having the following columns:
  - link to the repository,
  - list of branches,
  - number of rdf-like files (files with triplets),
  - number of ontology files (describing an ontology),
  - first and last commit to the repository.
 
  ### Batch scanning
  The file "scan_user_list.py" takes all names of the git users from the file "MSE_ontologies.xlsx - All ontologies.csv" and clones all repositories of these users.

# NFDIcore ontology metadata
Describing the metadata of ontologies with NFDIcore

## Intro

Ontologies are crucial for knowledge sharing and reuse on the Semantic Web, but finding suitable ontologies can be challenging.  Effective ontology discovery and reuse depend on comprehensive metadata descriptions, but current metadata schemas have limitations, including limited scope, lack of harmonization, and maintenance issues.  This paper introduces a metadata schema for ontology repositories based on the Basic Formal Ontology (BFO) 2020 and the NFDIcore ontology new release 3.0.  This schema leverages BFO's standardized framework and NFDIcore's promising approach to knowledge graph managing, to address the limitations of existing schemas and enhance semantic interoperability and reasoning over metadata items.

## Describing ontology metadata

### 1. Ontology object
   
Clases:
* ``nfdicore:Ontology``  <br/>
* ``nfdicore:NameSpace``  <br/>
* ``nfdicore:Title``  <br/>
* ``nfdicore:Description``  <br/>

Properties:

* ``obo:is about``  <br/>
  
The central object about which we discuss here is the ontology - an abstract concept, which stands for the designation and incorporates all its components: versions/modules/variants/ other artifacts. We treat the namespace of the ontology at the unique identifier. Hence, 1 namespace uri = 1 ontology object. Some people put number of the versions there either in fair slash release variant, etc., or even file extensions, which is the incorrect usage of namespace.  

As proprties of the ontology, apart from the namespace URI, we have two types of text entities here: title and description.

### 2. Ontology versions, variants and formats
   
Classes:

* ``nfdicore: Ontology Release Version``  <br/>
* ``nfdicore: Ontology Variant``  <br/>
* ``nfdicore: File Data Item``  <br/>

Properties:

* ``obo:is about``  <br/>
* ``obo:continuant part of``  <br/>
* ``nfdicore: has value``  <br/>

Similarly to what we have in software engineering repository for ontologies can contain different release versions with different features, e.g., ver. 0.1, ver. 1.2. This corresponds to the ontology release version class, which is connected with the property of or has continued part of ontology object. Each release version should ideally be characterized by its version IRI, for which we use nfdicore: has value data property. sometimes version iris are used incorrectly, containing information about file extensions or arbitrary comments. If the version literal is actually an IRI (starts from http://) we use nfdicore:versionIRI class, otherwise we use nfdicore:versionNumber class. Ontology release version is obo: continuant part of the corresponding ontology. 

In turn, release verions can be present in different variants, meaning, e.g., "reasoned", where the inferred axioms are included, "full", with incorporated import statements. This corresponds to nfdicore: Ontology Variant class, which is obo: continuant part of the release version. 

Ontologies with their versions and variants are avtually located in the files, having certain extensions. For this we use nfdicore:dataItem. If variant is specified, we use say that dataItem obo:is_about variant. Alternatively, if no variant is present, but version is present, we assert dataItem obo:is_about ontology version statement. Lastly, if no variant and no version specified for the ontology, dataItem obo:is_about ontology. 

Each file has one extension, and to instantiate the extension object, we use subclasses of edam:rdf format (subclass of iao:data format specification) - e.g., turtle format. To connect data item with the extension object, we use nfdicore:has format property. 

### 3. Ontology repository, files and documentation links

Classes:
* ``nfdicore:Source Code Repository``  <br/>
* ``edam:Format``  <br/>
* ``nfdicore:Website``  <br/>
* ``nfdicore:Document``  <br/>

Properties:

* ``obo:is about``  <br/>
* ``dcat:download URL``  <br/>
* ``nfdicore:has url``  <br/>
* ``obo:continuant part of``  <br/>

We use the NFDIcore class Source Code repository, since the principles of data organization share a lot in common between the organized collections of triplet file (ontology), and source code files.

The ontology repository contains files with the triplets that are the essence of the ontology. While each ``nfdicore: File Data Item`` ``is about`` ontology and its variant objects, it is also ``obo:continuant part of`` the nfdicore:Source Code Repository object. In this way we specify the belongings of the files to the repository. As each file contains has its download link in parentheses GitHub repository address, we use dcat:download URL object property to connect the file to its link object, which is of the nfdicore:Website class.  if present we instantiate the nfdicore:Document object standing for the ontology documentation, which obo:is about the ontology object. 

Then to provide the corresponding links objects they are string representation we use an FDI core as URL data property:
* The ``nfdicore:Source Code Repository`` repository object ``nfdicore:has url`` the string, e.g., ``https://github.com/my-ontology^xsd:string``.
* The ``nfdicore: File Data Item`` file object ``nfdicore:has url`` the string, e.g., ``github.com/my-ontology/file.ttl^^xsd:string``.
* The ``nfdicore:Document`` documentation object ``nfdicore:has url`` the string, e.g., ``github.com/my-ontology/documentation.html^^xsd:string``.

### 4. Ontology creators and contact points
   
Classes:

* ``nfdicore:Agent``  <br/>
* ``nfdicore:Person``  <br/>
* ``nfdicore:Organization``  <br/>
* ``nfdicore:Creator Role``  <br/>
* ``nfdicore:Creative Process``  <br/>
* ``nfdicore:Contact Point Role``  <br/>
* ``nfdicore:Contacting Process``  <br/>

Properties:

* ``bfo:concretizes``  <br/>
* ``bfo:realizes``  <br/>
* ``bfo:bearer of``  <br/>
* ``bfo:participates in``  <br/>
* ``nfdicore: has creator``  <br/>
* ``nfdicore: has contact point``  <br/>
* ``obo:is about``  <br/>


To describe that particular person or an organization is a creator or a contact point of some ontology we use the so-called role pattern which is typical for the bfo-based ontologies. This means instead of the intuitively obvious solution to define a class of contact point / creator, and create a corresponding individual of that class, we do the following: instantiate the so-called roles which are specifically dependent continuants, which describe certain functions which, e.g., perrson plays in certain situation, for example the role of a father at home, or the role of a teacher at school. 
Then we say that there is some agent and it is bearer of contact point and/or creator role, which is realized in contacting or creative process correspondingly. Ontology then participates in the corresponding process. As the shortcuts we have the corresponding properties has contact point and has creator which connect ontology to the corresponding agent. This approach solves the problem when one agent is creator and contact point of different ontologies. 

## Class definitions

Ontology - An (nfdi) ontology is a data item that coherently represents all components of an ontology, including its versions, variants, modules and other associated artifacts. It is typically denoted by a name and/or an acronym, which is the term we use to communicate about it.An (nfdi) ontology is a data item that coherently represents all components of an ontology, including its versions, variants, modules and other associated artifacts. It is typically denoted by a name and/or an acronym, which is the term we use to communicate about it.

O. Release Version - An (nfdi) ontology release version represents a particular release of an ontology.

O. Namespace - A namespace refers to a distinct, unique identifier that is used to distinguish concepts and entities within an ontology from those in other ontologies or systems. It's typically represented as a URL or URI (Uniform Resource Identifier) and ensures that each element within the ontology has a globally unique reference.

O. Variant - An ontology variant represents a self-contained, reusable subset of an ontology that provides a specific functionality while maintaining interoperability with the larger ontology. Typically, an ontology is released in different variants, which makes a variant a release artifact.

File Data Item - A file data item is a data item that represents a file stored on a hard drive. It might also include essential attributes like its name, location, download URL, size, type, and timestamps for creation, modification, and access. It might also capture permissions and ownership details to control how the file can be accessed or modified.

Source Code Repository - A document that organizes and stores source code files, associated metadata, and version history to facilitate the management, sharing, and collaborative development of software projects. It serves as a structured collection of information that tracks changes, maintains integrity, and supports workflows such as version control, branching, and merging.

Website - An information content entity that represents a collection of interconnected web pages, multimedia content, and digital resources accessible via the World Wide Web.

Title - A textual entity that denotes some resource.

Description  - A textual entity that describe some resource.

Contact Point - An agent that serves as a designated interface for communication, facilitating the exchange of information, support, or services between individuals, organizations, or systems.


# Contact

Dr. Konstantin Gubaev (Kostiantyn Hubaiev)

ORCID ID: https://orcid.org/0000-0003-2612-8515</br>
work e-mail: kostiantyn.hubaiev@fiz-karlsruhe.de</br>
personal e-mail: yamir4eg@gmail.com</br>
