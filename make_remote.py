#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
from typing import Optional
from subprocess import PIPE

# processa o conteúdo trocando os links locais para links remotos utilizando a url remota
def __replace_remote(content: str, remote_raw: str, remote_view: str, remote_folder: str) -> str:
    if not remote_raw.endswith("/"):
        remote_raw += "/"
    if not remote_view.endswith("/"):
        remote_view += "/"
    if not remote_folder.endswith("/"):
        remote_folder += "/"

    #trocando todas as imagens com link local
    regex = r"!\[(.*?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
    subst = "![\\1](" + remote_raw + "\\3)"
    result = re.sub(regex, subst, content, 0)


    regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?/)\)"
    subst = "[\\1](" + remote_folder + "\\3)"
    result = re.sub(regex, subst, result, 0)

    #trocando todos os links locais cujo conteudo nao seja vazio
    regex = r"\[(.+?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
    subst = "[\\1](" + remote_view + "\\3)"
    result = re.sub(regex, subst, result, 0)

    return result

def replace_remote(content: str, user: str, repo: str, path: str):
    remote_raw    = os.path.join("https://raw.githubusercontent.com", user, repo, "master" , path)
    remote_view    = os.path.join("https://github.com/", user, repo, "blob/master", path)
    remote_folder = os.path.join("https://github.com/", user, repo, "tree/master", path)
    return __replace_remote(content, remote_raw, remote_view, remote_folder)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('user', type=str, help="username of source repo")
    parser.add_argument('repo', type=str, help="name of source repo")
    parser.add_argument('base', type=str, help="relative path to root")
    parser.add_argument('source_file', type=str, help="input readme file")
    parser.add_argument('output_file', type=str, help="output readme file")

    args = parser.parse_args()

    # abrindo arquivo
    content = open(args.source_file).read()
    content = replace_remote(content, args.user, args.repo, args.base)
    open(args.output_file, "w").write(content)
    
    print("    Remote Readme created for " + os.path.join(args.base, args.output_file))

if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)


