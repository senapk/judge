#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Tuple, Dict
from os.path import getmtime
import glob
import configparser
import os
import subprocess
import argparse
import re
from subprocess import PIPE
import tempfile
import json
import enum

class Log:
    verbose = False

    @staticmethod
    def print(*args, **kwargs):
        if Log.verbose:
            print(*args, **kwargs)
    
    @staticmethod
    def write(*args, **kwargs):
        if Log.verbose:
            print(*args, **kwargs)
        else:
            print(*args, **kwargs, end="", flush=True)

class Check:
    # return the last update for the most recent file in the directory
    @staticmethod
    def last_update(path) -> Tuple[str, float]:
        value = 0
        if os.path.isfile(path):
            value = (path, getmtime(path))
        else:
            file_list = list(glob.iglob(path + '/**', recursive=True))
            file_list = [f for f in file_list if os.path.isfile(f)]
            # juntos = [(f, getmtime(f)) for f in file_list]
            # print(juntos)
            if len(file_list) == 0:
                value = (path, getmtime(path))
            else:
                juntos = [(f, getmtime(f)) for f in file_list]
                value = max(juntos, key=lambda x: x[1])
        # print (value)
        return value

    # retorna se tem atualização e o arquivo mais recente
    @staticmethod
    def check_rebuild(source: str, target: str) -> Tuple[str, bool]:
        if not os.path.exists(target):
            return [source, True]
        [source_path, source_time] = Check.last_update(source)
        [target_path, target_time] = Check.last_update(target)
        # source tem novas alterações
        return (source_path, source_time > target_time)


class Remote:

    # processa o conteúdo trocando os links locais para links remotos utilizando a url remota
    @staticmethod
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

    @staticmethod
    def replace_remote(content: str, user: str, repo: str, path: str):
        remote_raw    = os.path.join("https://raw.githubusercontent.com", user, repo, "master" , path)
        remote_view    = os.path.join("https://github.com/", user, repo, "blob/master", path)
        remote_folder = os.path.join("https://github.com/", user, repo, "tree/master", path)
        return Remote.__replace_remote(content, remote_raw, remote_view, remote_folder)

    @staticmethod
    def run(user, repo, base, source_file, output_file):
        content = open(source_file).read()
        content = Remote.replace_remote(content, user, repo, base)
        open(output_file, "w").write(content)
        
        #print("    Remote Readme created for " + os.path.join(base, output_file))


class HookRemote:

    @staticmethod
    def insert_online_link(lines: List[str], online: str, tkodown: str) -> List[str]:

        text = "\n- Veja a versão online: [aqui.](" + online + ")\n"
        text += "- Para programar na sua máquina (local/virtual) use:\n"
        text += "  - `" + tkodown + "`\n"
        text += "- Se não tem o `tko`, instale pelo [LINK](https://github.com/senapk/tko#tko).\n\n---"

        lines.insert(1, text)

        return lines

    @staticmethod
    def run(source, target) -> bool:
        config = configparser.ConfigParser()

        cfg = "../../remote.cfg"

        if not os.path.isfile(cfg):
            print("no remote.cfg found")
            return False

        config.read(cfg)

        user = config["DEFAULT"]["user"]
        repo = config["DEFAULT"]["rep"]
        base = config["DEFAULT"]["base"]

        hook = os.path.basename(os.getcwd())
        remote = os.path.join(base, hook)
    
        lines = open(source).read().split("\n")
        # lines = replace_title(lines, hook)
        online_readme_link = os.path.join("https://github.com", user, repo, "blob/master", remote, "Readme.md")
        hook = remote.split("/")[-1]
        tkodown = "tko down " + user[6:] + " " + hook
        lines = HookRemote.insert_online_link(lines, online_readme_link, tkodown)
        open(target, "w").write("\n".join(lines))
        Remote.run(user, repo, remote, source, target)
        return True

class Title:
    @staticmethod
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

class HTML:

    @staticmethod
    def generate_html(input_file: str, output_file: str, enable_latex: bool):
        title = Title.extract_title(input_file)
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

# Format used to send additional files to VPL
class JsonFile:
    def __init__(self, name: str, contents: str):
        self.name: str = name
        self.contents: str = contents
        self.encoding: int = 0

    def __str__(self):
        return self.name + ":" + self.contents + ":" + str(self.encoding)

class JsonFileType(enum.Enum):
    UPLOAD = 1
    KEEP = 2
    REQUIRED = 3


class JsonVPL:
    def __init__(self, title: str, description: str):
        self.title: str = title
        self.description: str = description
        self.upload: List[JsonFile] = []
        self.keep: List[JsonFile] = []
        self.required: List[JsonFile] = []
        self.draft: Dict[str, List[JsonFile]] = {}

    def __add_file(self, ftype: JsonFileType, exec_file: str, rename=""):
        with open(exec_file) as f:
            file_name = rename if rename != "" else exec_file.split(os.sep)[-1]
            jfile = JsonFile(file_name, f.read())
            if ftype == JsonFileType.UPLOAD:
                self.upload.append(jfile)
            elif ftype == JsonFileType.KEEP:
                self.keep.append(jfile)
            else:
                self.required.append(jfile)
    
    def set_cases(self, exec_file: str):
        self.__add_file(JsonFileType.UPLOAD, exec_file, "vpl_evaluate.cases")
        return self

    def add_upload(self, exec_file: str, rename=""):
        self.__add_file(JsonFileType.UPLOAD, exec_file, rename)
        return self

    def add_keep(self, exec_file: str, rename=""):
        self.__add_file(JsonFileType.KEEP, exec_file, rename)
        return self

    def add_required(self, exec_file: str, rename=""):
        self.__add_file(JsonFileType.REQUIRED, exec_file, rename)
        return self
    
    def add_draft(self, extension: str, exec_file: str):
        if extension not in self.draft:
            self.draft[extension] = []
        with open(exec_file) as f:
            jfile = JsonFile(exec_file.split(os.sep)[-1], f.read())
            self.draft[extension].append(jfile)
        return self

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def load_config_json(self, cfg_json: str, source: str):
        if os.path.isfile(cfg_json):
            with open(cfg_json) as f:
                cfg = json.load(f)
                if "upload" in cfg:
                    for file in cfg["upload"]:
                        self.add_upload(norm_join(source, file))
                if "keep" in cfg:
                    for file in cfg["keep"]:
                        self.add_keep(norm_join(source, file))
                if "required" in cfg:
                    for file in cfg["required"]:
                        self.add_required(norm_join(source, file))
            return True
        return False
    
    def load_draft_tree(self, draft_tree: Dict[str, List[str]], cache_draft: str):
        if len(draft_tree) == 0:
            return False
        
        for ext in draft_tree:
            for file in draft_tree[ext]:
                self.add_draft(ext, norm_join(cache_draft, ext, file))
        return True

    def __str__(self):
        return self.to_json()

class Cases:

    @staticmethod
    def run(cases_file, source_readme, source_dir):
        # find all files in the directory terminatig with .tio or .vpl
        files = list(glob.iglob(source_dir + '/**', recursive=True))
        files = [f for f in files if os.path.isfile(f)]
        files = [f for f in files if f.endswith(".tio") or f.endswith(".vpl")]
        cmd = " ".join(["tko", "build", cases_file, source_readme] + files)
        output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

def norm_join(*args):
    return os.path.normpath(os.path.join(*args))

class Config:
    @staticmethod
    def load_into_vpl(cfg_json, vpl, source):
        if os.path.isfile(cfg_json):
            with open(cfg_json) as f:
                cfg = json.load(f)
                if "upload" in cfg:
                    for file in cfg["upload"]:
                        vpl.add_upload(norm_join(source, file))
                if "keep" in cfg:
                    for file in cfg["keep"]:
                        vpl.add_keep(norm_join(source, file))
                if "required" in cfg:
                    for file in cfg["required"]:
                        vpl.add_required(norm_join(source, file))
            return True
        return False
    

class Mode(enum.Enum):
    ADD = 1 # inserir cortando por degrau
    RAW = 2 # inserir tudo
    DEL = 3 # apagar tudo
    COM = 4 # inserir código removendo comentários

class Filter:
    def __init__(self, filename):
        self.mode = Mode.RAW
        self.backup_mode = Mode.RAW
        self.level = 1
        self.com = "//"
        if filename.endswith(".py"):
            self.com = "#"
    
    def init_raw(self):
        self.mode = Mode.RAW
        return self

    def init_del(self):
        self.mode = Mode.DEL
        return self

    # decide se a linha deve entrar no texto
    def evaluate_insert(self, line: str):
        if self.mode == Mode.DEL:
            return False
        if self.mode == Mode.RAW:
            return True
        if self.mode == Mode.COM:
            return True
        if line == "":
            return True
        margin = (self.level + 1) * "    "
        if line.startswith(margin):
            return False

        return True

    def process(self, content: str) -> str:
        lines = content.split("\n")
        output = []
        for line in lines:
            alone = len(line.split(" ")) == 1
            two_words = len(line.strip().split(" ")) == 2
            if self.mode == Mode.COM:
                if not line.strip().startswith(self.com):
                    self.mode = self.backup_mode
            if two_words and line.endswith("$$") and self.mode == Mode.ADD:
                self.backup_mode = self.mode
                self.mode = Mode.COM
            elif alone and line[-3:-1] == "++":
                self.mode = Mode.ADD
                self.level = int(line[-1])
            elif alone and line.endswith("=="):
                self.mode = Mode.RAW
            elif alone and line.endswith("--"):
                self.mode = Mode.DEL
            elif self.evaluate_insert(line):
                if self.mode == Mode.COM:
                    line = line.replace(self.com + " ", "", 1)
                output.append(line)
        return "\n".join(output)

class Tree:
    @staticmethod
    def deep_filter_copy(source, dict_tree, destiny, deep: int):
        if deep == 0:
            return
        if os.path.isdir(source):
            chain = source.split(os.sep)
            if len(chain) > 1 and chain[-1].startswith("."):
                return
            if not os.path.isdir(destiny):
                os.makedirs(destiny)
            for file in sorted(os.listdir(source)):
                Tree.deep_filter_copy(os.path.join(source, file), dict_tree, os.path.join(destiny, file), deep - 1)
        else:
            filename = os.path.basename(source)
            text_extensions = [".md", ".c", ".cpp", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".hs", ".txt"]
            pieces = source.split(os.sep)
            if len(pieces) >= 3:
                if pieces[-3] == "src":
                    if pieces[-2] not in dict_tree:
                        dict_tree[pieces[-2]] = []
                    dict_tree[pieces[-2]].append(pieces[-1])

            if not any([filename.endswith(ext) for ext in text_extensions]):
                return
            content = open(source, "r").read()
            processed = Filter(filename).process(content)
            with open(destiny, "w") as f:
                if processed != content:
                    Log.print("(filtered): ", end="")
                else:
                    Log.print("(        ): ", end="")
                f.write(processed)
                Log.print(destiny)

class Action:
    def __init__(self, source):
        self.cache = ".cache"
        self.target = norm_join(self.cache, "mapi.json")
        self.source = source
        self.hook = os.path.basename(os.getcwd())
        self.source_readme = norm_join(self.source, "Readme.md")
        self.remote_readme = norm_join(self.cache, "Readme.md")
        self.description = norm_join(self.cache, "q.html")
        self.title = Title.extract_title(self.source_readme)
        self.cases = norm_join(self.cache, "q.tio")
        self.config_json = norm_join(self.source, "config.json")
        self.mapi_json = norm_join(source, self.cache, "mapi.json")
        self.draft_tree = {}
        self.cache_src = "lang"
        self.vpl = None


    def create_cache(self):
        if not os.path.exists(self.cache):
            os.makedirs(self.cache)
        return self
    
    def check_rebuild(self):
        [_path, changes_found] = Check.check_rebuild(self.source, self.target)
        return changes_found
    
    def remote(self):
        HookRemote.run(self.source_readme, self.remote_readme)
        Log.write("RemoteMd ")
    
    def html(self):
        HTML.generate_html(self.remote_readme, self.description, True)
        Log.write("HTML ")

    def build_cases(self):
        Cases.run(self.cases, self.source_readme, self.source)
        Log.write("Cases ")

    def copy_drafts(self):
        src_folder = norm_join(self.source, "src")
        if os.path.isdir(src_folder):
            Tree.deep_filter_copy(src_folder, self.draft_tree, norm_join(self.source, self.cache, self.cache_src), 5)

    def run_local_sh(self):
        local_sh = norm_join(self.source, "local.sh")
        if os.path.isfile(local_sh):
            subprocess.run("bash " + local_sh, shell=True)

    def init_vpl(self):
        self.vpl = JsonVPL(self.title, open(self.source_readme).read())
        self.vpl.set_cases(self.cases)
        if self.vpl.load_config_json(self.config_json, self.source):
            Log.write("Required ")
        if self.vpl.load_draft_tree(self.draft_tree, norm_join(self.cache, self.cache_src)):
            Log.write("Drafts ")
        Log.write("] ")

    def create_mapi(self):
        open(self.mapi_json, "w").write(str(self.vpl) + "\n")
        Log.write("DONE")

    def clean(self):
        os.remove(self.cases)
        os.remove(self.description)

    # run mdpp script on source readme
    def update_markdown(self):
        subprocess.run("mdpp " + self.source_readme, shell=True)


def main():

    args = argparse.ArgumentParser()
    args.add_argument("--check", "-c", action="store_true", help="Check if the file needs to be rebuilt")
    args.add_argument("--verbose", "-v", action="store_true", help="Prints the output of the commands")
    args = args.parse_args()

    action = Action(".").create_cache()
    Log.verbose = args.verbose

    action.update_markdown()

    if args.check and not action.check_rebuild():
        return

    Log.write(action.hook, ": Changes found [ ")
    action.remote()
    action.html()
    action.build_cases()
    action.copy_drafts()
    action.run_local_sh()
    action.init_vpl()
    action.create_mapi()
    Log.write("\n")
    action.clean()



main()