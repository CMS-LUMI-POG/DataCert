import ROOT
import sys
import math
import numpy
import argparse



parser = argparse.ArgumentParser(description = 'Make the Stability Plots')

parser.add_argument('-c', '--certfile', type=str, default="", help='The data certification tree')
parser.add_argument('-b', '--batch', action='store_true', default=False, help='Batch Mode')
parser.add_argument('-l', '--label', type=str, default="", help='The label of the output files')

args = parser.parse_args()

ROOT.gStyle.SetPadTickY(2)
ROOT.gStyle.SetOptStat(0)

if args.batch is True:
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    scale=4

filename=args.certfile
tfile=ROOT.TFile(filename)
tree=tfile.Get("certtree")

newfile=ROOT.TFile.Open("Ratio_Plots_"+args.label+".root", "recreate")

tcan = ROOT.TCanvas("ratio", "", 1200, 700)
tcan.cd()
tcan.SetTickx()

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
tree.SetBranchStatus("validVertices_Lumi", 1)

Bin_idx={}
hflumi_dict={}
pltlumi_dict={}
pclumi_dict={}
goodvtx_dict={}
validvtx_dict={}

for iev in range(nentries):
    tree.GetEntry(iev)
    Bin_idx[(tree.run, tree.LS)]=runLS_keys.index((tree.run, tree.LS))
    hflumi_dict[(tree.run, tree.LS)]=tree.HFLumi
    pltlumi_dict[(tree.run, tree.LS)]=tree.PLTLumi
    pclumi_dict[(tree.run, tree.LS)]=tree.PC_lumi_B3p8
    goodvtx_dict[(tree.run, tree.LS)]=tree.goodVertices_Lumi
    validvtx_dict[(tree.run, tree.LS)]=tree.validVertices_Lumi

nLS = len(Bin_idx)
combined_LS = 10
nLS = (int)(nLS/combined_LS)

histhfpc = ROOT.TH1F("histhfpc", ";Run, Lumi Section; HF/PCC", nLS, 0, nLS)
histhfpc.Sumw2()
histhfgoodvtx = ROOT.TH1F("histhfgoodvtx", ";Run, Lumi Section; HF/GoodVtx", nLS, 0, nLS)
histhfgoodvtx.Sumw2()

histhfvalidvtx = ROOT.TH1F("histhfvalidvtx", ";Run, Lumi Section; HF/ValidVtx", nLS, 0, nLS)
histhfvalidvtx.Sumw2()

histpltpc = ROOT.TH1F("histpltpc", ";Run, Lumi Section; PLT/PCC", nLS, 0, nLS)
histpltpc.Sumw2()

histpltgoodvtx = ROOT.TH1F("histpltgoodvtx", ";Run, Lumi Section; PLT/GoodVtx", nLS, 0, nLS)
histpltgoodvtx.Sumw2()

histpltvalidvtx = ROOT.TH1F("histpltvalidvtx", ";Run, Lumi Section; PLT/ValidVtx", nLS, 0, nLS)
histpltvalidvtx.Sumw2()
 

count=0
sum_hflumi=0
sum_pltlumi=0
sum_pclumi=0
sum_goodvtx=0
sum_validvtx=0

pre_run=0
for key in runLS_keys:
    print key, count
    cur_run=key[0]
    if cur_run!=pre_run:
        histhfpc.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histpltpc.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histhfgoodvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histpltgoodvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histhfvalidvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histhfvalidvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 

    if count < combined_LS:
        sum_hflumi+=hflumi_dict[key]
        sum_pltlumi+=pltlumi_dict[key]
        sum_pclumi+=pclumi_dict[key]
        sum_goodvtx+=goodvtx_dict[key]
        sum_validvtx+=validvtx_dict[key]

    if count == combined_LS-1:
        print sum_pclumi    
        if sum_pclumi!=0: 
            histhfpc.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_pclumi)
            histpltpc.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_pclumi)

        if sum_goodvtx!=0:
            histhfgoodvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_goodvtx)
            histpltgoodvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_goodvtx)
        
        if sum_validvtx!=0:
            histhfvalidvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_validvtx)
            histpltvalidvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_validvtx)
    
    pre_run = key[0]
    if count!=combined_LS-1:
        count+=1
    else:
        sum_hflumi=0
        sum_pltlumi=0
        sum_pclumi=0
        sum_goodvtx=0
        sum_validvtx=0
        count=0

histhfpc.SetMarkerColor(ROOT.kBlue)
histhfpc.SetMarkerStyle(23)

histpltpc.SetMarkerColor(ROOT.kBlue)
histpltpc.SetMarkerStyle(23)

histhfgoodvtx.SetMarkerColor(ROOT.kBlue)
histhfgoodvtx.SetMarkerStyle(23)

histpltgoodvtx.SetMarkerColor(ROOT.kBlue)
histpltgoodvtx.SetMarkerStyle(23)

    #if pclumi_dict[key] !=0:
    #    print Bin_idx[key], hflumi_dict[key], pclumi_dict[key]
        
        #histhfpc.Fill(Bin_idx[key], hflumi_dict[key]/pclumi_dict[key])
        #histpltpc.Fill(Bin_idx[key], pltlumi_dict[key]/pclumi_dict[key])

    #if goodvtx_dict[key] !=0:
        #histhfgoodvtx.Fill(Bin_idx[key], hflumi_dict[key]/goodvtx_dict[key])
        #histpltgoodvtx.Fill(Bin_idx[key], pltlumi_dict[key]/goodvtx_dict[key])

    #if validvtx_dict[key] !=0:
        #histhfvalidvtx.Fill(Bin_idx[key], hflumi_dict[key]/goodvtx_dict[key])
        #histpltvalidvtx.Fill(Bin_idx[key], pltlumi_dict[key]/validvtx_dict[key])

for nbin in range(nLS):
    histhfpc.SetBinError(nbin,0)
    histpltpc.SetBinError(nbin,0)
    histhfgoodvtx.SetBinError(nbin,0)
    histpltgoodvtx.SetBinError(nbin,0)
    histhfvalidvtx.SetBinError(nbin,0)
    histpltvalidvtx.SetBinError(nbin,0)

histhfpc.GetYaxis().SetRangeUser(0.7,1.2)
histpltpc.GetYaxis().SetRangeUser(0.7,1.2)

histhfgoodvtx.GetYaxis().SetRangeUser(0.7, 1.2)
histpltgoodvtx.GetYaxis().SetRangeUser(0.7, 1.2)

histhfpc.Draw("P")
tcan.SaveAs("ratio_hfpc_"+args.label+".png")
tcan.SaveAs("ratio_hfpc_"+args.label+".eps")

tcan.Clear()
tcan.Update()
histpltpc.Draw("P")
tcan.SaveAs("ratio_pltpc_"+args.label+".png")
tcan.SaveAs("ratio_pltpc_"+args.label+".eps")

tcan.Clear()
tcan.Update()
histhfgoodvtx.Draw("P")
tcan.SaveAs("ratio_hfgoodvtx_"+args.label+".png")
tcan.SaveAs("ratio_hfgoodvtx_"+args.label+".eps")

tcan.Clear()
tcan.Update()
histpltgoodvtx.Draw("P")
tcan.SaveAs("ratio_pltgoodvtx_"+args.label+".png")
tcan.SaveAs("ratio_pltgoodvtx_"+args.label+".eps")
#histhfpc.Draw()
newfile.WriteTObject(histhfpc, "histhfpc")
newfile.WriteTObject(histpltpc, "histpltpc")
newfile.WriteTObject(histhfgoodvtx, "histhfgoodvtx")
newfile.WriteTObject(histpltgoodvtx, "histpltgoodvtx")
newfile.WriteTObject(histhfvalidvtx, "histhfvalidvtx")
newfile.WriteTObject(histpltvalidvtx, "histpltvalidvtx")

newfile.Close()
