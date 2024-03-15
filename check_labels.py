#!/bin/python3

import sys
# use first parameter as filename
filename = sys.argv[1]


with open(filename, 'r') as file:
    data = file.read()
    lines = data.split('\n')

    ok = []
    not_ok = []

    for line in lines:
        if "/Readme.md)" in line:
            #print(line)
            label = line.split('@')[1].split(' ')[0].split(']')[0]
            hook = line.split('base/')[1].split('/')[0] 
            output = ("=" if label == hook else "!") + " " + label + " " + hook
            if label == hook:
                ok.append(output)
            else:
                not_ok.append(output)

    print("OK: ", len(ok))
    print("Not OK:")
    for line in not_ok:
        print(line)
