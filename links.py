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


class Links:
    @staticmethod
    def generate(hook_header_base: List[Union[str, str]], links_dir: str, base: str):
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
        parser = argparse.ArgumentParser(prog='links.py')
        parser.add_argument('--base', '-b', type=str, default="base", help="path to dir with the questions")
        parser.add_argument('--dir', type=str, default='.links', help = "dir to store md links")
        
        args = parser.parse_args()
        try:
            hook_header_base = Base.load_hook_header_from_base(args.base)
            Links.generate(hook_header_base, args.dir, args.base)
        except ValueError as e:
            print(str(e))


if __name__ == '__main__':
    Main.main()
