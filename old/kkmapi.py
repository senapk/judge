# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# import os
# import argparse
# from typing import Optional, List, Dict
# import json


# # Format used to send additional files to VPL
# class JsonFile:
#     def __init__(self, name: str, contents: str):
#         self.name: str = name
#         self.contents: str = contents
#         self.encoding: int = 0

#     def __str__(self):
#         return self.name + ":" + self.contents + ":" + str(self.encoding)


# class JsonVPL:
#     def __init__(self, title: str, description: str, tests: str = ""):
#         self.title: str = title
#         self.description: str = description
#         self.executionFiles: List[JsonFile] = [JsonFile("vpl_evaluate.cases", tests)]
#         self.requiredFile: Optional[JsonFile] = None

#     def add_execution_file(self, exec_file):
#         with open(exec_file) as f:
#             self.executionFiles.append(JsonFile(exec_file, f.read()))

#     def set_required_file(self, req_file):
#         with open(req_file) as f:
#             self.requiredFile = JsonFile(req_file, f.read())

#     def to_json(self) -> str:
#         return json.dumps(self, default=lambda o: o.__dict__, indent=4)

#     def __str__(self):
#         return self.to_json()

# def extract_title(readme_file):
#     hook = os.path.abspath(readme_file).split(os.sep)[-2]
#     with open(readme_file) as f:
#         title = f.read().split("\n")[0]
#         words = title.split(" ")
#         if words[0].count("#") == len(words[0]):  # only #
#             del words[0]
#         words = [word for word in words if not word.startswith("#")] #removendo as tags
#         title = "@" + hook + " " + " ".join(words)

# def generate(readme_file, description_file, tests_file, required_file, execution_files, output_file: str):
#     title = extract_title(readme_file)
#     with open(description_file) as f:
#             description = f.read()
#     with open(tests_file) as f:
#         tests = f.read()
#     jvpl = JsonVPL(title, description, tests)
#     for entry in execution_files:
#         jvpl.add_execution_file(entry)
#     if required_file is not None:
#         jvpl.set_required_file(required_file)
#     with open(output_file, "w") as f:
#         f.write(str(jvpl) + "\n")

