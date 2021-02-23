#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
from typing import Optional

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
    def add_toc(path):
        if os.path.isfile(path):
            with open(path) as f:
                file_content = f.read()
        else:
            print("Warning: File", path, "not found")
            return()

        toc_text = TOC.make_toc(file_content)
        found, _text = TOC.search_old_toc(file_content)
        if found:
            merged_content = TOC.merge_toc(file_content, toc_text)
            if file_content != merged_content:
                print("Toc updated in", path)
                with open(path, "w") as f:
                    f.write(merged_content)
        else:
            print("Create an entry with the text:")
            print(TOC.tag_begin)
            print(TOC.tag_end)
            print("in the file", path)
            print("Use '[]()' string in the lines that you want to hide in toc")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('targets', metavar='T', type=str, nargs='*', help='Readmes or folders')
    args = parser.parse_args()

    if len(args.targets) == 0:
        args.targets.append(".")
    
    for target in args.targets:
        target = os.path.normpath(target)
        if os.path.isdir(target):
            target = os.path.join(target, "Readme.md")
        TOC.add_toc(target)

if __name__ == '__main__':
    main()