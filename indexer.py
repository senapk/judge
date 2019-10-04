#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import argparse
import re
import subprocess
import csv
import io
from typing import List
from shutil import rmtree


class util:

    @staticmethod
    def join(path_list):
        if None in path_list:
            return None
        path_list = [os.path.normpath(x) for x in path_list]
        path = ""
        for x in path_list:
            path = os.path.join(path, x)
        return os.path.normpath(path)

    @staticmethod
    def normpath(file):
        if file is None:
            return None
        return os.path.normpath(file)

    @staticmethod
    def extract_title_content(line):
        if line == None or len(line) == 0:
            return ""
        if line[-1] == "\n":
            line = line[:-1]
        words = line.split(" ")
        if util.only_hashtags(words[0]):
            return " ".join(words[1:])
        return " ".join(words)

    @staticmethod
    def get_directions(source, destination):
        if source == '.' or source == './':
            return destination
        return util.join(["../" * (len(source.split(os.sep)) - 1), destination])

    @staticmethod
    def split_path(path):
        path = util.normpath(path)
        vet = path.split(os.path.sep)
        if len(vet) == 1:
            return ".", path
        return os.sep.join(vet[0:-1]), vet[-1]

    @staticmethod
    def create_dirs_if_needed(path):
        root, file = util.split_path(path)
        if not os.path.isdir(root):
            os.makedirs(root)

    @staticmethod
    def get_md_link(title):
        if title is None:
            return ""
        title = util.extract_title_content(title)
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
    def only_hashtags(x): return len(x) == x.count("#")

    @staticmethod
    def split_list(l, p): return [x[1:] for x in l if x.startswith(p)], [x for x in l if not x.startswith(p)]

    @staticmethod
    def get_first(info_list): return info_list[0] if len(info_list) > 0 else None


class Config:
    @staticmethod
    def get_default_cfg():
        cfg = {
            "base": "base",
            "execute": [
                {
                    "action": "run",
                    "cmds": [
                        ["cmd", "arg", "arg"],
                        ["cmd", "arg", "arg"]
                    ]
                },
                {
                    "action": "load_folder", 
                },
                {
                    "action": "board", 
                    "file": ".indexer/board.md"
                },
                {
                    "action": "links",
                    "dir": ".indexer/links"
                },
                {
                    "action": "thumbs", 
                    "width": 320,
                    "height": 180
                },
                {
                    "action": "index", 
                    "intro": None,
                    "file": ".indexer/cat_index.md",
                    "sorting": {
                        "orphan": "No category",
                        "group_by": "category",
                        "sort_by": "fulltitle",
                        "reverse_sort": False
                    }
                },
                {
                    "action": "view", 
                    "intro": None,
                    "file": ".indexer/cat_view.md",
                    "sorting": {
                        "orphan": "No category",
                        "group_by": "category",
                        "sort_by": "fulltitle",
                        "reverse_sort": False
                    },
                    "viewing": {
                        "posts_per_row": 3,
                        "empty_fig": None
                    }
                },
                {
                    "action": "posts",
                    "dir": "_posts",
                    "base_raw_remote": "https://raw.githubusercontent.com/senapk/senapk.github.io/master/base",
                    "default_date": "1984-04-25"
                }
            ]
        }
        return cfg

    @staticmethod
    def get_default_symbols():
        symbols = {
            "tag": "#",
            "category": "\u00a9",
            "date": "\u00f0",
            "author": "\u00e6"
        }
        return symbols

    @staticmethod
    def get_default_sorting():
        return {"orphan": "orphan", "group_by": "category", "sort_by": "fulltitle", "reverse_sort": False}

    @staticmethod
    def get_default_viewing():
        return {"empty_fig": None, "posts_per_row": 3}

    @staticmethod
    def load_cfg(config_file):
        if not os.path.isfile(config_file):
            print("  fail: create a " + config_file + "like in https://github.com/senapk/indexer")
            exit(1)
        with open(config_file, "r") as f:
            cfg = json.load(f)
            cfg["base"] = util.normpath(cfg["base"])
            keys = [x for x in Config.get_default_cfg().keys()]
            Config.check_keys(cfg, keys)
            return cfg
        
    @staticmethod
    def load_symbols(symbols_file):
        if not os.path.isfile(symbols_file):
            print("  warning: .symbols.json not found in", symbols_file, ", loading default value and creating file")
            symbols = Config.get_default_symbols()
            with open(symbols_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(symbols, indent=2))
            return symbols

        with open(symbols_file, "r") as f:
            symbols = json.load(f)
            print("Loading symbols")
            keys = [x for x in Config.get_default_symbols().keys()]
            Config.check_keys(symbols, keys)
            return symbols

    @staticmethod
    def check_keys(received, needed, optional = []):
        for opt in received:
            all_keys = needed + optional
            if opt not in all_keys:
                print("  error: config doesn't have the key:", opt)
                print("         the options are", str(all_keys))
                exit(1)
        for opt in needed:
            if opt not in received:
                print("  error: config requires the key:", opt)
                print("         the options required are", str(needed))
                exit(1)


class Category:
    def __init__(self, index = 0, qtd=0, name="", label="", description=""):
        self.index = index
        self.qtd = qtd
        self.name = name
        self.label = label
        self.description = description

    def get_entry(self):
        return str(self.qtd) + "," + self.name + "," + self.label + "," + self.description

    def __lt__(self, other):
        return self.index < other.index

    def __str__(self):
        return self.label


class Item:

    fulltitle: str

    @staticmethod
    def normalize_file(readme_path):
        with open(readme_path, "r") as f:
            lines = f.readlines()
            fulltext = "".join(lines)

        if len(lines) == 0:
            print("  warning: filling empty on ", readme_path)
            lines.append("# Empty #empty\n")
            lines.append("\n")

        if len(lines) == 1:
            lines.append("\n")

        for i in range(len(lines)):
            if lines[i] == "" or lines[i][-1] != "\n":
                lines[i] = lines[i] + "\n"

        if fulltext != "".join(lines):
            with open(readme_path, "w") as f:
                f.write("".join(lines))

        return lines[0][:-1], lines[1][:-1], "".join(lines[2:])

    def __init__(self, symbols, path):
        crude_title, self.description, self.content = Item.normalize_file(path)
        self.__parse_title(symbols, crude_title)
        self.path_full = util.normpath(path)                               # arcade/base/000/Readme.md
        self.base = os.sep.join(self.path_full.split(os.sep)[:-2])         # arcade/base
        self.hook = path.split(os.sep)[-2]                                 # 000
        self.filename = path.split(os.sep)[-1]                             # Readme.md
        self.cover = self.__get_cover()                                    # cover.jpg ou ../001/cover.jpg
        self.fulltitle = self.__sort_fulltitle(symbols)                    # first line content withoub the \n
        self.category = Category()
        if crude_title != self.fulltitle:
            with open(path, "w") as f:
                f.write(self.fulltitle + "\n" + self.content)

    def __parse_title(self, symbols, first_line):
        words = first_line.split(" ")
        self.level = None
        if util.only_hashtags(words[0]):
            self.level = words[0]
            del words[0]
        words = [x for x in words if not util.only_hashtags(x)]
        self.tags, words = util.split_list(words, symbols["tag"])
        self.category_id, words = util.split_list(words, symbols["category"])
        self.date, words = util.split_list(words, symbols["date"])
        self.author, words = util.split_list(words, symbols["author"])
        self.title = " ".join(words).strip() if len(words) > 0 else ''
        self.category_id = util.get_first(self.category_id)
        self.date = util.get_first(self.date)
        self.author = util.get_first(self.author)

    def __get_cover(self):
        regex = r"!\[(.*?)\]\(([^:]*?)\)"
        match = re.search(regex, self.content)
        if match:
            img = os.path.normpath(match.group(2))  # cover.jpg
            if not os.path.isfile(util.join([self.base, self.hook, img])):
                print("  error: cover image not found in ", self.path_full)
                exit(1)
            return img
        return None

    def __sort_fulltitle(self, symbols):
        out = []
        if self.level:
            out += [self.level]
        if self.date:
            out += [symbols["date"] + self.date]
        if self.category_id:
            out += [symbols["category"] + self.category_id]
        if self.title:
            out += [self.title]
        for tag in self.tags:
            out += [symbols["tag"] + tag]
        if self.author:
            out += [symbols["author"] + self.author]
        return " ".join(out)

    def __str__(self):
        out = "@" + str(self.hook) + " "
        out += "[title: " + str(self.title) + "]"
        if self.category_id:
            out += "[cat: " + self.category_id + "]"
        if self.date:
            out += "[date: " + self.date + "]"
        if len(self.tags) > 0:
            out += "[tags: " + ", ".join(self.tags) + "]"
        if self.author:
            out += "[author: " + self.author + "]"
        return out


class Folder:
    @staticmethod
    def get_categories_file_path(base):
        return util.join([base, ".categories.csv"])

    @staticmethod
    def get_symbols_file_path(base):
        return util.join([base, ".symbols.json"])

    @staticmethod
    def load(base):        
        base = os.path.normpath(base)
        if not os.path.isdir(base):
            print("  error: base dir is missing")
            exit(1)

        symbols = Config.load_symbols(Folder.get_symbols_file_path(base))
        itens = Folder.load_itens(base, symbols)
        cat_dict = Folder.load_categories_file(base)
        Folder.merge_categories(itens, cat_dict)
        Folder.save_categories_on_file(cat_dict, base)
        Folder.set_categories_on_itens(itens, cat_dict)
        return itens

    @staticmethod
    def load_itens(base, symbols):
        itens = []
        for (root, dirs, files) in os.walk(base, topdown=True):
            folder = root.split(os.sep)[-1]
            if folder.startswith("__") or folder.startswith("."):
                continue
            if root.count(os.sep) - base.count(os.sep) != 1:  # one level only
                continue
            files = [x for x in files if x.endswith(".md")]
            for file in files:
                path = util.join([root, file])
                itens.append(Item(symbols, path))
        return itens

    @staticmethod
    def load_categories_file(base):
        categories_file = Folder.get_categories_file_path(base)
        print("Loading categories")
        cat_dict = {}
        if os.path.isfile(categories_file):
            with open(categories_file, 'r') as f:
                spamreader = csv.reader(f, delimiter=',', quotechar='"', skipinitialspace=True)
                index = 0
                for row in spamreader:
                    qtd, cat, label, description = row
                    if cat not in cat_dict:
                        cat_dict[cat] = Category(index, int(qtd), cat, label, description)
                        index += 1
        return cat_dict

    @staticmethod
    def merge_categories(itens, cat_dict):
        sorting = Config.get_default_sorting()
        sorting["group_by"] = "category_id"
        tree = Tree.generate(itens, sorting)
        for key in cat_dict:
            cat_dict[key].qtd = 0
        for key in tree.keys():
            qtd = len(tree[key])
            if qtd == 0:
                continue
            if key not in cat_dict:
                cat_dict[key] = Category(1000, qtd, key, key, "")
            else:
                cat_dict[key].qtd = qtd

    @staticmethod
    def save_categories_on_file(cat_dict, base):
        categories_file = Folder.get_categories_file_path(base)
        with open(categories_file, "w") as out:
            write = csv.writer(out, delimiter=',', quotechar='"')
            for x in sorted(cat_dict.values()):  # ordena pelo nome da categoria
                write.writerow([x.qtd, x.name, x.label, x.description])

    @staticmethod
    def set_categories_on_itens(itens, cat_dict):
        for item in itens:
            item.category = cat_dict[item.category_id]


class Board:
    @staticmethod
    def get_entry(item, board_file):
        return "[](" + util.get_directions(board_file, item.path_full) + ')', item.fulltitle, item.description

    @staticmethod
    def update_titles(board_file):
        f = open(board_file, "r")
        names_list = [x for x in f.readlines() if x != "\n"]
        f.close()
        for line in names_list:
            parts = line.split(":")
            path = parts[0].strip()[6:-1]
            fulltitle = parts[1].strip()
            description = parts[2].strip()

            if not os.path.isfile(path):
                util.create_dirs_if_needed(path)
                print("  warning: file", path, "not found, creating!")
                with open(path, "w") as f:
                    f.write(fulltitle + " #empty\n")
            else:
                with open(path, "r") as f:  # updating first line content
                    data = f.readlines()
                old_first_line = data[0]
                new_first_line = fulltitle + "\n"
                old_description = data[1]
                new_description = description + "\n"
                if old_first_line != new_first_line or old_description != new_description:
                    with open(path, "w") as f:
                        f.write(new_first_line + new_description +  "".join(data[2:]))

    @staticmethod
    def generate(itens: List[Item], board_file):
        if board_file is None:
            return
        itens.sort(key=lambda item: item.category.index)
        paths = []
        fulltitles = []
        subtitles = []
        max_len_path = 0
        max_len_title = 0
        for x in itens:
            path, fulltitle, subtitle = Board.get_entry(x, board_file)
            if len(path) > max_len_path:
                max_len_path = len(path)
            if len(fulltitle) > max_len_title:
                max_len_title = len(fulltitle)
            paths.append(path)
            fulltitles.append(fulltitle)
            subtitles.append(subtitle if subtitle is not None else "")
        paths = [x.ljust(max_len_path) for x in paths]
        fulltitles = [x.ljust(max_len_title) for x in fulltitles]
        util.create_dirs_if_needed(board_file)
        with open(board_file, "w") as names:
            for i in range(len(paths)):
                names.write(paths[i] + " : " + fulltitles[i] + " : " + subtitles[i] + "\n")

class Links:
    @staticmethod
    def generate(itens, links_dir):
        if os.path.isdir(links_dir):
            rmtree(links_dir, ignore_errors=True)
        if not os.path.isdir(links_dir):
            os.makedirs(links_dir)
        for item in itens:
            path = util.join([links_dir, item.title.strip() + ".md"])
            with open(path, "w") as f:
                f.write("[LINK](" + util.get_directions(path, item.path_full) + ")\n")


class Tree:
    @staticmethod
    def generate(itens, sorting):
        if sorting is None:
            sorting = Config.get_default_sorting()
        orphan = sorting["orphan"]
        reverse_sort = sorting["reverse_sort"]
        sort_by = sorting["sort_by"]
        group_by = sorting["group_by"]
        tree = {}

        for item in itens:
            data = getattr(item, group_by)
            if data is None:
                data = []
            elif not type(data) is list:
                data = [data]

            if len(data) == 0:
                if orphan not in tree:
                    tree[orphan] = []
                tree[orphan].append(item)
            else:
                for elem in data:
                    if elem not in tree:
                        tree[elem] = []
                    tree[elem].append(item)
        if sort_by:
            for key in tree:
                tree[key].sort(key=lambda x: getattr(x, sort_by), reverse=reverse_sort)
        return tree


class Index:
    @staticmethod
    def generate(tree, out_file):
        if out_file is None:
            return
        readme_text = io.StringIO()
        for key in sorted(tree.keys()):
            item_list = tree[key]
            readme_text.write("\n## " + str(key) + "\n\n")
            for item in item_list:
                item_path = item.path_full + "#" + util.get_md_link(item.fulltitle)
                entry = "- [" + item.title.strip() + "](" + util.get_directions(out_file, item_path) + ")\n"
                readme_text.write(entry)
        util.create_dirs_if_needed(out_file)
        with open(out_file, "a") as f:
            f.write(readme_text.getvalue())


class Summary:
    @staticmethod
    def generate(tree, out_file):
        if out_file is None:
            return
        summary = io.StringIO()
        for key in sorted(tree.keys()):
            item_list = tree[key]
            summary.write("\n## " + key + "\n")
            for item in item_list:
                summary.write(item.hook + " ")
            summary.write("\n\n")
        
        util.create_dirs_if_needed(out_file)
        with open(out_file, "a") as f:
            f.write(summary.getvalue())
        summary.close()


class View:
    @staticmethod
    def __make_row(data):
        a = "|".join([x[0] for x in data]) + "\n"
        b = "|".join(["-"] * len(data)) + "\n"
        c = "|".join([x[1] for x in data]) + "\n\n\n"
        return a, b, c

    @staticmethod
    def __make_table_entry(item_list, out_file, empty_fig, posts_per_row):
        data = []
        for item in item_list:
            thumb = Thumbs.get_thumb_full(item)
            if thumb:
                thumb = util.get_directions(out_file, thumb)
            else:
                if empty_fig:
                    thumb = util.get_directions(out_file, empty_fig)
                else:
                    thumb = "https://placekitten.com/320/181"
            file_path = util.get_directions(out_file, item.path_full + "#" + util.get_md_link(item.fulltitle))
            entry = "[![](" + thumb + ")](" + file_path + ")"
            if item.date:
                data.append([entry, "@" + item.date + "<br>" + item.title])
            else:
                data.append([entry, "@" + item.hook + "<br>" + item.title])
        
        while len(data) % posts_per_row != 0:
            if empty_fig:
                data.append(["![](" + empty_fig + ")", " "])
            else:
                data.append(["-", "*"])
        
        lines = []
        for i in range(0, len(data), posts_per_row):
            a, b, c = View.__make_row(data[i: i + posts_per_row])
            lines += [a, b, c]
        return "".join(lines)

    @staticmethod
    def generate(tree, out_file, viewing):
        if out_file is None:
            return
        empty_fig = viewing["empty_fig"]
        posts_per_row = viewing["posts_per_row"]
        view_text = io.StringIO()

        for key in sorted(tree.keys()):
            item_list = tree[key]
            view_text.write("\n## " + str(key) + "\n\n")
            text = View.__make_table_entry(item_list, out_file, empty_fig, posts_per_row)
            view_text.write(text)
    
        util.create_dirs_if_needed(out_file)
        with open(out_file, "a") as f:
            f.write(view_text.getvalue())
        view_text.close()


class Thumbs:
    @staticmethod
    def generate(itens, width, height):
        itens.sort(key=lambda x: x.hook)
        for item in itens:
            Thumbs.make(item, width, height)

    # return .thumb/hook/Readme.jpg
    @staticmethod
    def get_thumb(item):
        if item.cover:
            return util.join([".thumb", item.hook, item.filename[:-2] + "jpg"])
        return None

    # return "arcade/base/.thumb/hook/Readme.jpg"
    @staticmethod
    def get_thumb_full(item):
        if item.cover:
            return util.join([item.base, Thumbs.get_thumb(item)])
        return None

    @staticmethod
    def make(item, width, height):
        thumb_full = Thumbs.get_thumb_full(item)
        if thumb_full is None:
            print("  warning: thumb skipping, missing cover on", item.path_full)
            return
        cover_full = util.join([item.base, item.hook, item.cover])
        util.create_dirs_if_needed(thumb_full)
        if not os.path.isfile(thumb_full) or os.path.getmtime(cover_full) > os.path.getmtime(thumb_full):
            print("  making thumb for", item.path_full)
            cmd = ['convert', cover_full, '-resize', str(width) + 'x' + str(height) + '>', thumb_full]
            subprocess.run(cmd)


class Posts:
    @staticmethod
    def write_post(item, posts_dir, default_date, remote):
        if item.date is None and default_date is None:
             print("  warning: Date missing, using on", item.path_full, ", skipping")
             return
        if item.date is None:
            item.date = default_date
        if item.cover is None:
            print("  warning: Cover missing, skip", item.path_full)
            return
        if remote[-1] == "/":
            remote = remote[:-1]
        out = io.StringIO()
        out.write("---\nlayout: post\n")
        out.write("title: " + item.title + '\n')
        out.write("image: " + remote + "/" + item.hook + "/" + item.cover + "\n")
        out.write("optimized_image: " + remote + "/" + Thumbs.get_thumb(item) + "\n")
        if item.description:
            description = util.extract_title_content(item.description)
            out.write("subtitle: " + description + "\n")
            out.write("description: " + description + "\n")
        if item.category:
            out.write("category: " + item.category.name + "\n")
        if len(item.tags) > 0:
            out.write("tags:\n")
            for t in item.tags:
                out.write("  - " + t + "\n")
        if item.author:
            out.write("author: " + item.author + "\n")
        out.write("---\n")
        warning_msg = "<!-- DON'T EDIT THIS FILE, GENERATED BY SCRIPT -->\n" * 5
        out.write(warning_msg)
        out.write(item.content)
        out.write(Posts.get_tests_link(item))
        text = out.getvalue()

        regex = r"\[(.*?)\]\(([^:]*?)\)"
        text = re.sub("!" + regex, "", text, 1, re.MULTILINE)  # removing cover
        subst = "[\\1](" + remote + "/" + item.hook + "/" + "\\2)"
        text = re.sub(regex, subst, text, 0, re.MULTILINE)  # creating full url for links

        name = "%s-c%02d-%s-%s" % (item.date, item.category.index, item.category.name, item.title)
        name = util.get_md_link(name) + "-@" + item.hook + ".md"
        while "--" in name:
            name = name.replace("--", "-")
        with open(posts_dir + os.sep + name, "w") as f:
            f.write(text)

    @staticmethod
    def get_tests_link(item):
        out = io.StringIO()
        out.write("\n## Tests\n")
        test_path = util.join([item.base, item.hook, "t.tio"])
        if os.path.isfile(test_path):
            out.write("[DONWLOAD](t.tio)\n\n")
            return out.getvalue()
        return ""


    @staticmethod 
    def find_old_posts(item, posts_dir):
        files = os.listdir(posts_dir)
        files = [util.join([posts_dir, x]) for x in files]
        files = [x for x in files if os.path.isfile(x)]
        files = [x for x in files if x.endswith("-@" + item.hook + ".md")]
        return files


    # return if content is new
    @staticmethod
    def is_new_content(item, posts_dir, rebuild_all):
        files = Posts.find_old_posts(item, posts_dir)
        if len(files) == 0:
            return True
        is_new = False
        for file in files:
            if rebuild_all or os.path.getmtime(item.path_full) > os.path.getmtime(file):
                print("  replacing post", file)
                os.remove(file)
                is_new = True
        return is_new

    @staticmethod
    def generate(base, itens, posts_dir, default_date, remote, categories_dir, rebuild_all):
        for item in itens:
            Posts.is_new_content(item, posts_dir, rebuild_all)
            Posts.write_post(item, posts_dir, default_date, remote)
        Posts.generate_categories_files(base, categories_dir)

    @staticmethod
    def generate_categories_files(base, categories_dir):
        categories_dir = os.path.normpath(categories_dir)
        rmtree(categories_dir, ignore_errors=True)
        os.mkdir(categories_dir)
        cat_dict = Folder.load_categories_file(base)
        for key in cat_dict:
            cat = cat_dict[key]
            if cat.qtd > 0:
                with open(util.join([categories_dir, cat.name + ".md"]), "w") as f:
                    f.write("---\n")
                    f.write("layout: category\n")
                    f.write("title: " + cat.label + "\n")
                    f.write("slug: " + cat.name + "\n")
                    f.write("description: " + cat.description + "\n")
                    f.write("---\n")


class Main:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(prog='indexer.py')
        parser.add_argument('-b', action='store', help='set titles using board')
        parser.add_argument('-r', action='store_true', help='rebuild all')
        parser.add_argument('--init', action='store_true', help='show .indexer.json default')
        args = parser.parse_args()
        return args

    @staticmethod
    def init():
        f = open(".indexer.json", "w")
        print("Creating .indexer.json file")
        f.write(json.dumps(Config.get_default_cfg(), indent=2))
        f.close()
        exit(0)

    @staticmethod
    def update_from_board(board):
        if board:
            print("Updating names using board")
            Board.update_titles(board)

    @staticmethod
    def load_intro(intro, out_file):
        intro = os.path.normpath(intro)
        out_file = os.path.normpath(out_file)
        if intro:
            with open(intro, "r") as f:
                intro = f.read()
            with open(out_file, "w") as f:
                f.write(intro)
        else:
            if os.path.isfile(out_file):
                os.remove(out_file)

    @staticmethod
    def execute_actions(base, options, itens, rebuild_all):
        action = options["action"]
        actions = ["load_folder", "board", "run", "thumbs", "links", "index", "view", "summary", "posts"]
        if action not in actions:
            print("  error: action", options["action"], "not found")
            print("  you need choose one of this actions:")
            print("  " + str(actions))

        if action == "load_folder":
            print("Loading folder")
            Config.check_keys(options, ["action"])
            itens = Folder.load(base)
        
        elif action == "board":
            print("Generating board")
            Config.check_keys(options, ["action", "file"])
            Board.generate(itens, options["file"])

        elif action == "run":
            print("Running Scripts")
            Config.check_keys(options, ["action", "cmds"])
            Main.run_scripts(options["cmds"])

        elif action == "thumbs":
            print("Generating thumbs")
            Config.check_keys(options, ["action", "width", "height"])
            Thumbs.generate(itens, options["width"], options["height"])

        elif action == "links":
            print("Generating links")
            Config.check_keys(options, ["action", "dir"])
            Links.generate(itens, options["dir"])

        elif action == "index":
            print("Generating index")
            Main.load_intro(options["intro"], options["file"])
            Config.check_keys(options, ["action", "intro", "file", "sorting"])
            Index.generate(Tree.generate(itens, options["sorting"]), options["file"])

        elif action == "view":
            print("Generating photo board")
            Main.load_intro(options["intro"], options["file"])
            Config.check_keys(options, ["action", "intro", "file", "sorting", "viewing"])
            View.generate(Tree.generate(itens, options["sorting"]), options["file"], options["viewing"])

        elif action == "summary":
            print("Generating summary")
            Main.load_intro(options["intro"], options["file"])
            Config.check_keys(options, ["action", "intro", "file", "sorting"])
            Summary.generate(Tree.generate(itens, options["sorting"]), options["path"])

        elif action == "posts":
            print("Generating posts")
            Config.check_keys(options, ["action", "dir", "default_date", "base_raw_remote", "categories_dir"])
            posts_dir = options["dir"]
            date = options["default_date"]
            remote = options["base_raw_remote"]
            categories_dir = options["categories_dir"]
            Posts.generate(base, itens, posts_dir, date, remote, categories_dir, rebuild_all)

        return itens

    @staticmethod
    def run_scripts(cmd_list):
        for cmd in cmd_list:
            print(cmd)
            print("$ " + " ".join(cmd))
            subprocess.run(cmd)


def main():
    args = Main.parse_args()
    if args.init:
        Main.init()

    cfg = Config.load_cfg(".indexer.json")
    Config.check_keys(cfg, ["base", "execute"])
    if args.b:
        Main.update_from_board(args.b)
    itens = []
    base = os.path.normpath(cfg["base"])
    for options in cfg["execute"]:
        itens = Main.execute_actions(base, options, itens, args.r)
        
    print("All done!")


if __name__ == '__main__':
    main()
