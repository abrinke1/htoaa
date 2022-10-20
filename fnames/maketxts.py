## get the file names from BGenFiles.txt into single individual files for submission to condor
import os
with open('../HToAATo4B_Pt150.txt') as f:
        BGenPaths = [line.rstrip() for line in f]


for BGenPath in BGenPaths:
    fname = BGenPath.split('.')[0].split('/')[-1]
    with open(f'{fname}.txt', 'w') as fbg:
            fbg.write(BGenPath)
