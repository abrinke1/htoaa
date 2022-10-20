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
import time

#import htoaaRootFilesLoc

#JetHT = False

#exec(open("./htoaaRootFilesLoc.py").read())

## MC weights for each pt range
#BGenWeights = [0.3234, 1.375, 72.05, 331,1]
BGenWeights = {
    # '200to300' : 5.96579,
    # '300to500' : 1.63893,
    # '500to700' : 0.371682,
    # '700to1000' : 0.123908,
    # '1000to1500' :  0.0707572,
    # '1500to2000' : 0.0266096,
    # '2000toInf' : 0.0101252
    (200,300) : 5.96579,
    (300,500) : 1.63893,
    (500,700) : 0.371682,
    (700,1000) : 0.123908,
    (1000,1500) :  0.0707572,
    (1500,2000) : 0.0266096,
    (2000,np.Inf) : 0.0101252
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
           'FatJet_phi',
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
           'FatJet_btagHbb',
           'FatJet_deepTagMD_ZbbvsQCD',
           'FatJet_deepTagMD_ZvsQCD',
           'FatJet_deepTag_QCDothers',
           'FatJet_deepTag_ZvsQCD',
           'FatJet_n3b1',
           'FatJet_particleNetMD_Xqq',
           'FatJet_particleNet_ZvsQCD',
           'FatJet_tau1',
           'FatJet_tau2',
           'FatJet_tau3',
           'FatJet_tau4',
           'FatJet_lsf3',
           'FatJet_jetId',
           'FatJet_nConstituents',

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

otherVars = ['run','luminosityBlock','event', 'PV_npvs', 'PV_npvsGood']

allVars = list(jetVars + muonVars + PVVars + ak4JetVars + ['LHE_HT'])
allVars.sort()

## for checking that input into processData have the valid cases setup
tagslist = ['BGen' , 'QCD', 'WJets', 'ZJets', 'TunCP5', 'ggH']

## dataset list
dataSetList = ['UL']




## filePath: (str) path to root file to process
## tag: (str) what dataset the root file is (BGen, GGH..) check list of valid tags
## dataset: (str) what kind of cuts you want to be making. check list of valid datasets
## MC: (bool) is this file MC or not
def processData (filePath, tag, dataSet, MC): #JetHT=False):
    ## open file, get events
    fileName, fileExtension = os.path.splitext(filePath)

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


    f = uproot.open(filePath)

    events = f.get('Events')

    ## create physics objects
    jets = PhysObj('jets' + fileName)
    # muons = PhysObj('muons' + fileName)
    other = PhysObj('other' + fileName)
    #ak4Jets = PhysObj('ak4Jets' + fileName)
    genPart = PhysObj('genPart' + fileName)

    ## data doens't have LHE_HT
    if tag == 'data' and 'LHE_HT' in allVars:
        allVars.remove('LHE_HT')

    ## fill the PhysObjs with data from the root file
    ## fatjets vars
    for v in jetVars:
        jets[v] = pd.DataFrame(events.array(v))

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

    #for v in ak4JetVars:
    #    ak4Jets[v] = pd.DataFrame(events.array(v))

    ## fill muon physics objects (only for parked dataset)
    # muons['Muon_pt'] = pd.DataFrame(events.array('Muon_pt'))
    # muons['Muon_eta'] = pd.DataFrame(np.abs(events.array('Muon_eta')))
    # muons['Muon_ip3d'] = pd.DataFrame(events.array('Muon_ip3d'))
    # muons['Muon_softId'] = pd.DataFrame(events.array('Muon_softId')).fillna(0).astype(int)
    # muons['Muon_IP'] = pd.DataFrame(events.array('Muon_dxy')/events.array('Muon_dxyErr')).abs()


    ## gen particle
    Aid = 36
    bid = 5
    if 'ggH' == tag:
        pdgid = events.array('GenPart_pdgId')
        genPart['GenPart_pdgId'] = pd.DataFrame(pdgid)
        genPart['GenPartMother'] = pd.DataFrame(pdgid[events.array('GenPart_genPartIdxMother')])
        genPart['GenPart_eta'] = pd.DataFrame(events.array('GenPart_eta'))
        genPart['GenPart_phi'] = pd.DataFrame(events.array('GenPart_phi'))
        genPart['GenPart_status'] = pd.DataFrame(events.array('GenPart_status'))
        genPart['GenPart_pt'] = pd.DataFrame(events.array('GenPart_pt'))

    ## other vars
    if MC:
        other['LHE_HT'] = pd.DataFrame(events.array('LHE_HT')).astype(np.float64)
    for v in otherVars:
        other[v] = pd.DataFrame(events.array(v))

    ## make Event object
    ev = Event(jets, other, genPart) #ak4Jets, genPart)

    ## cutting events
    if 'ggH' == tag:
        genPart.cut(np.abs(genPart['GenPart_pdgId']) == 5)
        genPart.cut(genPart['GenPart_status'] == 23)


    ## jet cuts
    jets.cut(jets['FatJet_pt'] > 170)
    jets.cut(jets['FatJet_eta'].abs() < 2.4)
    # jets.cut(jets['FatJet_btagDDBvLV2'] > 0.8)
    # jets.cut(jets['FatJet_btagDeepB'] > 0.4184)
    # jets.cut(jets['FatJet_msoftdrop'] > 90)
    # jets.cut(jets['FatJet_msoftdrop'] < 200)#<= 200)
    # jets.cut(jets['FatJet_mass'] > 90)
    # jets.cut(jets['FatJet_mass'] <= 200)
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
    for v in otherVars:
        other[v] = other[v].rename({0:v}, axis='columns')
    #other.PV_npvs = other.PV_npvs.rename({0:'PV_npvs'}, axis='columns')
    #other.PV_npvsGood =other.PV_npvsGood.rename({0:'PV_npvsGood'}, axis='columns')


    ## sync so all events cut to same events after apply individual cuts
    ev.sync()

    if 'ggH' == tag:
        for i in genPart:
            genPart[i] = genPart[i].dropna(axis=1, how='all')

        ev.sync()


    ## return empty frame if nothing is left after cuts
    if jets.FatJet_pt.empty:
        return pd.DataFrame()

    else:

        ## Return only the highest pt physics objects and their related variables
        maxPtJets = getMaxPt(jets, 'FatJet_pt')
        #maxPtGenPart = getMaxPt(genPart, 'GenPart_pt')
        ## find a way to
        maxPtData = maxPtJets# pd.concat([maxPtJets, maxPtGenPart], axis=1)



        ## get each of the 4 genparts here???
        if 'ggH' == tag:
            pt = np.array(genPart['GenPart_pt'])
            eta = np.array(genPart['GenPart_eta'])
            pt2 = genPart['GenPart_pt'].to_numpy()
            ranking = np.argsort(pt)

            maxPtData = addGenPartToDf(ranking, genPart, 'GenPart_pt', maxPtData)
            maxPtData = addGenPartToDf(ranking, genPart, 'GenPart_eta', maxPtData)
            maxPtData = addGenPartToDf(ranking, genPart, 'GenPart_phi', maxPtData)
            maxPtData = addGenPartToDf(ranking, genPart, 'GenPart_pdgId', maxPtData)
            maxPtData = addGenPartToDf(ranking, genPart, 'GenPart_status', maxPtData)
            maxPtData = addGenPartToDf(ranking, genPart, 'GenPartMother', maxPtData)

        ## !!!!!!!!!! SI: MAYBE DO MUONS TOO !!!!!!!!!!!!!!!!!!!!!
        #maxPtMuons = getMaxPt(muons, 'Muon_pt')
        #maxPtData = pd.concat([maxPtJets, maxPtMuons], axis=1)

        maxPtData = maxPtData.assign(PV_npvs=other.PV_npvs.to_numpy())
        maxPtData = maxPtData.assign(PV_npvsGood=other.PV_npvsGood.to_numpy())
        maxPtData = maxPtData.assign(run=other.run.to_numpy())
        maxPtData = maxPtData.assign(luminosityBlock=other.luminosityBlock.to_numpy())
        maxPtData = maxPtData.assign(event=other.event.to_numpy())

        ## add index back into the df for comparison
        # maxPtData['eventNum'] = jets.FatJet_pt.index

        if MC:
            maxPtData = maxPtData.assign(LHE_HT=other.LHE_HT.to_numpy())

        ## applying weighing factors for MC to match data
        ## LHE_weights

        if 'ggH'==tag:
            maxPtData = maxPtData.assign(final_weights=1)

        if 'BGen'==tag:
            # just check the LHE HT of thefile and pply the right one
            lhe = maxPtData['LHE_HT'].iloc[0]
            for key in BGenWeights:
                if (lhe >= key[0]) and (lhe < key[1]):
                    weights = BGenWeights[key]


            # if (lhe >= 200) and (lhe < 300):
            #     weights = BGenWeights['200to300']
            # elif (lhe >=300) and (lhe < 500):
            #     weights = BGenWeights['300to500']
            # elif (lhe >= 500) and (lhe < 700):
            #     weights = BGenWeights['500to700']
            # elif (lhe >= 700) and (lhe < 1000):
            #     weights = BGenWeights['700to1000']
            # elif (lhe >= 1000) and (lhe < 1500):
            #     weights = BGenWeights['1000to1500']
            # elif (lhe >= 1500) and (lhe <2000):
            #     weights = BGenWeights['1500to2000']
            # else:
            #     weights = BGenWeights['2000toInf']

            maxPtData['LHE_weights'] = weights
            maxPtData['final_weights'] = weights
            # print(fileName)
            # key = re.search('QCD_HT(.*)_', fileName).group(1) ##find which HT range from filename
            # maxPtData['LHE_weights'] = BGenWeights[key]
            # for i in BGenDict:
            #     if i in fileName:
            #         key = i
            #         maxPtData['LHE_weights'] = BGenDict[key]
            # maxPtData = maxPtData.assign(final_weights = maxPtData['LHE_weights'])

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



    # make sure genpart has dr < 0.8 to the main fatjet
    if 'ggH' == tag:
        for i in range(1,5):
            maxPtData[f'dr{i}'] = calcDr(maxPtData['FatJet_phi'], maxPtData['FatJet_eta'], maxPtData[f'GenPart_phi{i}'], maxPtData[f'GenPart_eta{i}'])

        for i in range(1,5):
            maxPtData = maxPtData[maxPtData[f'dr{i}'] < 0.8]

    #maxPtData['FatJet_nSV'] = getnSVCounts(jets, events)
    maxPtData = maxPtData.dropna(how='all')
    #maxPtData = maxPtData.fillna(0)

    return maxPtData

def calcDr(phi1, eta1, phi2, eta2):
    ## dr^2 = (eta1-eta2)^2 + dphi^2
    dphi = np.abs(phi1-phi2)
    dphi[dphi>=np.pi] = 2*np.pi-dphi[dphi>=np.pi]
    return np.sqrt(np.square(eta1-eta2) + np.square(dphi))

## takes the argsort array (mostly likely argsort of the genpart pt), the genPart physics object,
## var to add to maxPtData (such as pt,eta,phi), then the maxPtData to add these variables to
## returns the maxPtData with the genPart variables added to it with var1 corresponding to the highest
## var by arg sort. such as eta1 is the eta of the highest pt if sorted by pt
def addGenPartToDf(ranking, genPart, v, maxPtData):
    arr = np.array(genPart[v])
    sorted = np.take_along_axis(arr, ranking, axis=1)
    num = {0:4, 1:3, 2:2, 3:1} ## need this because argsort only sorts ascending
    for i in range(3,-1,-1): #going from 3 to 0
        print(f'{v}_{num[i]}')
        maxPtData[f'{v}{num[i]}'] = sorted[:,i]

    return maxPtData
