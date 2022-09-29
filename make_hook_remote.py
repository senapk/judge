#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#this script must run from inside hook
import configparser
import os
import subprocess
import argparse

def replace_title(content: str, hook: str) -> str:
    lines = content.split("\n")
    header = lines[0]
    words = header.split(" ")
    del words[0]
    words = ["## @" + hook] + words
    lines[0] = " ".join(words)
    content = "\n".join(lines)
    return content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input' , '-i', type=str, default="Readme.md" ,help="readme source file")
    parser.add_argument('--output', '-o', type=str, default=".cache/Readme.md", help="remote readme file")

    args = parser.parse_args()

    source = args.input
    target = args.output

    config = configparser.ConfigParser()

    config.read("../.database.cfg")

    user = config["DEFAULT"]["user"]
    repo = config["DEFAULT"]["rep"]
    base = config["DEFAULT"]["base"]

    hook = os.path.basename(os.getcwd())
    remote = os.path.join(base, hook)
   
    content = open(source).read()
    content = replace_title(content, hook)
    open(target, "w").write(content)
    subprocess.run(["make_remote", user, repo, remote, target, target])

if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)







