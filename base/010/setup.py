import argparse
import json

data = {}

parser = argparse.ArgumentParser()
parser.add_argument("--required", "-r", type=str)
parser.add_argument("--system", "-s", type=str, nargs="*", help="system files")
parser.add_argument("--keep", "-k", type=str, nargs="*", help="user files to keep")
args = parser.parse_args()
data["keep"] = args.keep
data["system"] = args.system
data["required"] = args.required
with open(".mapi", "w") as f:
    f.write(json.dumps(data, indent=4) + "\n")