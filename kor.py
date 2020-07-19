#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import platform
import sys
from enum import Enum
from typing import List, Tuple, Any, Optional
import os
import re
import shutil
import argparse
import subprocess
import tempfile
import io
from subprocess import PIPE


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


class Runner:
    @staticmethod
    def simple_run(cmd_list: List[str], input_data: str = "") -> Tuple[int, Any, Any]:
        p = subprocess.Popen(cmd_list, stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        stdout, stderr = p.communicate(input=input_data)
        if p.returncode != 0:
            print(stderr)
            exit(1)
        return stdout

class Base:
    @staticmethod
    def find_files(base: str) -> List[str]:
        file_text = Runner.simple_run(["find", base, "-name", "Readme.md"])
        return [line for line in file_text.split("\n") if line != ""]

    @staticmethod
    def load_headers(file_list: List[str]) -> List[str]:
        headers = Runner.simple_run(["xargs", "-n", "1", "head", "-n", "1"], "\n".join(file_list))
        return headers.split("\n")

    @staticmethod
    def load_hook_header_from_base(base) -> List[Tuple[str, str]]:
        file_list = Base.find_files(base)
        header_list = Base.load_headers(file_list)
        hook_list = [item[len(base) + 1:-10] for item in file_list]  # remove base and Readme.md
        return list(zip(hook_list, header_list))

class Manual:
    @staticmethod
    def load_lines(path) -> List[str]:
        if os.path.isfile(path):
            with open(path) as f:
                return f.read().split("\n")
        return []

    @staticmethod
    def search_hook(line: str) -> Optional[str]:
        parts = line.split("@")
        if len(parts) == 1:
            return None
        return parts[1].split("]")[0].split(" ")[0].split(")")[0]   # extracting token
        
    @staticmethod
    def calc_prefix(line: str):
        cont = 0
        for c in line:
            if c == ' ':
                cont += 1
            else:
                break
        return cont
    
    @staticmethod
    def refactor_line(line: int, hook: str, header: str, base: str, hide: bool):
        prefix = Manual.calc_prefix(line)
        words = header.split(" ")
        tags = [word for word in words if word.startswith("#") and len(word) != word.count('#')]
        title = " ".join([word for word in words if not word.startswith("#")])
        line = ' ' * prefix + '- ['
        if not hide:
            line += '@' + hook + ' '
        line += title
        line += '](' + Util.join([base, hook, 'Readme.md']) + '#' + Util.get_md_link(header) + ') ' 
        
        extra = []
        if hide:
            extra.append('@' + hook)
        if len(tags) > 0:
            extra += tags
        if len(extra) > 0:
            line += " [](" + " ".join(extra) + ")"
        return line

    @staticmethod
    def find_header(hook_header_list: Tuple[Optional[str], Optional[str]], hook: Optinal[str]) -> Optional[str]:
        header = []
        if hook:
            header = [header for _hook, header in hook_header_list if _hook == hook]
        if len(header) == 0:
            return None
        else:
            return header[0]

    @staticmethod
    def load_line_hook_header_from_readme(line_list: List[str], hook_header_base: List[Tuple[str, str]]) -> List[Tuple[str, Optional[str], Optional[str]]]:
        hook_list = [Manual.search_hook(line) for line in line_list]
        header_list = [Manual.find_header(hook_header_base, hook) for hook in hook_list]
        return zip(line_list, hook_list, header_list)

    @staticmethod
    def generate_new_list(line_hook_header_readme, base, hide) -> List[str]:
        new_line_list = []
        for line, hook, header in line_hook_header_readme:
            if hook is None or header is None:
                new_line_list.append(line)
            else:
                new_line_list.append(Manual.refactor_line(line, hook, header, base, hide))
        return new_line_list

    @staticmethod
    def update_readme(line_list, new_line_list, path):
        if line_list != new_line_list:
            print("Updating", path)
            with open(path, "w") as f:
                f.write("\n".join(new_line_list))

    @staticmethod
    def find_not_used_hooks(line_hook_header_readme, hook_header_base, base, hide):
        hooks_readme = [item[1] for item in line_hook_header_readme]
        missing_hook_header = [pair for pair in hook_header_base if pair[0] not in hooks_readme]
        if len(missing_hook_header) > 0:
            print('Warning: There are hooks not used:')
            for hook, header in missing_hook_header:
                print(Manual.refactor_line("", hook, header, base, hide))
    
    @staticmethod
    def find_not_found_hooks(line_hook_header_readme, hook_header_base, base):
        line_list = [line for line, hook, _header in line_hook_header_readme if hook is not None and _header is None]
        if len(line_list) > 0:
            print("Warning: There are hooks not found:")
            for line in line_list:
                print(line)

    @staticmethod
    def indexer(hook_header_base, base, path, hide):
        line_list = Manual.load_lines(path)
        line_hook_header_readme = list(Manual.load_line_hook_header_from_readme(line_list, hook_header_base))
        new_line_list = Manual.generate_new_list(line_hook_header_readme, base, hide)
        Manual.update_readme(line_list, new_line_list, path)
        Manual.find_not_used_hooks(line_hook_header_readme, hook_header_base, base, hide)
        Manual.find_not_found_hooks(line_hook_header_readme, hook_header_base, base)


class Actions:
    

    @staticmethod
    def generate_links(hook_header_base: List[Union[str, str]], links_dir: str, base: str):
        shutil.rmtree(links_dir, ignore_errors=True)
        os.mkdir(links_dir)
        for hook, header in hook_header_base:
            title = " ".join([word for word in header.split(" ") if not word.startswith("#")])
            path = os.path.join(links_dir, title + ".md")
            with open(path, "w") as f:
                link = Util.get_directions(path, Util.join([base, hook, 'Readme.md']))
                f.write("[LINK](" + link + ")\n")
        
class Main:
    @staticmethod
    def main():
        parser = argparse.ArgumentParser(prog='kor')
        parser.add_argument('--base', '-b', type=str, default="base", help="path to dir with the questions")
        parser.add_argument('--file', '-f', type=str, default='Readme.md', help="source file do load and rewrite")
        parser.add_argument('--key', '-k', action='store_true', help="disable index key")
        
        args = parser.parse_args()
        try:
            hook_header_base = Base.load_hook_header_from_base(args.base)
            Manual.indexer(hook_header_base, args.base, args.file, args.key)
        except ValueError as e:
            print(str(e))


if __name__ == '__main__':
    Main.main()
