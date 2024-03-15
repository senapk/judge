#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#this script must run from inside hook
import configparser
from typing import List
import os
import subprocess
import argparse

# def replace_title(lines: List[str], hook: str) -> List[str]:
#     header = lines[0]
#     words = header.split(" ")
#     del words[0]
#     words = ["# @" + hook] + words
#     lines[0] = " ".join(words)
#     return lines

def insert_online_link(lines: List[str], online: str) -> List[str]:
    lines.insert(1, "\nVeja a versão online: [aqui.](" + online + ")")
    
    return lines

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input' , '-i', type=str, default="Readme.md" ,help="readme source file")
    parser.add_argument('--output', '-o', type=str, default=".cache/Readme.md", help="remote readme file")

    args = parser.parse_args()

    source = args.input
    target = args.output

    config = configparser.ConfigParser()

    cfg = "../../remote.cfg"

    if not os.path.isfile(cfg):
        print("no remote.cfg found")
        return

    config.read(cfg)

    user = config["DEFAULT"]["user"]
    repo = config["DEFAULT"]["rep"]
    base = config["DEFAULT"]["base"]

    hook = os.path.basename(os.getcwd())
    remote = os.path.join(base, hook)
   
    lines = open(source).read().split("\n")
    # lines = replace_title(lines, hook)
    online_readme_link = os.path.join("https://github.com", user, repo, "blob/master", remote, "Readme.md")
    lines = insert_online_link(lines, online_readme_link)
    open(target, "w").write("\n".join(lines))
    subprocess.run(["make_remote", user, repo, remote, target, target])

if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)







