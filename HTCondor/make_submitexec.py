

# read all the filenames
import os
import argparse

parser = argparse.ArgumentParser(description='make condor exec, submit and the script to submit all of the exec')
parser.add_argument('filepath', type=str, help='link to dir containing the text files to be used in condor exec')
args = parser.parse_args()

filepath = os.path.abspath(args.filepath)
txtfiles = os.listdir(args.filepath)
BGenPaths = []
for txtfile in txtfiles:
        print(filepath+txtfile)
        BGenPaths.append(filepath+txtfile)
        #with open(args.filepath+txtfile, 'r') as f:
        #        BGenPaths.append(f.readlines()[0])

# make the bash to run all the submits
with open('submitall.sh' , 'w+') as submitall_f:


    for BGenPath in BGenPaths:
        fname = BGenPath.split('.')[-2].split('/')[-1]


        print(fname)

        # make condor exec
        condor_exec_txt = (
            f'''#!/bin/bash

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

export X509_USER_PROXY=/afs/cern.ch/user/c/csutanta/x509up_u128984
cd /afs/cern.ch/user/c/csutanta/Projects/htoaa
source /afs/cern.ch/user/c/csutanta/.bashrc
time conda activate htoaa
            time /afs/cern.ch/work/c/csutanta/miniconda3/envs/htoaa/bin/python3 dataVsMC.py filepath+{fname} BGen
'''
        )
        with open(f'condor_exec_htoaa_{fname}.sh', 'w+') as condor_exec_f:
            condor_exec_f.write(condor_exec_txt)
            condor_exec_f.close()

        # condor submit
        condor_submit_txt = (
            f'''universe = vanilla
executable = condor_exec_htoaa_{fname}.sh
getenv = TRUE
log = htoaa_{fname}.log
output = htoaa_{fname}.out
error = htoaa_{fname}.error
notification = never
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
+JobFlavour = "microcentury"
RequestCpus = 4
queue
'''
        )
        with open(f'condor_submit_htoaa_{fname}.sh', 'w+') as condor_submit_f:
            condor_submit_f.write(condor_submit_txt)
            condor_submit_f.close()


        submitall_f.write(f'condor_submit condor_submit_htoaa_{fname}.sh\n')
