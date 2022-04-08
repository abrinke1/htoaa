#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 19:33:18 2020

@author: si_sutantawibul1
"""

import uproot
import pandas as pd
from analib import PhysObj, Event
import sys
import os
import pickle
import numpy as np
#from dataManager import getSubJetData, getnSVCounts
from htoaaRootFilesLoc import  BGenPaths, TunCP5Paths#WJetsPaths, ZJetsPaths
from DMFuncs import *
import re

#import htoaaRootFilesLoc

#JetHT = False

#exec(open("./htoaaRootFilesLoc.py").read())

## MC weights for each pt range
#BGenWeights = [0.3234, 1.375, 72.05, 331,1]
BGenWeights = {
    '200to300' : 5.96579,
    '300to500' : 1.63893,
    '500to700' : 0.371682,
    '700to1000' : 0.123908,
    '1000to1500' :  0.0707572,
    '1500to2000' : 0.0266096,
    '2000toInf' : 0.0101252
}


## dict of file and weights 
#BGenDict = dict(zip(BGenPaths, BGenWeights))
#TunCP5Dict = {path:1 for path in TunCP5Paths}
# QCDIncDict = dict(zip(QCDIncPaths,QCDIncWeight))
#ZJetsDict = dict(zip(ZJetsPaths, ZJetsWeight))
#WJetsDict = dict(zip(WJetsPaths, WJetsWeight))



## variables to compare MC and data
jetVars = ['FatJet_pt',
           'FatJet_eta',
           'FatJet_mass',
           'FatJet_msoftdrop',
           'FatJet_btagCSVV2',
           'FatJet_btagDeepB',
           'FatJet_btagDDBvLV2',
           'FatJet_deepTagMD_H4qvsQCD',
           'FatJet_n2b1',
           'FatJet_particleNetMD_Xbb',
           'FatJet_particleNet_H4qvsQCD',
           'FatJet_particleNet_HbbvsQCD',
           'FatJet_particleNetMD_QCD',
           'FatJet_particleNet_QCD',
           'FatJet_particleNet_mass',
           'FatJet_deepTagMD_HbbvsQCD',
           'FatJet_deepTagMD_ZHbbvsQCD',
           'FatJet_deepTagMD_bbvsLight',
           'FatJet_deepTagMD_H4qvsQCD',
           'FatJet_deepTag_H',
           'FatJet_deepTag_QCD',
           #'FatJet_btagDDBvLV2',
           'FatJet_btagHbb',
           #'FatJet_btagDeepB',
           #'FatJet_btagCSVV2'
           
           #'SubJet_mass(1)',
           #'SubJet_mass(2)',
           #'SubJet_tau1(1)',
           #'FatJet_n3b1',
           #'FatJet_tau2',
           #'FatJet_tau2',
           #'SubJet_n2b1(1)',
           #'SubJet_pt(1)|FatJet_pt',
           #'SubJet_pt(2)|FatJet_pt',
           #'SubJet_btagDeepB(2)',
           #'SubJet_tau1(2)',
           #'FatJet_nSV'
]
muonVars = ['Muon_pt',
            'Muon_eta',
            'Muon_ip3d',
            'Muon_softId']

ak4JetVars = ['Jet_btagDeepFlavB']

PVVars = ['PV_npvs', 'PV_npvsGood']

allVars = list(jetVars + muonVars + PVVars + ak4JetVars + ['LHE_HT'])
allVars.sort()

## for checking that input into processData have the valid cases setup
tagslist = ['BGen' , 'QCD', 'WJets', 'ZJets', 'TunCP5']

## dataset list 
dataSetList = ['UL']




## filePath: (str) path to root file to process
## tag: (str) what dataset the root file is (BGen, GGH..) check list of valid tags
## dataset: (str) what kind of cuts you want to be making. check list of valid datasets
## MC: (bool) is this file MC or not
def processData (filePath, tag, dataSet, MC): #JetHT=False):
    ## open file, get events
    fileName, fileExtension = os.path.splitext(filePath)

    print(filePath)

    if fileExtension != '.root':
        print('this program only supports .root  files')
        sys.exit()

    if tag not in tagslist:
        print(f'tag given: {tag} \n taglist: {taglist}')
        print('check yo tags')
        sys.exit()

    if dataSet not in dataSetList:
        print(f'dataset given: {dataSet} \n datasetlist: {dataSetList}')
        print('check dataset')
        sys.exit()

    if type(MC) != bool:
        print('MC needs to be set true/false')
        sys.exit()

    f = uproot.open(fileName + '.root')
    events = f.get('Events')

    ## create physics objects 
    jets = PhysObj('jets' + fileName)
    # muons = PhysObj('muons' + fileName)
    other = PhysObj('other' + fileName)
    ak4Jets = PhysObj('ak4Jets' + fileName)

    ## data doens't have LHE_HT
    if tag == 'data' and 'LHE_HT' in allVars:
        allVars.remove('LHE_HT')

    ## fill the PhysObjs with data from the root file
    ## fatjets vars
    for v in jetVars:
        jets[v] = pd.DataFrame(events.array(v))
    # jets['FatJet_pt'] = pd.DataFrame(events.array('FatJet_pt'))
    # jets['FatJet_eta'] = pd.DataFrame(events.array('FatJet_eta'))
    # jets['FatJet_mass'] = pd.DataFrame(events.array('FatJet_mass'))
    # jets['FatJet_btagCSVV2'] = pd.DataFrame(events.array('FatJet_btagCSVV2'))
    # jets['FatJet_btagDeepB'] = pd.DataFrame(events.array('FatJet_btagDeepB'))
    # jets['FatJet_msoftdrop'] = pd.DataFrame(events.array('FatJet_msoftdrop'))
    # jets['FatJet_btagDDBvLV2'] = pd.DataFrame(events.array('FatJet_btagDDBvLV2'))
    # jets['FatJet_deepTagMD_H4qvsQCD'] = pd.DataFrame(events.array('FatJet_deepTagMD_H4qvsQCD'))
    # jets['FatJet_phi'] = pd.DataFrame(events.array('FatJet_phi'))
    # jets['FatJet_n2b1'] = pd.DataFrame(events.array('FatJet_n2b1'))
    #jets['SubJet_mass(1)'] = getSubJetData(1,'SubJet_mass', events)
    #jets['SubJet_mass(2)'] = getSubJetData(2, 'SubJet_mass', events)
    #jets['SubJet_tau1(1)'] = getSubJetData(1, 'SubJet_tau1', events)
    # jets['FatJet_n3b1'] = pd.DataFrame(events.array('FatJet_n3b1'))
    # jets['FatJet_tau2'] = pd.DataFrame(events.array('FatJet_tau2'))
    # jets['SubJet_n2b1(1)'] = getSubJetData(1, 'SubJet_n2b1', events)
    # jets['SubJet_pt(1)|FatJet_pt'] = getSubJetData(1, 'SubJet_pt', events)/jets.FatJet_pt
    # jets['SubJet_pt(2)|FatJet_pt'] = getSubJetData(2, 'SubJet_pt', events)/jets.FatJet_pt
    # jets['SubJet_btagDeepB(2)'] = getSubJetData(2, 'SubJet_btagDeepB', events)
    # jets['SubJet_tau1(2)'] = getSubJetData(2, 'SubJet_tau1', events)
    
    for v in ak4JetVars:
        ak4Jets[v] = pd.DataFrame(events.array(v))
    # ak4Jets['Jet_pt'] = pd.DataFrame(events.array('Jet_pt'))
    # ak4Jets['Jet_eta'] = pd.DataFrame(events.array('Jet_eta'))
    # ak4Jets['Jet_puId'] = pd.DataFrame(events.array('Jet_puId'))
    # ak4Jets['Jet_phi'] = pd.DataFrame(events.array('Jet_phi'))
    # ak4Jets['Jet_btagDeepB'] = pd.DataFrame(events.array('Jet_btagDeepB'))

    ## fill muon physics objects (only for parked dataset) 

    # muons['Muon_pt'] = pd.DataFrame(events.array('Muon_pt'))
    # muons['Muon_eta'] = pd.DataFrame(np.abs(events.array('Muon_eta')))
    # muons['Muon_ip3d'] = pd.DataFrame(events.array('Muon_ip3d'))
    # muons['Muon_softId'] = pd.DataFrame(events.array('Muon_softId')).fillna(0).astype(int)
    # muons['Muon_IP'] = pd.DataFrame(events.array('Muon_dxy')/events.array('Muon_dxyErr')).abs()


    ## other vars
    if MC:
        other['LHE_HT'] = pd.DataFrame(events.array('LHE_HT')).astype(np.float64)
    other['PV_npvs'] = pd.DataFrame(events.array('PV_npvs'))
    other['PV_npvsGood'] = pd.DataFrame(events.array('PV_npvsGood'))
    

    ## make Event object
    ev = Event(jets, other, ak4Jets)

    ## cutting events
    ## jet cuts
    jets.cut(jets['FatJet_pt'] > 170)
    jets.cut(jets['FatJet_eta'].abs() < 2.4)
    # jets.cut(jets['FatJet_btagDDBvLV2'] > 0.8)
    # jets.cut(jets['FatJet_btagDeepB'] > 0.4184)
    jets.cut(jets['FatJet_msoftdrop'] > 90)
    jets.cut(jets['FatJet_msoftdrop'] < 200)#<= 200)
    jets.cut(jets['FatJet_mass'] > 90)
    #jets.cut(jets['FatJet_mass'] <= 200)
    other.cut(other['PV_npvsGood'] >= 1)
    
    ev.sync()

    ## muon cuts
    # muons.cut((muons['Muon_softId'] > 0.9))
    # muons.cut(muons['Muon_eta'].abs() < 2.4)
    # muons.cut(muons['Muon_pt'] > 7)
    # muons.cut(muons['Muon_IP'] > 2)
    # muons.cut(muons['Muon_ip3d'] < 0.5)



    ## have to calculate dR after cutting all the things, so that I don't
    ## choose the wrong fat jet
    # ak4Jets['dR'] = getdR(objName='Jet', events=events, fatJetPhysObj=jets, jetPhysObj=ak4Jets)
    # other['JetFatJet_dRCnt'] = getdRCount(ak4Jets['dR'])
    # ak4Jets.cut(ak4Jets['dR'] < 0.8)

    ## rename the columns of LHE_HT, PV_npvs, PV_npvsGood to match the ones that get
    ## passed into getMaxPt
    if MC:
        other.LHE_HT = other.LHE_HT.rename({0:'LHE_HT'}, axis='columns')
    other.PV_npvs = other.PV_npvs.rename({0:'PV_npvs'}, axis='columns')
    other.PV_npvsGood =other.PV_npvsGood.rename({0:'PV_npvsGood'}, axis='columns')

    ## sync so all events cut to same events after apply individual cuts
    ev.sync()

    ## return empty frame if nothing is left after cuts
    if jets.FatJet_pt.empty:
        return pd.DataFrame()

    else:
        ## Return only the highest pt physics objects and their related variables
        maxPtJets = getMaxPt(jets, 'FatJet_pt')
        maxPtData = maxPtJets

        ## !!!!!!!!!! SI: MAYBE DO MUONS TOO !!!!!!!!!!!!!!!!!!!!!
        #maxPtMuons = getMaxPt(muons, 'Muon_pt')
        #maxPtData = pd.concat([maxPtJets, maxPtMuons], axis=1)

        maxPtData = maxPtData.assign(PV_npvs=other.PV_npvs.to_numpy())
        maxPtData = maxPtData.assign(PV_npvsGood=other.PV_npvsGood.to_numpy())

        ## add index back into the df for comparison
        # maxPtData['eventNum'] = jets.FatJet_pt.index

        if MC:
            maxPtData = maxPtData.assign(LHE_HT=other.LHE_HT.to_numpy())

        ## applying weighing factors for MC to match data
        ## LHE_weights
        
        if 'BGen'==tag:
            key = re.search('QCD_HT(.*)_B', fileName).group(1) ##find which HT range from filename 
            maxPtData['LHE_weights'] = BGenWeights[key]
            # for i in BGenDict:
            #     if i in fileName:
            #         key = i 
            #         maxPtData['LHE_weights'] = BGenDict[key]
            maxPtData = maxPtData.assign(final_weights = maxPtData['LHE_weights'])
                
        elif 'TunCP5'==tag:
            for i in TunCP5Dict:
                if i in fileName:
                    key = i 
                    maxPtData['LHE_weights'] = TunCP5Dict[key]
                    maxPtData = maxPtData.assign(final_weights = maxPtData['LHE_weights'])

        elif 'WJets'==tag:
            maxPtData['LHE_weights'] = WJetsDict[filePath]
            maxPtData = maxPtData.assign(final_weights = maxPtData['LHE_weights'])


        elif 'ZJets'==tag:
            maxPtData['LHE_weights'] = ZJetsDict[filePath]
            maxPtData = maxPtData.assign(final_weights = maxPtData['LHE_weights'])

        if tag == 'data':
            maxPtData['final_weights'] = ParkedDataDict[filePath]


    #maxPtData['FatJet_nSV'] = getnSVCounts(jets, events)
    maxPtData = maxPtData.dropna(how='all')
    #maxPtData = maxPtData.fillna(0)

    return maxPtData



