#!/bin/bash

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

export X509_USER_PROXY=/afs/cern.ch/user/c/csutanta/x509up_u108989
cd /afs/cern.ch/user/c/csutanta/Projects/htoaa
source /afs/cern.ch/user/c/csutanta/.bashrc
time conda env list
time conda activate htoaa
time conda env list
python --version
python3 -V
which python
which python3
time conda list
which conda
time /afs/cern.ch/work/c/csutanta/miniconda3/envs/htoaa/bin/python3 dataVsMC.py BGenFiles-short.txt
