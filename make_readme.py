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
    regex = r"\[(.*?)\]\((\s*?)([^#:\s]*?)(\s*?)\)"
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
    parser.add_argument('source_file', type=str, help="input readme file")
    parser.add_argument('output_file', type=str, help="output readme file")

    args = parser.parse_args()
    remote = "https://raw.githubusercontent.com/" + args.user + "/" + args.repo + "/master/base/"

    abs_path = os.path.abspath(args.source_file)
    hook = abs_path.split(os.sep)[-2]
    make_readme_remote_newtitle(args.source_file, args.output_file, remote, hook)

    print("Remote created for " + hook)

if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
