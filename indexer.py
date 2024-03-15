#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
import subprocess
from typing import Optional, List, Dict
from os.path import join, isdir, isfile, getmtime


parser = argparse.ArgumentParser(description='Indexer')
parser.add_argument('path', type=str, help='Path to Markdown file')

args = parser.parse_args()

with open(args.path, 'r') as file:
    content = file.read()

lines = content.split('\n')

output = []

for line in lines:
    new_description = 'New description'
    match = re.search(r'\[(.*?)\]\((.*?)\)', line)
    data = line
    if match:
        link = match.group(2)
        if link.endswith('md') and not link.startswith('http'):
            if not isfile(link):
                print(link, ' not found')
            else:
                header = open(match.group(2), 'r').read().split('\n')[0]
                if (len(header) == 0):
                    print('Empty header in ', link)
                # remove first word
                try:
                    header = header.split(' ', 1)[1]
                except:
                    print('Error ', header)
                    pass
                new_description = header
                #print(new_description)
                #replace line with new description
                data = line.replace(match.group(1), new_description)
    output.append(data)

with open(args.path, 'w') as file:
    file.write('\n'.join(output))
