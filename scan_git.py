from github import Github
from github import Auth
import pygit2
import pandas as pd
import os
import glob
import re
import time
from pygit2 import Repository
import sys
from git import Repo
import argparse
sys.path.insert(1, './lib')     #add local library path
import gitcrawl

# Instantiate the parser
parser = argparse.ArgumentParser(description='Clones all the repositories of provided user, or the specific one')

# Required positional argument - git user name
parser.add_argument('user_arg', type=str,
                    help='A required string argument - git user name')
# Optional argument
parser.add_argument('--repo_name', type=str,
                    help='Optional: git repository name')
# Optional argument
parser.add_argument('--clone_path', type=str,
                    help='Optional: local path for storing cloned repositories')

args = parser.parse_args()

user=""
repname=""
folder=""
try:
    print("Git user name: " + args.user_arg)
    user = args.user_arg
except:
    print("Error:provide a git user name!")
    exit()

try:
    repname = args.repo_name
    print("Git repo name: " + args.repo_name)
except:
    print("No Git repository provided: scanning all user repositories")
    repname=""
    pass

try:
    folder = args.clone_path
except:
    pass

if (folder==None):
        folder="Downloads"

print("Clone path: " + str(folder))

prefix="https://github.com/"
prefix+="/"+user+"/"
clone_subfold="/"+user+"/"+repname

names_to_clone = [repname]
if (repname==""):
    names_to_clone = gitcrawl.get_user_repos(user)

for repo in names_to_clone:
    print("cloning " + repo)
    try:
        myrep = gitcrawl.clone_repo(folder,user,repo)
    except:
        print("this repository is already cloned")
        pass
    
    myrep = Repository(folder+clone_subfold)

    defbranch = myrep.head.shorthand
    print("default branch = "+defbranch)

    branches = []
    tags=[]

    pre_bra = "refs/remotes/origin/"
    pre_tag ="refs/tags/"

    for branch in list(myrep.references):
        if (pre_bra in branch):
            if ("gh-pages" in branch):  #ignore gh-pages branches
                continue
            if ("HEAD" in branch):
                continue
            if ("issue" in branch): #ignore issue-specific branches
                continue
            if (branch[len(pre_bra):] == defbranch):
                continue
            if (branch[len(pre_bra):] == "refs"):
                continue
            branches.append(branch[len(pre_bra):])
            try:
                Repo.clone_from(prefix+repo, folder+clone_subfold+"/more_branches/"+branches[-1],branch=branches[-1])
            except:
                pass
        elif pre_tag in branch:
            tags.append(branch[len(pre_tag):]) 

    branches.append(defbranch)
    print("branches: ")
    print(branches)
    print("tags: ")
    print(tags)     

