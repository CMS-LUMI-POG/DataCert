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

#Non-linearity Correction for Good Vertices
p0=0.9633
p1=0.0529
#Overall Scale for Good Vertices
N=0.8691
#Overall Scale Factor for Tight Vertices
Nt=1.7

for iev in range(nentries):
    tree.GetEntry(iev)
    runLS_keys.append((tree.run, tree.LS))



runLS_keys.sort()
tree.SetBranchStatus("nActiveBX", 1)
tree.SetBranchStatus("HFLumi", 1)
tree.SetBranchStatus("PLTLumi", 1)
tree.SetBranchStatus("PC_lumi_B3p8", 1)
tree.SetBranchStatus("goodVertices_Lumi", 1)
tree.SetBranchStatus("tightVertices_Lumi", 1)


nBX_dict={}
hflumi_dict={}
pltlumi_dict={}
pclumi_dict={}
goodvtx_dict={}
tightvtx_dict={}


for iev in range(nentries):
    tree.GetEntry(iev)
    nBX_dict[(tree.run, tree.LS)] = tree.nActiveBX
    hflumi_dict[(tree.run, tree.LS)] = tree.HFLumi
    pltlumi_dict[(tree.run, tree.LS)] = tree.PLTLumi
    pclumi_dict[(tree.run, tree.LS)] = tree.PC_lumi_B3p8
    goodvtx_dict[(tree.run, tree.LS)] = tree.goodVertices_Lumi
    tightvtx_dict[(tree.run, tree.LS)] = tree.tightVertices_Lumi
    

for key in runLS_keys:
    SBIL_goodvtx=  goodvtx_dict[key]/nBX_dict[key]
    outfile.write("run,"+str(key[0])+",LS,"+str(key[1])+",HFLumi,"+str(hflumi_dict[key])+",PLTLumi,"+str(pltlumi_dict[key])+",PCCLumi,"+str(pclumi_dict[key])+",GoodVtxLumi,"+str(goodvtx_dict[key])+",TightVtxLumi,"+str(Nt*tightvtx_dict[key])+",GoodVtxLumi_Corr,"+str(N*(p0*SBIL_goodvtx+p1*SBIL_goodvtx*SBIL_goodvtx)*nBX_dict[key])+",nActiveBX,"+str(nBX_dict[key])+"\n")


outfile.close()



