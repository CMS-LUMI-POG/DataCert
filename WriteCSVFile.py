import ROOT
import sys
import math
import numpy
import argparse


parser = argparse.ArgumentParser(description = 'Make the csv file for PCC and Pixel Vertex Counting')
parser.add_argument('-c', '--certfile', type=str, default="", help='The data certification tree')
parser.add_argument('-b', '--batch', action='store_true', default=False, help='Batch Mode')
parser.add_argument('-l', '--label', type=str, default="", help='The label of the output files')

args = parser.parse_args()

if args.batch is True:
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    scale=4

filename=args.certfile
tfile=ROOT.TFile(filename)
tree=tfile.Get("certtree")

outfile=open("LUMI_"+args.label+".csv", "w")

tree.SetBranchStatus("*", 0)
tree.SetBranchStatus("fill", 1)
tree.SetBranchStatus("run", 1)
tree.SetBranchStatus("LS", 1)

nentries = tree.GetEntries()

runLS_keys = []

for iev in range(nentries):
    tree.GetEntry(iev)
    runLS_keys.append((tree.run, tree.LS))

runLS_keys.sort()

tree.SetBranchStatus("HFLumi", 1)
tree.SetBranchStatus("PLTLumi", 1)
tree.SetBranchStatus("PC_lumi_B3p8", 1)
tree.SetBranchStatus("goodVertices_Lumi", 1)


hflumi_dict={}
pltlumi_dict={}
pclumi_dict={}
goodvtx_dict={}

for iev in range(nentries):
    tree.GetEntry(iev)
    hflumi_dict[(tree.run, tree.LS)] = tree.HFLumi
    pltlumi_dict[(tree.run, tree.LS)] = tree.PLTLumi
    pclumi_dict[(tree.run, tree.LS)] = tree.PC_lumi_B3p8
    goodvtx_dict[(tree.run, tree.LS)] = tree.goodVertices_Lumi
    

for key in runLS_keys:
    outfile.write("run,"+str(key[0])+",LS,"+str(key[1])+",HFLumi,"+str(hflumi_dict[key])+",PLTLumi,"+str(pltlumi_dict[key])+",PCCLumi,"+str(pclumi_dict[key])+",GoodVtxLumi,"+str(goodvtx_dict[key])+"\n")


outfile.close()



