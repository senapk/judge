#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List, Tuple,  Optional
import os
import subprocess

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
        except ValueError as _e:
            pass
        return " ".join(words).strip()

    # generate a relative path from source to destination
    @staticmethod
    def get_directions(source: str, destination: str) -> str:
        source = os.path.normpath(source)
        destination = os.path.normcase(destination)
        source_list = source.split(os.sep)
        destin_list = destination.split(os.sep)
        while source_list[0] == destin_list[0]:
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
    def get_md_link(title: Optional[str]) -> str:
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
    def simple_run(cmd_list: List[str], input_data: str = "") -> str:
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
    def extract_hook_from_path(path: str, base: str):
        return path[len(base) + 1:-10]  # remove base and Readme.md

    @staticmethod
    def load_hook_header_from_base(base) -> List[Tuple[str, str]]:
        file_list = Base.find_files(base)
        header_list = Base.load_headers(file_list)
        hook_list = [Base.extract_hook_from_path(item, base) for item in file_list]  # remove base and Readme.md
        return list(zip(hook_list, header_list))
