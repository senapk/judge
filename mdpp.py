#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
import enum
from typing import Optional

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


class Mode(enum.Enum):
    ADD = 1
    RAW = 2
    DEL = 3

class ADD:
    @staticmethod
    def evaluate(line: str, mode: Mode, keep_comment: bool):
        if mode == Mode.DEL:
            return False
        if "//" in line and not keep_comment:
            return False
        if mode == Mode.RAW:
            return True
        for token in ["    "]:
            if line == token:
                return False
        for token in ["import", "    @", "        ", "    }"]:
            if line.startswith(token):
                return False
        return True

    @staticmethod
    def transform(line: str, mode: Mode):
        if mode == Mode.RAW:
            return line
        if line == "//":
            return ""
        return line.replace("){", ") {")\
                    .replace("):",   ") :")\
                    .replace(") :",   ") {")\
                    .replace(") const {", ") const { ... }")\
                    .replace(") {", ") { ... }");

    @staticmethod
    def process(content: str) -> str:
        lines = content.split("\n")
        output = []
        mode = Mode.ADD
        keep_comment = True
        for line in lines:
            if "!ADD" in line:
                mode = Mode.ADD
            elif "!RAW" in line:
                mode = Mode.RAW
            elif "!DEL" in line:
                mode = Mode.DEL
            elif "!NOCOMMENT" in line:
                keep_comment = False
            elif ADD.evaluate(line, mode, keep_comment):
                line = ADD.transform(line, mode)
                output.append(line)
        return "\n".join(output)

    @staticmethod
    def remove_above(content, tagbegin, tagend):
        regex = r"<!--" + tagbegin + r"(.*?)-->.*?<!--" + tagend + r"-->"
        replace = "<!--" + tagbegin + "\\1-->"
        return re.sub(regex, replace, content, 0, re.MULTILINE | re.DOTALL)

    @staticmethod
    def insert_fences(output, content, language, tagend):
        output.append("```" + language)
        output.append(content)
        output.append("```")
        output.append("<!--" + tagend + "-->")

    @staticmethod
    def remove_extra_newline(updated, tag):
        while "\n\n```\n<!--" + tag + "-->" in updated:
            updated = updated.replace("\n\n```\n<!--" + tag + "-->", "\n```\n<!--" + tag + "-->")
        return updated

    @staticmethod
    def insert_files(content, folder):
        lines = content.split("\n")
        output = []
        for line in lines:
            if line.startswith("!ADD"):
                line = line.replace("!ADD", "<!--ADD")
                line = line + "-->"
            if line.startswith("!FILTER"):
                line = line.replace("!FILTER", "<!--FILTER")
                line = line + "-->"
            if line.startswith("<!--ADD "):
                output.append(line)
                data = line.replace("<!--ADD ", "").replace("-->", "").split(" ")
                content = open(os.path.join(folder, data[0])).read()
                ADD.insert_fences(output, content, data[1], "ADD_END")
            elif line.startswith("<!--FILTER "):
                output.append(line)
                data = line.replace("<!--FILTER ", "").replace("-->", "").split(" ")
                content = open(os.path.join(folder, data[0])).read()
                content = ADD.process(content)
                ADD.insert_fences(output, content, data[1], "FILTER_END")
            else:
                output.append(line)
        updated = "\n".join(output)
        updated = ADD.remove_extra_newline(updated, "ADD_END")
        updated = ADD.remove_extra_newline(updated, "FILTER_END")
        return updated

class Save:
    @staticmethod
    # execute filename and content
    def execute(content):
        regex = r"\[\]\(save\)\[\]\((.*?)\)\n```[a-z]*\n(.*?)```\n\[\]\(save\)"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        
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
        updated = ADD.remove_above(updated, "ADD", "ADD_END")
        updated = ADD.remove_above(updated, "FILTER", "FILTER_END")
        updated = ADD.insert_files(updated, folder)
        Save.execute(updated)
        if updated != original:
            with open(path, "w") as f:
                f.write(updated)

if __name__ == '__main__':
    main()