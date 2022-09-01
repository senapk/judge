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
from enum import Enum

import subprocess
from subprocess import PIPE


def extract_title(readme_file):
    title = open(readme_file).read().split("\n")[0]
    parts = title.split(" ")
    if parts[0].count("#") == len(parts[0]):
        del parts[0]
    title = " ".join(parts)
    return title

class CssStyle:
    data = "body,li{color:#000}body{line-height:1.4em;max-width:42em;padding:1em;margin:auto}li{margin:.2em 0 0;padding:0}h1,h2,h3,h4,h5,h6{border:0!important}h1,h2{margin-top:.5em;margin-bottom:.5em;border-bottom:2px solid navy!important}h2{margin-top:1em}code,pre{border-radius:3px}pre{overflow:auto;background-color:#f8f8f8;border:1px solid #2f6fab;padding:5px}pre code{background-color:inherit;border:0;padding:0}code{background-color:#ffffe0;border:1px solid orange;padding:0 .2em}a{text-decoration:underline}ol,ul{padding-left:30px}em{color:#b05000}table.text td,table.text th{vertical-align:top;border-top:1px solid #ccc;padding:5px}"
    path = None
    @staticmethod
    def get_file():
        if CssStyle.path is None:
            CssStyle.path = tempfile.mktemp(suffix=".css")
            with open(CssStyle.path, "w") as f:
                f.write(CssStyle.data)
        return CssStyle.path

def generate_html(input_file: str, output_file: str, enable_latex: bool):
    title = extract_title(input_file)
    fulltitle = title.replace('!', '\\!').replace('?', '\\?')
    cmd = ["pandoc", input_file, '--css', CssStyle.get_file(), '--metadata', 'pagetitle=' + fulltitle,
           '-s', '-o', output_file]
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

parser = argparse.ArgumentParser()
parser.add_argument("mdfile", type=str, help="file title and content")
parser.add_argument("--output", "-o", type=str, help="html file")
args = parser.parse_args()

desc_file = args.output
if desc_file is None:
    temp_dir = tempfile.mkdtemp()
    desc_file = temp_dir + "/q.html"

generate_html(args.mdfile, desc_file, True)
print("Html created for", args.mdfile)
if args.output is None:
    print(open(desc_file).read())