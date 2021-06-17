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
import json

import subprocess
from subprocess import PIPE


def insert_remote_url(content: str, remote_url: Optional[str]) -> str:
    if remote_url is None:
        return content
    if not remote_url.endswith("/"):
        remote_url += "/"
    regex = r"\[(.*)\]\((\s*)([^#:\s]*)(\s*)\)"
    subst = "[\\1](" + remote_url + "\\3)"
    result = re.sub(regex, subst, content, 0, re.MULTILINE)
    return result

def make_readme_remote_newtitle(source_dir, output_file, remote, hook):
    content = open(join(source_dir, "Readme.md")).read()
    content = insert_remote_url(content, remote + hook)
    open(output_file, "w").write(content)

def make_tests(source_dir, output_target):
    cmd = ["tk", "build", '-f', output_target, join(source_dir, "Readme.md")]
    extra = join(source_dir, "t.tio")
    if os.path.isfile(extra):
        cmd.append(extra)
    subprocess.run(cmd)

def cp_images(source_dir, destin_dir):
    files = [file for file in os.listdir(source_dir) if file.endswith(".jpg") or file.endswith(".png")]
    for file in files:
        shutil.copy(join(source_dir, file), destin_dir)

def last_update(folder):
    return max([getmtime(join(folder, f)) for f in os.listdir(folder)])

def check_rebuild(source_dir, destin_dir, rebuild_all):
    rebuild_this = rebuild_all
    if not os.path.exists(destin_dir):
        os.mkdir(destin_dir)
        rebuild_this = True

    if len(os.listdir(destin_dir)) == 0:
        rebuild_this = True

    if not rebuild_this:
        smtime = last_update(source_dir)
        dmtime = last_update(destin_dir)
        if smtime > dmtime:
            rebuild_this = True
            
    return rebuild_this

def mirror(input_rep, output_rep, remote, rebuild_all):
    input_base = join(input_rep, "base")
    output_base = join(output_rep, "base")
    hooks_input = [hook for hook in os.listdir(input_base) if os.path.isdir(join(input_base, hook))]
    for hook in sorted(hooks_input):

        source_dir = join(input_base, hook)
        destin_dir = join(output_base, hook)
        
        if check_rebuild(source_dir, destin_dir, rebuild_all):
            print("updating", hook)
            cp_images(source_dir, destin_dir)
            output_readme = join(destin_dir, "Readme.md")
            make_readme_remote_newtitle(source_dir, output_readme, remote, hook)
            generate_html(output_readme, join(destin_dir, "q.html"), True)
            make_tests(source_dir, join(destin_dir, "q.tio"))
            make_tests(source_dir, join(destin_dir, "q.vpl"))
            
            mapi_generate(source_dir, destin_dir)

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
    parser.add_argument("--rebuild", '-r', action="store_true")

    args = parser.parse_args()
    remote = "https://raw.githubusercontent.com/" + args.user + "/" + args.repo + "/master/base/"
    mirror(args.input_rep, args.output_rep, remote, args.rebuild)


if __name__ == '__main__':
    main()
