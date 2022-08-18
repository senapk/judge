#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import tempfile
import shutil
import argparse
import subprocess
from time import mktime
from typing import List, Optional
from os.path import join, getmtime

from os.path import join, isdir, isfile, getmtime


import subprocess
from subprocess import PIPE

# processa o conteúdo trocando os links locais para links remotos utilizando a url remota
def insert_remote_url(content: str, remote_url: Optional[str]) -> str:
    if remote_url is None:
        return content
    if not remote_url.endswith("/"):
        remote_url += "/"
    regex = r"\[(.*)\]\((\s*)([^#:\s]*)(\s*)\)"
    subst = "[\\1](" + remote_url + "\\3)"
    result = re.sub(regex, subst, content, 0, re.MULTILINE)
    return result

# cria o arquivo readme refazendo os links para ficarem remotos para o moodle
def make_readme_remote_newtitle(source_file: str, output_file: str, remote: str, hook: str) -> None:
    content = open(source_file).read() # pega dados do arquivo readme de origem
    lines = content.split("\n")
    header = lines[0]
    words = header.split(" ")
    del words[0]
    words = ["## @" + hook] + words
    lines[0] = " ".join(words)
    content = "\n".join(lines)
    content = insert_remote_url(content, remote + hook)
    open(output_file, "w").write(content)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('user', type=str, help="username of source repo")
    parser.add_argument('repo', type=str, help="name of source repo")

    args = parser.parse_args()
    remote = "https://raw.githubusercontent.com/" + args.user + "/" + args.repo + "/master/base/"

    base_dir = join(os.getcwd(), "base")
    # lista ordenada de labels da pasta base do repositório de entrada
    hooks_input = sorted([hook for hook in os.listdir(base_dir) if os.path.isdir(join(base_dir, hook))])
    
    for hook in hooks_input:
        source = join(base_dir, hook, "Readme.md")
        
        cache = join(base_dir, hook, ".cache")
        if not isdir(cache):
            os.mkdir(cache)
        target = join(cache, "Readme.md")
        
        if not isfile(target) or getmtime(source) > getmtime(target):
            print("updating remote readme:", hook)
            make_readme_remote_newtitle(source, target, remote, hook)


if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
