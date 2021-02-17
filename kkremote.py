#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import argparse
from typing import Optional


def insert_remote_url(content: str, remote_url: Optional[str]) -> str:
    if remote_url is None:
        return content
    if not remote_url.endswith("/"):
        remote_url += "/"
    regex = r"\[(.*)\]\((\s*)([^:\s]*)(\s*)\)"
    subst = "[\\1](" + remote_url + "\\3)"
    result = re.sub(regex, subst, content, 0, re.MULTILINE)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='Readme.md path')
    parser.add_argument('--remote', '-r', type=str, help='remote prefix')
    parser.add_argument('--output', '-o', type=str, help='destination path')

    args = parser.parse_args()

    content = open(args.source).read()
    content = insert_remote_url(content, args.remote)
    if args.output:
        open(args.output, "w").write(content)
    else:
        print(content)


if __name__ == '__main__':
    main()
