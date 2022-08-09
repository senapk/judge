#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
import enum
from typing import Optional
from filter import Filter

class TocMaker:
    @staticmethod
    def __only_hashtags(x: str) -> bool:
        return len(x) == x.count("#") and len(x) > 0

    # generate md link for the text
    @staticmethod
    def __get_md_link(title: Optional[str]) -> str:
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
    def __get_level(line: str) -> int:
        return len(line.split(" ")[0])

    @staticmethod
    def __get_content(line: str) -> str:
        return " ".join(line.split(" ")[1:])

    @staticmethod
    def __remove_code_fences(content: str) -> str:
        regex = r"^```.*?```\n"
        return re.sub(regex, "", content, 0, re.MULTILINE | re.DOTALL)


    @staticmethod
    def execute(content: str) -> str:
        content = TocMaker.__remove_code_fences(content)

        lines = content.split("\n")
        disable_tag = "[]()"
        lines = [line for line in lines if TocMaker.__only_hashtags(line.split(" ")[0]) and line.find(disable_tag) == -1]

        min_level = 1
        toc_lines = []
        for line in lines:
            level = (TocMaker.__get_level(line) - 1) - min_level
            if level < 0:
                continue
            text = "    " * level + "- [" + TocMaker.__get_content(line) + "](#" + TocMaker.__get_md_link(line) + ")"
            toc_lines.append(text)
        toc_text = "\n".join(toc_lines)
        return toc_text

class Toc:
    @staticmethod
    def execute(content: str) -> str:
        new_toc = TocMaker.execute(content)
        regex = r"\[\]\(toc\)\n" + r"(.*?)"+ r"\[\]\(toc\)"
        subst = r"[](toc)\n" + new_toc + r"\n[](toc)"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)


class Load:
    @staticmethod
    def execute(content: str) -> str:
        new_content = ""
        last = 0

        regex = r"\[\]\(load\)\[\]\((.*?)\)\n(.*?)\[\]\(load\)"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            path = match.group(1)
            new_content += content[last:match.start()] # inserindo texto entre matches
            last = match.end()
            new_content += "[](load)[](" + path + ")\n"
            if os.path.isfile(path):
                data = open(path).read()
                new_content += open(path).read()
                if data[-1] != "\n":
                    new_content += "\n"
            else:
                print("warning: file", path, "not found")
            new_content += "[](load)"
        new_content += content[last:]
        return new_content

class Filter:
    @staticmethod
    def execute(content: str) -> str:
        new_content = ""
        last = 0

        regex = r"\[\]\(filter\)\[\]\((.*?)\)\n(.*?)\[\]\(filter\)"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            path = match.group(1)
            new_content += content[last:match.start()] # inserindo texto entre matches
            last = match.end()
            new_content += "[](filter)[](" + path + ")\n"
            if os.path.isfile(path):
                data = open(path).read()
                filter = Filter()
                new_content += filter.process(open(path).read())
                if data[-1] != "\n":
                    new_content += "\n"
            else:
                print("warning: file", path, "not found")
            new_content += "[](filter)"
        new_content += content[last:]
        return new_content
            

class Save:
    @staticmethod
    # execute filename and content
    def execute(file_content):
        regex = r"\[\]\(save\)\[\]\((.*?)\)\n```[a-z]*\n(.*?)```\n\[\]\(save\)"
        matches = re.finditer(regex, file_content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            path = match.group(1)
            content = match.group(2)
            exists = os.path.isfile(path)
            if exists:
                content_old = open(path).read()
            if not exists or content != content_old:
                with open(path, "w") as f:
                    print("file", path, "updated")
                    f.write(content)

class Main:
    @staticmethod
    def fix_path(target):
        target = os.path.normpath(target)
        if os.path.isdir(target):
            target = os.path.join(target, "Readme.md")
        pieces = target.split(os.sep)
        folder = "."
        if len(pieces) > 1:
            folder = os.sep.join(pieces[:-1])
        return target, folder

    @staticmethod
    def open_file(path): 
        if os.path.isfile(path):
            with open(path) as f:
                file_content = f.read()
                return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('targets', metavar='T', type=str, nargs='*', help='Readmes or folders')
    parser.add_argument('--quiet', '-q', action="store_true", help='quiet mode')
    args = parser.parse_args()

    if len(args.targets) == 0:
        args.targets.append(".")
    
    for target in args.targets:
        path, folder = Main.fix_path(target)
        result, original = Main.open_file(path)
        if not result:
            continue
        updated = original
        updated = Toc.execute(updated)
        updated = Load.execute(updated)
        updated = Filter.execute(updated)
        Save.execute(updated)
        if updated != original:
            with open(path, "w") as f:
                f.write(updated)

if __name__ == '__main__':
    main()