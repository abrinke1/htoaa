import pickle
import numpy as np
import pandas as pd
from analib import PhysObj, Event
import dataVsMC_DataManager as DM
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import mplhep as hep
import uproot
import os
import multiprocessing as mp
import time
import argparse
from pathlib import Path

#np.seterr(divide='ignore', invalid='ignore')

## get that sweet CMS style plots
plt.style.use(hep.style.CMS)


## if reading from rootfiles, set true. if already have pickle of dataframe, set false
root = True

## function to add a BDTScore column to each of the background/signal/data DF
# loadedModel = pickle.load(open('BDTModels/Htoaa_BDThigh disc.pkl', 'rb'))
#def analyze(dataDf):
#    prediction = loadedModel.predict_proba(dataDf[trainVars])
#    dataDf = dataDf.assign(BDTScore=prediction[:,1])
#    return dataDf



histranges = {           'FatJet_btagCSVV2' :   ((0,1), 20),
                       'FatJet_btagDDBvLV2' :   ((0,1), 20),
                         'FatJet_btagDeepB' :   ((0,1), 20),
                'FatJet_deepTagMD_H4qvsQCD' :   ((0,1), 20),
                               'FatJet_eta' :   ((-2.4, 2.4), 20),
                              'FatJet_mass' :   ((90, 250), 32),
                         'FatJet_msoftdrop' :   ((90, 200), 22),
                              'FatJet_n2b1' :   ((0, 0.5), 10),
                                'FatJet_pt' :   ((180, 1500), 40),
                                   'LHE_HT' :   ((500, 2500), 50),
                 'FatJet_particleNetMD_Xbb' :   ((0,1), 20),
              'FatJet_particleNet_H4qvsQCD' :   ((0,1), 20),
              'FatJet_particleNet_HbbvsQCD' :   ((0,1),20),
                 'FatJet_particleNetMD_QCD' :   ((0,1),20),
                   'FatJet_particleNet_QCD' :   ((0,1),20),
                  'FatJet_particleNet_mass' :   ((0,250), 20),
                'FatJet_deepTagMD_HbbvsQCD' :   ((0,1), 20),
               'FatJet_deepTagMD_ZHbbvsQCD' :   ((0,1), 20),
               'FatJet_deepTagMD_bbvsLight' :   ((0,1), 20),
                         'FatJet_deepTag_H' :   ((0,1), 20),
                       'FatJet_deepTag_QCD' :   ((0,1), 20),
                           'FatJet_btagHbb' :   ((-1,1), 20),

              #'Muon_eta' : (-2.4, 2.4),
              #'Muon_ip3d' : (0, 0.5),
              #'Muon_pt' : (0, 300),
              #'Muon_softId' : (0,1),
                                  'PV_npvs' : ((1,90), 10),
                               'PV_npvsGood': ((0,70), 10)}

nphists = {col:[0.0, 0.0] for col in histranges}
cols = histranges.keys()

## function to get center of ins given binedges as np array
def getBinCenter(arr):
    arrCen = list()
    for i in range(len(arr)-1):
        arrCen.append((arr[i+1]+arr[i])/2)
    return arrCen


## get all rootfiles from a given folder
# def getFileNames(directory):
#     filelist = []
#     for root, dirs, files in os.walk(directory):
#         for name in files:
#             filelist.append(os.path.join(root, name))
#     return filelist


## make dict of np.histogram given maxPtData df
def makeNpHist(df):
    toremove = ['final_weights', 'LHE_weights']

    for i in toremove:
        if i in cols: cols.remove(i)

    nphistdict = {}

    for var in cols:
        nbins = histranges[var][1]

        nphistdict[var] = np.histogram(df[var], bins=nbins, range=histranges[var][0], weights=df['final_weights'])

    return nphistdict


def main(fname,tag):
    # fname = 'BGenFiles-short.txt' #'BGenFiles.txt'
    # read the bgenfile from txt
    # with open(fname) as f:
    #     BGenPaths = filter(None, (line.rstrip() for line in f_in))
    with open(fname) as f:
        BGenPaths = [line.rstrip() for line in f]#filter(None, (line.rstrip() for line in f)) #f.read().split('\n')

    BGenPaths = ['root://xrootd-cms.infn.it/' + x for x in BGenPaths]

    for filedir in BGenPaths:#DM.TunCP5Path
        ## better to parallel across the files than folders since more files than folders exist

        print(filedir)

        results = DM.processData(filedir, tag=tag, dataSet='UL', MC=True)

        ## save nphists so that it can be loaded and plotted without running the whole thing again

        pname = filedir.split('.')[-2].split('/')[-1]

        Path(f"pickles/{tag}").mkdir(parents=True, exist_ok=True)
        pickle.dump(results, open(f'pickles/{tag}/{pname}.pkl', 'wb'))



if __name__ == "__main__":
    parser = argparse.ArgumentParser("create data vs mc pickles")
    parser.add_argument('fname', type=str, help='name of file containing root file locations on /store/... accessed using xrootd')
    parser.add_argument('tag', type=str, help='BGen, ggH, etc. check datavsmc_datamanager for available tags')
    args = parser.parse_args()
    main(args.fname,args.tag)
