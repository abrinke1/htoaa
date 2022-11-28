## get the file names from BGenFiles.txt into single individual files for submission to condor
## usaqqge: pytyhon maketxts.py <textfile> <tag>
## textfile contains the list of rootfiles to bew converted into individual textfiles. The list of root files can be acquired from das
## tag is like BGen, bEnr, ggH, etc etc
import os
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('txtfile')
parser.add_argument('tag')
args = parser.parse_args()
tag = args.tag
with open(args.txtfile) as f:
        paths = [line.rstrip() for line in f]


for path in paths:
    fname = path.split('.')[0].split('/')[-1]
    Path(f"{tag}").mkdir(parents=True, exist_ok=True)
    with open(f'{tag}/{fname}.txt', 'w') as fbg:
            fbg.write(path)
