#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import io
import argparse
import tempfile
import subprocess
from shutil import rmtree
from typing import Dict, List, Tuple, Union  # , Any, Callable
import configparser
from subprocess import run, PIPE


class Defaults:
    EMPTY = "__EMPTY__"
    SYMBOLS = {
        "category": ["cat:", "©"],
        "tag": ["#", "tag:"],
        "date": ["date:", "ð"],
        "author": ["author:", "æ"],
        "subtitle": ["sub:", "ß"]
    }


class Util:
    # join the many strings in the list using join
    @staticmethod
    def join(path_list: List[str]) -> str:
        path_list = [os.path.normpath(x) for x in path_list]
        path = ""
        for x in path_list:
            path = os.path.join(path, x)
        return os.path.normpath(path)

    @staticmethod
    def key_filter(key: str) -> str:
        key = key.replace("_", " ")
        words = key.split(" ")

        try:
            _index = int(words[0])
            del words[0]
        except:
            pass
        return " ".join(words).strip()

    # generate a relative path from source to destination
    @staticmethod
    def get_directions(source: str, destination: str) -> str:
        source = os.path.normpath(source)
        destination = os.path.normcase(destination)
        source_list = source.split(os.sep)
        destin_list = destination.split(os.sep)
        while source_list[0] == destin_list[0]:  # erasing commom path
            del source_list[0]
            del destin_list[0]

        return Util.join(["../" * (len(source_list) - 1)] + destin_list)

    # returns a tuple with two strings
    # the first  is the directory
    # the second is the filename
    @staticmethod
    def split_path(path: str) -> Tuple[str, str]:
        path = os.path.normpath(path)
        vet: List[str] = path.split(os.path.sep)
        if len(vet) == 1:
            return ".", path
        return Util.join(vet[0:-1]), vet[-1]

    @staticmethod
    def create_dirs_if_needed(path: str) -> None:
        root, file = Util.split_path(path)
        if not os.path.isdir(root):
            os.makedirs(root)

    # generate md link for the text
    @staticmethod
    def get_md_link(title: Union[None, str]) -> str:
        if title is None:
            return ""
        title = title.lstrip(" #").rstrip()
        title = title.lower()
        out = ''
        for c in title:
            if c == ' ' or c == '-':
                out += '-'
            elif c == '_':
                out += '_'
            elif c.isalnum():
                out += c
        return out

    @staticmethod
    def only_hashtags(x: str) -> bool:
        return len(x) == x.count("#") and len(x) > 0

    # return two lists
    # the first  with the words that        start with str p
    # the second with the words that do not start with char p
    @staticmethod
    def split_list(word_list: List[str], prefix: List[str]) -> Tuple[List[str], List[str]]:
        inside_list = []
        for p in prefix:
            inside_list += [x[(len(p)):] for x in word_list if x.startswith(p)]
            word_list = [x for x in word_list if not x.startswith(p)]
        return inside_list, word_list


class Config:
    @staticmethod
    def get_default_cfg():
        return ""

    @staticmethod
    def load_cfg(config_file):
        if not os.path.isfile(config_file):
            print("  fail: create a " + config_file + "like in https://github.com/senapk/indexer")
            exit(1)
        config = configparser.ConfigParser()
        config.read(config_file)
        return config


class Meta:
    def __init__(self, content: str = "", symbols: Dict[str, str] = None):
        if symbols is None:
            symbols = Defaults.SYMBOLS

        self.fulltitle = ""
        self.symbols = symbols
        self.md_level = Defaults.EMPTY
        self.title = ""
        self.subtitle = Defaults.EMPTY
        self.tags = []
        self.categories = []
        self.authors = []
        self.date = ""

        self.payload = ""
        self.cover = None

        self.parse_content(content)

    def parse_content(self, content: str):
        symbols = self.symbols
        lines = content.split('\n')

        self.payload = "" if len(lines) == 1 else "\n".join(lines[1:])
        self.cover = self.__get_cover()

        self.fulltitle = lines[0]
        words = self.fulltitle.split(" ")
        if Util.only_hashtags(words[0]):
            self.md_level = words[0]
            del words[0]

        words = [x for x in words if not Util.only_hashtags(x)]
        self.tags, words = Util.split_list(words, symbols["tag"])
        self.categories, words = Util.split_list(words, symbols["category"])
        self.authors, words = Util.split_list(words, symbols["author"])
        self.date, words = Util.split_list(words, symbols["date"])

        parts = []
        for symbol in symbols["subtitle"]:
            parts = " ".join(words).split(symbol)
            if len(parts) != 1:
                break

        self.title = parts[0].strip()
        self.subtitle = Defaults.EMPTY if len(parts) == 1 else parts[1].strip()

        self.date = Defaults.EMPTY if len(self.date) == 0 else self.date[0]

        if len(self.categories) == 0:
            self.categories.append(Defaults.EMPTY)
        if len(self.tags) == 0:
            self.tags.append(Defaults.EMPTY)
        if len(self.authors) == 0:
            self.authors.append(Defaults.EMPTY)

    def __get_cover(self):
        regex = r"!\[(.*?)\]\(([^:]*?)\)"
        match = re.search(regex, self.payload)
        if match:
            return os.path.normpath(match.group(2))  # cover.jpg
        return None

    def assemble(self, sequence="lTdctas"):
        symbols = self.symbols
        out = []

        for s in sequence:
            if s == 'T':
                if self.title:
                    out += [self.title]
            if s == 'l':
                if self.md_level != Defaults.EMPTY:
                    out += [self.md_level]
            if s == 'd':
                if self.date != Defaults.EMPTY:
                    out += [symbols["date"][0] + self.date]
            if s == 'c':
                for cat in self.categories:
                    if cat != Defaults.EMPTY:
                        out += [symbols["category"][0] + cat]
            if s == 's':
                if self.subtitle != Defaults.EMPTY:
                    out += [symbols['subtitle'][0] + " " + self.subtitle]
            if s == 't':
                for tag in self.tags:
                    if tag != Defaults.EMPTY:
                        out += [symbols["tag"][0] + tag]
            if s == 'a':
                for author in self.authors:
                    if author != Defaults.EMPTY:
                        out += [symbols["author"][0] + author]
        return " ".join(out)

    def meta_str(self):
        out = ("l[" + self.md_level + "] ") if self.md_level != Defaults.EMPTY else ""
        out += "T[" + self.title + "]"
        out += (" s[" + self.subtitle + "]") if self.subtitle != Defaults.EMPTY else ""
        out += (" c[" + ",".join(self.categories) + "]") if self.categories[0] != Defaults.EMPTY else ""
        out += (" t[" + ",".join(self.tags) + "]") if self.tags[0] != Defaults.EMPTY else ""
        out += (" a[" + ",".join(self.authors) + "]") if self.authors[0] != Defaults.EMPTY else ""
        out += (" d[" + self.date + "]") if self.date != Defaults.EMPTY else ""
        return out

    def __str__(self):
        return self.meta_str()


class Item(Meta):
    def __init__(self, path: str = "", content: str = "", symbols: Dict[str, str] = None):
        if symbols is None:
            symbols = Defaults.SYMBOLS
        Meta.__init__(self, content, symbols)
        self.path_full = os.path.normpath(path)  # arcade/base/000/Readme.md
        self.base = os.sep.join(self.path_full.split(os.sep)[:-2])  # arcade/base
        self.base = "." if self.base == "" else self.base
        self.hook = path.split(os.sep)[-2]  # 000
        self.filename = path.split(os.sep)[-1]  # Readme.md

    def check_cover(self):
        if not os.path.isfile(Util.join([self.base, self.hook, self.cover])):
            raise FileNotFoundError("  error: cover image not found in ", self.path_full)

    def __str__(self):
        return self.base + ":" + self.hook + ":" + self.filename


class ItemRepository:
    def __init__(self, base: str):
        self.base = os.path.normpath(base)
        self.__test_exists()
        self.itens: List[Item] = []

    def __test_exists(self):
        if not os.path.isdir(self.base):
            print("  error: base dir is missing")
            exit(1)

    def load(self):
        for (root, _dirs, files) in os.walk(self.base, topdown=True):
            folder = root.split(os.sep)[-1]
            if folder.startswith("_") or folder.startswith("."):
                continue
            if root.count(os.sep) - self.base.count(os.sep) != 1:  # one level only
                continue
            files = [x for x in files if x.endswith(".md")]
            for file in files:
                if file.startswith("_") or file.startswith(">"):
                    continue
                path = Util.join([root, file])
                self.itens.append(FileItem.load_from_file(path))
        return self.itens


class FileItem:
    @staticmethod
    def load_from_file(path: str) -> Item:
        with open(path, "r") as f:
            return Item(path, f.read())

    @staticmethod
    def write_from_item(item: Item):
        with open(item.path_full, "w") as f:
            f.write(item.fulltitle.strip() + "\n")
            f.write(item.payload)

    @staticmethod
    def has_changes(source: str, derivated: str):
        if not os.path.isfile(derivated):
            return True
        return os.path.getctime(source) > os.path.getctime(derivated)


class Sorter:
    @staticmethod
    def test_key(item: Item, key: str):
        if not hasattr(item, key):
            print("    fail: Item doesn't have the key", key)
            print("    The options are ", ["title", "hook", "categories/cat", "tags/tag", "authors", "date"])
            exit(1)

    @staticmethod
    def fix_key_name(key: str):
        key = key.lower()
        if key == "cat":
            return "categories"
        if key == "tag":
            return "tags"
        if key == "title":
            return "fulltitle"
        return key

    @staticmethod
    def normalize_keys(keys: str) -> Tuple[str, str]:
        keys_list = [x.strip() for x in keys.split(",")]
        if len(keys_list) == 1:
            keys_list.append("title")
        elif len(keys_list) > 2:
            keys_list = keys_list[:2]
        keys_list = [Sorter.fix_key_name(x) for x in keys_list]
        return keys_list[0], keys_list[1]

    @staticmethod
    def sorted_by_key(itens: List[Item], keys: str, reverse: bool = False) -> List[Item]:
        primary_key, secondary_key = Sorter.normalize_keys(keys)

        if len(itens) == 0:
            return []
        Sorter.test_key(itens[0], primary_key)
        Sorter.test_key(itens[0], secondary_key)

        if type(getattr(itens[0], primary_key)) is list:
            return sorted(itens, key=lambda x: (getattr(x, primary_key)[0], getattr(x, secondary_key)), reverse=reverse)
        return sorted(itens, key=lambda x: (getattr(x, primary_key), getattr(x, secondary_key)), reverse=reverse)

    @staticmethod
    def group_by(itens: List[Item], group_by: str, sort_by: str = "fulltitle", reverse_sort: bool = False) -> \
            List[Union[str, List[Item]]]:
        tree = {}
        if len(itens) > 0:
            group_by = Sorter.fix_key_name(group_by)
            Sorter.test_key(itens[0], group_by)
        for item in itens:
            data = getattr(item, group_by)
            if data is None:
                data = []
            elif not type(data) is list:
                data = [data]

            if len(data) == 0:
                if Defaults.EMPTY not in tree:
                    tree[Defaults.EMPTY] = []
                tree[Defaults.EMPTY].append(item)
            else:
                for elem in data:  # inserting the elem in all tags or categories
                    if elem not in tree:
                        tree[elem] = []
                    tree[elem].append(item)
        output: List[Union[str, List[Item]]] = []

        for key in tree.keys():  # sorting the lists
            sorted_list = Sorter.sorted_by_key(tree[key], sort_by)
            output.append([key, sorted_list])
        output.sort(key=lambda x: x[0], reverse=reverse_sort)  # sorting the keys
        return output


class Board:
    @staticmethod
    def make_entry(item: Item, board_file: str) -> Tuple[str, str]:
        return "[](" + Util.get_directions(board_file, item.path_full) + ')', item.fulltitle

    @staticmethod
    def extract_path_and_fulltitle(line: str, board_path: str):
        parts = line.split(":")
        file_path = parts[0].strip()[3:-1]  # removing []( )
        fulltitle = parts[1].strip()

        # change path relative to board to a path relative to base
        board_dir = Util.split_path(board_path)[0]
        path = Util.join([board_dir, file_path])
        return path, fulltitle

    @staticmethod
    def update_itens(itens: List[Item]):
        for item in itens:
            FileItem.write_from_item(item)

    @staticmethod
    def check_itens_for_update(board_content: str, board_path: str, itens: List[Item]):
        names_list = [x for x in board_content.split("\n") if x != ""]  # cleaning the empty lines
        itens_for_update = []
        for line in names_list:
            path, fulltitle = Board.extract_path_and_fulltitle(line, board_path)
            search = [item for item in itens if item.path_full == path]
            if len(search) == 0:
                print("  warning: file", path, "not found!")
            else:
                if search[0].fulltitle != fulltitle:
                    search[0].fulltitle = fulltitle
                    itens_for_update.append(search[0])
        return itens_for_update

    @staticmethod
    def generate(itens: List[Item], board_file: str, sort_by: str, reverse_sort: bool = False) -> str:
        sorted_list = Sorter.sorted_by_key(itens, sort_by, reverse_sort)
        # Util.create_dirs_if_needed(board_file)

        output = io.StringIO()
        for item in sorted_list:
            path, fulltitle = Board.make_entry(item, board_file)
            output.write(path + " : " + fulltitle + "\n")

        return output.getvalue()


class IndexConfig:
    def __init__(self, cfg_index):
        self.path        =           cfg_index["path"]
        self.sort_by      =          cfg_index["sort_by"]
        self.group_by     =          cfg_index["group_by"]
        self.insert_toc   = bool(int(cfg_index["insert_toc"]))
        self.insert_hook  = bool(int(cfg_index["insert_hook"]))
        self.reverse_sort = bool(int(cfg_index["reverse_sort"]))
        self.key_filter   = bool(int(cfg_index["key_filter"]))


class Index:
    @staticmethod
    # bool: generate_indices
    # bool: parse key to 01_Titulo_Coisado -> Titulo Coisado
    # bool: add hook
    def generate(itens: List[Item], param: IndexConfig) -> str:
        groups = Sorter.group_by(itens, param.group_by, param.sort_by, param.reverse_sort)
        output = io.StringIO()
        output.write("\n## Links\n")

        # gerando indices
        if param.insert_toc:
            for key, _item_list in groups:
                key = Util.key_filter(key) if param.key_filter else key
                link = Util.get_md_link(key)
                output.write("- [" + key + "](#" + link + ")\n")

        for key, item_list in groups:
            key = Util.key_filter(key) if param.key_filter else key
            output.write("\n## " + key + "\n\n")
            for item in item_list:
                item_path = item.path_full + "#" + Util.get_md_link(item.fulltitle)
                prefix = ("@" + item.hook + " ") if param.insert_hook else ""
                entry = "- [" + prefix + item.title.strip() + "](" + Util.get_directions(param.path, item_path) + ")\n"
                output.write(entry)
        return output.getvalue()


class Links:
    @staticmethod
    def generate(itens: List[Item], links_dir: str):
        rmtree(links_dir, ignore_errors=True)
        os.mkdir(links_dir)
        for item in itens:
            path = os.path.join(links_dir, item.title.strip() + ".md")
            with open(path, "w") as f:
                link = Util.get_directions(path, item.path_full)
                f.write("[LINK](" + link + ")\n")


class HTML:

    """
    generate a html page from infile
    if remote_server not null, all reference to images begining with __
    will be updates to full url
    """
    @staticmethod
    def _generate_html(title: str, content: str, enable_latex: bool) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        outfile = os.path.join(temp_dir.name, "out.html")
        infile = os.path.join(temp_dir.name, "in.md")
        with open(infile, "w") as f:
            f.write(content)

        fulltitle = title.replace('!', '\\!').replace('?', '\\?')
        cmd = ["pandoc", infile, '--metadata', 'pagetitle=' + fulltitle, '-s', '-o', outfile]
        if enable_latex:
            cmd.append("--mathjax")
        try:
            p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            stdout, stderr = p.communicate()
            if stdout != "" or stderr != "":
                print(stdout)
                print(stderr)
            with open(outfile) as f:
                return f.read()
        except Exception as e:
            print("Erro no comando pandoc:", e)
            exit(1)

    @staticmethod
    def _insert_remote_url(content: str, remote_url: str) -> str:
        regex = r"\[(.*)\]\((\s*)([^:\s]*)(\s*)\)"
        subst = "[\\1](" + remote_url + "\\3)"
        result = re.sub(regex, subst, content, 0, re.MULTILINE)
        return result

    @staticmethod
    def generate(itens: List[Item], insert_hook: bool, enable_latex: bool, remote_base_url: str, rebuild_all: bool):
        for item in itens:
            hook = ("@" + item.hook) if insert_hook else ""

            payload = item.payload
            if remote_base_url != "":
                remote_hook = remote_base_url.rstrip("/") + "/" + item.hook + "/"
                payload = HTML._insert_remote_url(payload, remote_hook)

            md_content = "## " + hook + "\n" + item.fulltitle + "\n" + payload
            title = " ".join([hook, item.title])

            output_file = Util.join([item.base, item.hook, ".html"])

            if FileItem.has_changes(item.path_full, output_file) or rebuild_all:
                print("  regenerating html for hook", item.hook)
                html_content = HTML._generate_html(title, md_content, enable_latex)
                with open(output_file, "w") as f:
                    f.write(html_content)


class VPL:
    @staticmethod
    def _generate_cases(infiles: List[str], outfile):
        cmd = ["th", "build", outfile]
        for infile in infiles:
            if os.path.isfile(infile):
                cmd.append(infile)
        # cmd.append("-q")
        try:
            p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            stdout, stderr = p.communicate()
            if stdout != "" or stderr != "":
                print(stdout)
                print(stderr)
        except Exception as e:
            print("Erro no comando th:", e)
            exit(1)

    @staticmethod
    def generate(itens: List[Item], rebuild_all: bool):
        for item in itens:
            output_file = Util.join([item.base, item.hook, ".vpl"])
            extra_tests = Util.join([item.base, item.hook, "t.tio"])

            to_rebuild = False
            to_rebuild = to_rebuild or FileItem.has_changes(item.path_full, output_file)
            if os.path.isfile(extra_tests):
                to_rebuild = to_rebuild or FileItem.has_changes(extra_tests, output_file)
            if to_rebuild or rebuild_all:
                print("  regenerating .vpl for hook", item.hook)
                input_files = [item.path_full, extra_tests]
                VPL._generate_cases(input_files, output_file)


def main():
    parser = argparse.ArgumentParser(prog='indexer.py')
    parser.add_argument('-b', action='store_true', help='rebuild headers using board')
    parser.add_argument('-r', action='store_true', help='rebuild all')
    # parser.add_argument('--init', action='store_true', help='init default .config.ini')
    args = parser.parse_args()

    #    if args.init:
    #        f = open(".indexer.json", "w")
    #        print("Creating .indexer.json file")
    #        f.write(json.dumps(Config.getDefault(), indent=2))
    #        f.close()
    #        exit(0)

    def to_bool(x: str) -> bool:
        return bool(int(x))

    cfg = configparser.ConfigParser()
    if os.path.isfile(".config.ini"):
        cfg.read(".config.ini")
    else:
        print("  fail: config file not found")
        exit(1)

    base_path = cfg["base"]["dir"]

    itens = ItemRepository(base_path).load()

    if cfg["board"]["enabled"] == '1':
        param = cfg["board"]
        if args.b:
            print("Updating names using board")
            with open(param["path"]) as f:
                marked = Board.check_itens_for_update(f.read(), param["path"], itens)
                Board.update_itens(marked)
            itens = ItemRepository(base_path).load()

        print("Generating board")
        board = Board.generate(itens, param["path"], param["sort_by"], to_bool(param["reverse_sort"]))
        with open(param["path"], "w") as f:
            f.write(board)

    if cfg["links"]["enabled"] == '1':
        param = cfg["links"]
        print("Generating links")
        Links.generate(itens, param["dir"])

    print("Generating index")
    index_param = IndexConfig(cfg["index"])
    index = Index.generate(itens, index_param)
    with open(index_param.path, "w") as f:
        f.write(index)

    itens = sorted(itens, key=lambda x: x.hook) # ordenando para os geradores

    if cfg["html"]["enabled"] == '1':
        param = cfg["html"]
        print("Generating htmls")
        HTML.generate(itens, to_bool(param["insert_hook"]), to_bool(param["latex"]), param["remote"], args.r)

    if cfg["vpl"]["enabled"] == '1':
        print("Generating vpls")
        VPL.generate(itens, args.r)


if __name__ == '__main__':
    main()
