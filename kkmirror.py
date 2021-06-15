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

def generate_html(input_file: str, output_file: str, enable_latex: bool):
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
    cmd = ["pandoc", temp_input, '--css', CssStyle.get_file(), '--metadata', 'pagetitle=' + fulltitle, '-s', '-o', output_file]
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

# Format used to send additional files to VPL
class JsonFile:
    def __init__(self, name: str, contents: str):
        self.name: str = name
        self.contents: str = contents
        self.encoding: int = 0

    def __str__(self):
        return self.name + ":" + self.contents + ":" + str(self.encoding)


class JsonVPL:
    def __init__(self, title: str, description: str, tests: str = ""):
        self.title: str = title
        self.description: str = description
        self.executionFiles: List[JsonFile] = [JsonFile("vpl_evaluate.cases", tests)]
        self.requiredFile: Optional[JsonFile] = None
        self.keep_size: int = 0

    def add_execution_file(self, exec_file):
        with open(exec_file) as f:
            file_name = exec_file.split(os.sep)[-1]
            self.executionFiles.append(JsonFile(file_name, f.read()))

    def set_required_file(self, req_file):
        with open(req_file) as f:
            file_name = req_file.split(os.sep)[-1]
            self.requiredFile = JsonFile(file_name, f.read())

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def __str__(self):
        return self.to_json()

def extract_title(readme_file):
    hook = os.path.abspath(readme_file).split(os.sep)[-2]
    with open(readme_file) as f:
        title = f.read().split("\n")[0]
        words = title.split(" ")
        if words[0].count("#") == len(words[0]):  # only #
            del words[0]
        words = [word for word in words if not word.startswith("#")] #removendo as tags
        title = "@" + hook + " " + " ".join(words)
        return title

def mapi_build(readme_file, description_file, tests_file, required_file, keep_files, upload_files, output_file: str):
    
    title = extract_title(readme_file)

    with open(description_file) as f:
            description = f.read()
    with open(tests_file) as f:
        tests = f.read()
    jvpl = JsonVPL(title, description, tests)
    for entry in keep_files:
        jvpl.add_execution_file(entry)
    jvpl.keep_size = len(keep_files)
    for entry in upload_files:
        jvpl.add_execution_file(entry)
    if required_file is not None:
        jvpl.set_required_file(required_file)
    with open(output_file, "w") as f:
        f.write(str(jvpl) + "\n")


def insert_remote_url(content: str, remote_url: Optional[str]) -> str:
    if remote_url is None:
        return content
    if not remote_url.endswith("/"):
        remote_url += "/"
    regex = r"\[(.*)\]\((\s*)([^#:\s]*)(\s*)\)"
    subst = "[\\1](" + remote_url + "\\3)"
    result = re.sub(regex, subst, content, 0, re.MULTILINE)
    return result

def make_readme(source_dir, output_file, remote, hook):
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

def mapi_generate(source_dir, destin_dir):
    output_file = join(destin_dir, "mapi.json")

    description_file = join(destin_dir, "q.html")
    readme_file = join(destin_dir, "Readme.md")
    tests_file = join(destin_dir, "q.vpl")
    cfg_file = join(source_dir, ".mapi")
    required = None
    keep = []
    upload = []
    if os.path.exists(cfg_file):
        f = open(cfg_file)
        config = json.load(f)
        f.close()
        required = config["required"]
        if required is not None:
            required = join(source_dir, required)
            shutil.copy(required, destin_dir)
        keep = [join(source_dir, f) for f in config["keep"]]
        for entry in keep:
            shutil.copy(entry, destin_dir)
        upload = [join(source_dir, f) for f in config["upload"]]

    mapi_build(readme_file, description_file, tests_file, required, keep, upload, output_file)

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
            make_readme(source_dir, output_readme, remote, hook)
            generate_html(output_readme, join(destin_dir, "q.html"), True)
            make_tests(source_dir, join(destin_dir, "q.tio"))
            make_tests(source_dir, join(destin_dir, "q.vpl"))
            
            mapi_generate(source_dir, destin_dir)

    hooks_output = [hook for hook in os.listdir(output_base) if os.path.isdir(join(output_base, hook))]
    for hook in sorted(hooks_output):
        if hook not in hooks_input:
            shutil.rmtree(join(output_base, hook))

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
