#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
from typing import Optional
import tempfile

class TOC:
    tag_begin = r"<!--TOC_BEGIN-->"
    tag_end = r"<!--TOC_END-->"
    regex = tag_begin + r"(.*)" + tag_end

    @staticmethod
    def only_hashtags(x: str) -> bool:
        return len(x) == x.count("#") and len(x) > 0

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
    def get_level(line: str) -> int:
        return len(line.split(" ")[0])

    @staticmethod
    def get_content(line: str) -> str:
        return " ".join(line.split(" ")[1:])

    @staticmethod
    def remove_code_blocks(content):
        regex = r"^```.*?```\n"
        return re.sub(regex, "", content, 0, re.MULTILINE | re.DOTALL)

    @staticmethod
    def search_old_toc(readme_content):
        found = re.search(TOC.regex, readme_content, re.MULTILINE | re.DOTALL)
        if found:
            return True, found[1]
        return False, ""

    @staticmethod
    def merge_toc(readme_content, toc):
        subst = TOC.tag_begin + "\\n" + toc + "\\n" + TOC.tag_end
        merged_content = re.sub(TOC.regex, subst, readme_content, 0, re.MULTILINE | re.DOTALL)
        return merged_content

    @staticmethod
    def make_toc(file_content):
        content = TOC.remove_code_blocks(file_content)

        lines = content.split("\n")
        disable_tag = "[]()"
        lines = [line for line in lines if TOC.only_hashtags(line.split(" ")[0]) and line.find(disable_tag) == -1]

        min_level = 1
        toc_lines = []
        for line in lines:
            level = (TOC.get_level(line) - 1) - min_level
            if level < 0:
                continue
            text = "    " * level + "- [" + TOC.get_content(line) + "](#" + TOC.get_md_link(line) + ")"
            toc_lines.append(text)
        toc_text = "\n".join(toc_lines)
        return toc_text

    @staticmethod
    def add_toc(file_content, quiet_mode: bool, path):
        file_content = file_content.replace("!TOC\n", TOC.tag_begin + "\n" + TOC.tag_end + "\n")

        found, _text = TOC.search_old_toc(file_content)
        if found:
            toc_text = TOC.make_toc(file_content)
            updated_content = TOC.merge_toc(file_content, toc_text)
            if updated_content != file_content and not quiet_mode:
                print("Updating TOC in", path)
            return updated_content
        elif not quiet_mode:
            print("Create an entry with the text:\n!TOC")
            print("in the file", path)
            print("Use '[]()' string in the entries that you want to hide in toc")
        return file_content

class ADD:
    @staticmethod
    def evaluate(line: str, store: bool, delete: bool):
        if delete:
            return False
        elif store:
            return True
        for token in ["", "    "]:
            if line == token:
                return False
        for token in ["import", "    @", "        ", "    }"]:
            if line.startswith(token):
                return False
        return True

    @staticmethod
    def transform(line: str, store: bool):
        if store:
            return line
        return line.replace("){", ") {").replace(") {", ");")

    @staticmethod
    def process(content: str) -> str:
        lines = content.split("\n")
        output = []
        store = False
        delete = False
        for line in lines:
            if "!KEEP" in line:
                store = True
            elif "!DEL" in line:
                delete = True
            elif "!OFF" in line:
                store = False
            elif "!INS" in line:
                delete = False
            elif ADD.evaluate(line, store, delete):
                line = ADD.transform(line, store)
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
        updated = TOC.add_toc(updated, args.quiet, path)
        updated = ADD.remove_above(updated, "ADD", "ADD_END")
        updated = ADD.remove_above(updated, "FILTER", "FILTER_END")
        updated = ADD.insert_files(updated, folder)
        
        if updated != original:
            with open(path, "w") as f:
                f.write(updated)

if __name__ == '__main__':
    main()