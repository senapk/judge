#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import shutil
import argparse
import subprocess
from os.path import join, getctime
import kkremote
import kkhtml
import kkmapi

def make_readme(source_dir, output_file, remote, hook):
    content = open(join(source_dir, "Readme.md")).read()
    content = kkremote.insert_remote_url(content, remote + hook)
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

def mirror(input_rep, output_rep, remote, rebuild):
    input_base = join(input_rep, "base")
    output_base = join(output_rep, "base")
    hooks_input = [hook for hook in os.listdir(input_base) if os.path.isdir(join(input_base, hook))]
    for hook in sorted(hooks_input):
        source_dir = join(input_base, hook)
        destin_dir = join(output_base, hook)
        if rebuild or not os.path.exists(destin_dir) or getctime(source_dir) > getctime(destin_dir):
            print("updating", hook)
            if not os.path.exists(destin_dir):
                os.mkdir(destin_dir)
            cp_images(source_dir, destin_dir)
            output_readme = join(destin_dir, "Readme.md")
            make_readme(source_dir, output_readme, remote, hook)
            kkhtml.generate(output_readme, join(destin_dir, "q.html"), True)
            make_tests(source_dir, join(destin_dir, "q.tio"))
            make_tests(source_dir, join(destin_dir, "q.vpl"))
            kkmapi.generate(destin_dir, join(destin_dir, "mapi.json"))

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
