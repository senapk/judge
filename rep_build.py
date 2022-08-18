#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# cria o readme, cria as thumbs e roda o mapi default


import re
import os
import tempfile
import shutil
import argparse
import subprocess
from typing import List, Optional
from os.path import join, getmtime, isdir, isfile


mapi_def_cmd = "mapi_default"

import subprocess
from subprocess import PIPE

class RemoteReadme:
    @staticmethod
    # processa o conteúdo trocando os links locais para links remotos utilizando a url remota
    def __insert_remote_url(content: str, remote_url: Optional[str]) -> str:
        if remote_url is None:
            return content
        if not remote_url.endswith("/"):
            remote_url += "/"
        regex = r"\[(.*)\]\((\s*)([^#:\s]*)(\s*)\)"
        subst = "[\\1](" + remote_url + "\\3)"
        result = re.sub(regex, subst, content, 0, re.MULTILINE)
        return result

    def __refactor_title(content: str, hook) -> str:
        lines = content.split("\n")
        header = lines[0]
        words = header.split(" ")
        del words[0]
        words = ["## @" + hook] + words
        lines[0] = " ".join(words)
        return "\n".join(lines)


    # cria o arquivo readme refazendo os links para ficarem remotos para o github
    @staticmethod
    def create(source_dir: str, output_dir: str, remote: str) -> None:
        source_file = join(source_dir, "Readme.md")
        output_file = join(output_dir, "Readme.md")
        hook = source_dir.split(os.sep)[-1]
        content = open(source_file).read() # pega dados do arquivo readme de origem
        content = RemoteReadme.__refactor_title(content, hook)
        content = RemoteReadme.__insert_remote_url(content, remote + hook)
        open(output_file, "w").write(content)

class Thumb:
    @staticmethod
    def create(source_dir, output_dir):
        if not isdir(source_dir):
            return
        capa = join(source_dir, "cover.jpg")
        thumb = join(output_dir, "thumb.jpg")
        if not isfile(capa):
            print("warning: {} não tem capa".format(source_dir))
            return
        # if modification time of thumb is less than capa, rebuild
        if not isfile(thumb) or getmtime(thumb) < getmtime(capa):
            print("gerando {}".format(source_dir))
            cmd = ["convert", capa, "-resize", "142x80^", "-gravity", "center", "-extent", "142x80", thumb]
            subprocess.run(cmd)

class Mapi:
    @staticmethod
    def create(source_dir):
        root_dir = os.getcwd()
        os.chdir(source_dir)
        subprocess.run(["mapi_default"])
        os.chdir(root_dir)

def last_update(folder):
    return max([getmtime(join(folder, f)) for f in os.listdir(folder) if isfile(join(folder, f))])

def check_rebuild(source_dir: str) -> bool:
    # olha a pasta inteira e pega a data de modificação do arquivo mais recente
    cache_dir = join(source_dir, ".cache")

    # pasta destino não existe ou não tem arquivos
    if not os.path.exists(cache_dir) or len(os.listdir(cache_dir)) == 0:
        return True
    # source tem novas alterações
    return last_update(source_dir) > last_update(cache_dir)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('root_rep', type=str, help="input rep root")
    parser.add_argument('user', type=str, help="username of source repo")
    parser.add_argument('repo', type=str, help="name of source repo")
    # bool parameter
    parser.add_argument('--rebuild', '-r', action='store_true', help="force rebuild all")
    

    args = parser.parse_args()
    remote = "https://raw.githubusercontent.com/" + args.user + "/" + args.repo + "/master/base/"
    base_path = join(args.root_rep, "base")

    hook_list = sorted([hook for hook in os.listdir(base_path) if os.path.isdir(join(base_path, hook))])
    for hook in hook_list:
        source_dir = join(base_path, hook)

        if not args.rebuild and not check_rebuild(source_dir):
            continue

        output_dir = join(source_dir, ".cache")
        shutil.rmtree(output_dir, ignore_errors=True)
        os.mkdir(output_dir)

        
        RemoteReadme.create(source_dir, output_dir, remote)
        Thumb.create(source_dir, output_dir)
        Mapi.create(source_dir)


if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
