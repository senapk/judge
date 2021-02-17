#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import argparse
import subprocess
from subprocess import PIPE


def generate(input_file: str, output_file: str, enable_latex: bool):
    hook = os.path.abspath(input_file).split(os.sep)[-2]
    lines = open(input_file).read().split("\n")
    header = lines[0]
    title = "@" + hook + " " + " ".join([word for word in header.split(" ") if not word.startswith("#")])
    content = "\n".join(lines[1:])
    tags = [word for word in header.split(" ") if word.startswith("#") and word.count("#") != len(word)]
    temp_input = tempfile.mktemp(suffix=".md")
    with open(temp_input, "w") as f:
        f.write("## " + title + " " + " ".join(tags) + "\n" + content)
    fulltitle = title.replace('!', '\\!').replace('?', '\\?')
    cmd = ["pandoc", temp_input, '--metadata', 'pagetitle=' + fulltitle, '-s', '-o', output_file]
    if enable_latex:
        cmd.append("--mathjax")
    try:
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        stdout, stderr = p.communicate()
        if stdout != "" or stderr != "":
            print(stdout)
            print(stderr)
    except Exception as e:
        print("Erro no comando pandoc:", e)
        exit(1)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', type=str, help="name of input markdown file")
    parser.add_argument('output_file', type=str, help="name of output html file")
    parser.add_argument('--dindex', action='store_true', help="disable insert index in name")
    parser.add_argument('--dlatex', action='store_true', help="disable latex rendering")

    args = parser.parse_args()
    generate(args.input_file, args.output_file, not args.dlatex)


if __name__ == '__main__':
    main()
