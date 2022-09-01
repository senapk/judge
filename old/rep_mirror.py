#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import tempfile
import shutil
import argparse
import subprocess
from typing import List, Optional
from os.path import join, getmtime


mapi_def_cmd = "mapi_default"

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
def make_readme_remote_newtitle(source_dir: str, output_file: str, remote: str, hook: str) -> None:
    content = open(join(source_dir, "Readme.md")).read() # pega dados do arquivo readme de origem
    lines = content.split("\n")
    header = lines[0]
    words = header.split(" ")
    del words[0]
    words = ["## @" + hook] + words
    lines[0] = " ".join(words)
    content = "\n".join(lines)
    content = insert_remote_url(content, remote + hook)
    open(output_file, "w").write(content)

# copia todos os arquivos da pasta de origem para a pasta de destino
def copy_files_only(source_dir, destin_dir):
    def is_file(folder, file):
        return os.path.isfile(os.path.join(folder, file))

    files = [file for file in os.listdir(source_dir) if is_file(source_dir, file)]
    for file in files:
        shutil.copy(join(source_dir, file), destin_dir)

# olha a pasta inteira e pega a data de modificação do arquivo mais recente
def last_update(folder):
    return max([getmtime(join(folder, f)) for f in os.listdir(folder)])


def check_rebuild(source_dir: str, destin_dir: str) -> bool:
    # pasta destino não existe ou não tem arquivos
    if not os.path.exists(destin_dir) or len(os.listdir(destin_dir)) == 0:
        return True
    # source tem novas alterações
    return last_update(source_dir) > last_update(destin_dir)

# realiza mirror de um repositorio para outro
def mirror(input_rep, output_rep, remote):
    input_base = join(input_rep, "base")
    output_base = join(output_rep, "base")
    if not os.path.exists(output_base):
        os.mkdir(output_base)

    # lista ordenada de labels da pasta base do repositório de entrada
    hooks_input = sorted([hook for hook in os.listdir(input_base) if os.path.isdir(join(input_base, hook))])
    
    base_root = os.getcwd()
    for hook in hooks_input:

        source_dir = join(input_base, hook)
        destin_dir = join(output_base, hook)
        
        if check_rebuild(source_dir, destin_dir):
            print("updating", hook)
            shutil.rmtree(destin_dir, ignore_errors=True)
            os.mkdir(destin_dir)
            copy_files_only(source_dir, destin_dir)
            
            # reescreve Readme.md com links para apontarem para o path absoluto do moodle
            output_readme_path = join(destin_dir, "Readme.md")
            make_readme_remote_newtitle(source_dir, output_readme_path, remote, hook)
            os.chdir(destin_dir)
            print(os.getcwd())
            subprocess.run(["mapi_default"])
            os.chdir(base_root)
            

    hooks_output = [hook for hook in os.listdir(output_base) if os.path.isdir(join(output_base, hook))]
    for hook in sorted(hooks_output):
        if hook not in hooks_input:
            shutil.rmtree(join(output_base, hook))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_rep', type=str, help="input rep root")
    parser.add_argument('output_rep', type=str, help="output rep root")
    parser.add_argument('user', type=str, help="username of source repo")
    parser.add_argument('repo', type=str, help="name of source repo")

    args = parser.parse_args()
    remote = "https://raw.githubusercontent.com/" + args.user + "/" + args.repo + "/master/base/"
    mirror(args.input_rep, args.output_rep, remote)


if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
