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

#Non-linearity Correction for Good Vertices
p0=0.9633
p1=0.0529 
#Overall Scale for Good Vertices
N=0.8691
#Overall Scale Factor for Tight Vertices
Nt=1.7

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

tree.SetBranchStatus("nActiveBX", 1)
tree.SetBranchStatus("HFLumi", 1)
tree.SetBranchStatus("PLTLumi", 1)
tree.SetBranchStatus("PC_lumi_B3p8", 1)
tree.SetBranchStatus("goodVertices_Lumi", 1)
tree.SetBranchStatus("tightVertices_Lumi", 1)
tree.SetBranchStatus("validVertices_Lumi", 1)


Bin_idx={}
fill_dict={}
nBX_dict={}
hflumi_dict={}
pltlumi_dict={}
pclumi_dict={}
goodvtx_dict={}
tightvtx_dict={}
validvtx_dict={}

tightvtxpcc_dict={}


for iev in range(nentries):
    tree.GetEntry(iev)
    Bin_idx[(tree.run, tree.LS)]=runLS_keys.index((tree.run, tree.LS))
    fill_dict[(tree.run, tree.LS)]=tree.fill
    nBX_dict[(tree.run, tree.LS)]=tree.nActiveBX
    hflumi_dict[(tree.run, tree.LS)]=tree.HFLumi
    pltlumi_dict[(tree.run, tree.LS)]=tree.PLTLumi
    pclumi_dict[(tree.run, tree.LS)]=tree.PC_lumi_B3p8
    goodvtx_dict[(tree.run, tree.LS)]=tree.goodVertices_Lumi
    tightvtx_dict[(tree.run, tree.LS)]=tree.tightVertices_Lumi
    validvtx_dict[(tree.run, tree.LS)]=tree.validVertices_Lumi

nLS = len(Bin_idx)
combined_LS = 10
nLS = (int)(nLS/combined_LS)


histhfpc = ROOT.TH1F("histhfpc", ";Fill, Lumi Section; HF/PCC", nLS, 0, nLS)
histhfpc.Sumw2()

histhfgoodvtx = ROOT.TH1F("histhfgoodvtx", ";Fill, Lumi Section; HF/GoodVtx", nLS, 0, nLS)
histhfgoodvtx.Sumw2()

histhfgoodvtx_corr = ROOT.TH1F("histhfgoodvtx_corr", ";Fill, Lumi Section; HF/GoodVtx_Corr", nLS, 0, nLS)
histhfgoodvtx_corr.Sumw2()

histhftightvtx = ROOT.TH1F("histhftightvtx", ";Fill, Lumi Section; HF/TightVtx", nLS, 0, nLS)
histhftightvtx.Sumw2()

histhfvalidvtx = ROOT.TH1F("histhfvalidvtx", ";Fill, Lumi Section; HF/ValidVtx", nLS, 0, nLS)
histhfvalidvtx.Sumw2()

histpltpc = ROOT.TH1F("histpltpc", ";Fill, Lumi Section; PLT/PCC", nLS, 0, nLS)
histpltpc.Sumw2()

histpltgoodvtx = ROOT.TH1F("histpltgoodvtx", ";Fill, Lumi Section; PLT/GoodVtx", nLS, 0, nLS)
histpltgoodvtx.Sumw2()

histpltgoodvtx_corr = ROOT.TH1F("histpltgoodvtx_corr", ";Fill, Lumi Section; PLT/GoodVtx_corr", nLS, 0, nLS)
histpltgoodvtx_corr.Sumw2()

histplttightvtx =ROOT.TH1F("histplttightvtx", ";Fill, Lumi Section; PLT/TightVtx", nLS, 0, nLS)
histplttightvtx.Sumw2()

histpltvalidvtx = ROOT.TH1F("histpltvalidvtx", ";Fill, Lumi Section; PLT/ValidVtx", nLS, 0, nLS)
histpltvalidvtx.Sumw2()
 
gra_goodvtxpcc = ROOT.TGraph()
gra_tightvtxpcc = ROOT.TGraph()

pro_goodvtxpcc = ROOT.TProfile("ratio_goodvtxpcc", "goodvtx/PCC; PCC Lumi; GoodVtx Lumi/PCC", 100, 0, 5)
pro_pccgoodvtx = ROOT.TProfile("ratio_pccgoodvtx", "PCC/goodvtx; GoodVtx Lumi; PCC/GoodVtx Lumi", 100, 0, 5)

pro_hfgoodvtxcorr = ROOT.TProfile("ratio_hfgoodvtxcorr", "HF/goodvtx_corr; HF/GoodVtx Lumi (Corrected)", 100, 0, 5)

pro_tightvtxpcc = ROOT.TProfile("ratio_tightvtxpcc", "tightvtx/PCC; PCC Lumi; TightVtx Lumi/PCC", 100, 0, 5)

pro_pcctightvtx = ROOT.TProfile("ratio_pcctightvtx", "PCC/tightvtx; TightVtx Lumi; TightVtx Lumi/PCC", 100, 0, 5)

count=0
sum_hflumi=0
sum_pltlumi=0
sum_pclumi=0
sum_goodvtx=0
sum_goodvtx_corr=0
sum_tightvtx=0
sum_validvtx=0

pre_run=0
iPoint = 0

for key in runLS_keys:
    cur_run=fill_dict[key]#key[0]
    if cur_run!=pre_run:
        histhfpc.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histpltpc.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histhfgoodvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histpltgoodvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run))
        histhfgoodvtx_corr.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1, str(cur_run))
        histpltgoodvtx_corr.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1, str(cur_run))
        histhftightvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run))
        histplttightvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run))
        histhfvalidvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 
        histhfvalidvtx.GetXaxis().SetBinLabel((int)(Bin_idx[key]/combined_LS)+1,str(cur_run)) 

    if count < combined_LS:
        sum_hflumi+=hflumi_dict[key]
        sum_pltlumi+=pltlumi_dict[key]
        sum_pclumi+=pclumi_dict[key]
        sum_goodvtx+=goodvtx_dict[key]
        sum_tightvtx+=1.7*tightvtx_dict[key]
        sum_validvtx+=validvtx_dict[key]
        
        if nBX_dict[key]!=0:
            SBIL_goodvtx=goodvtx_dict[key]/nBX_dict[key]
            sum_goodvtx_corr+=N*(p0*SBIL_goodvtx+p1*SBIL_goodvtx*SBIL_goodvtx)*nBX_dict[key]
            print sum_goodvtx, sum_goodvtx_corr

    if count == combined_LS-1:
        if sum_pclumi!=0: 
            histhfpc.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_pclumi)
            histpltpc.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_pclumi)

            if nBX_dict[key]!=0:
                gra_goodvtxpcc.SetPoint(iPoint, sum_pclumi/combined_LS/nBX_dict[key], sum_goodvtx/sum_pclumi)
                gra_tightvtxpcc.SetPoint(iPoint, sum_pclumi/combined_LS/nBX_dict[key], sum_tightvtx/sum_pclumi)
                pro_goodvtxpcc.Fill(sum_pclumi/combined_LS/nBX_dict[key], sum_goodvtx/sum_pclumi, 1)
                pro_pccgoodvtx.Fill(sum_goodvtx/combined_LS/nBX_dict[key], sum_pclumi/sum_goodvtx, 1)
                pro_hfgoodvtxcorr.Fill(sum_goodvtx_corr/combined_LS/nBX_dict[key], sum_hflumi/sum_goodvtx_corr, 1)
                pro_tightvtxpcc.Fill(sum_pclumi/combined_LS/nBX_dict[key], sum_tightvtx/sum_pclumi, 1)
                pro_pcctightvtx.Fill(sum_tightvtx/combined_LS/nBX_dict[key], sum_pclumi/sum_tightvtx, 1)
            
            iPoint+=1

        if sum_goodvtx!=0:
            histhfgoodvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_goodvtx)
            histpltgoodvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_goodvtx)

        if sum_goodvtx_corr!=0:
            histhfgoodvtx_corr.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_goodvtx_corr)
            histpltgoodvtx_corr.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_goodvtx_corr)

        if sum_tightvtx!=0:
            histhftightvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_tightvtx)
            histplttightvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_tightvtx)
        
        if sum_validvtx!=0:
            histhfvalidvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_hflumi/sum_validvtx)
            histpltvalidvtx.Fill((int)(Bin_idx[key]/combined_LS), sum_pltlumi/sum_validvtx)
    
    pre_run = fill_dict[key]#key[0]
    if count!=combined_LS-1:
        count+=1
    else:
        sum_hflumi=0
        sum_pltlumi=0
        sum_pclumi=0
        sum_goodvtx=0
        sum_goodvtx_corr=0
        sum_tightvtx=0
        sum_validvtx=0
        count=0

histhfpc.SetMarkerSize(0.4)
histhfpc.SetMarkerColor(ROOT.kBlue)
histhfpc.SetMarkerStyle(23)
histhfpc.GetXaxis().SetNdivisions(404)

histpltpc.SetMarkerSize(0.4)
histpltpc.SetMarkerColor(ROOT.kBlue)
histpltpc.SetMarkerStyle(23)
histpltpc.GetXaxis().SetNdivisions(404)

histhfgoodvtx.SetMarkerSize(0.4)
histhfgoodvtx.SetMarkerColor(ROOT.kBlue)
histhfgoodvtx.SetMarkerStyle(23)
histhfgoodvtx.GetXaxis().SetNdivisions(404)

histpltgoodvtx.SetMarkerSize(0.4)
histpltgoodvtx.SetMarkerColor(ROOT.kBlue)
histpltgoodvtx.SetMarkerStyle(23)
histpltgoodvtx.GetXaxis().SetNdivisions(404)

histhfgoodvtx_corr.SetMarkerSize(0.4)
histhfgoodvtx_corr.SetMarkerColor(ROOT.kBlue)
histhfgoodvtx_corr.SetMarkerStyle(23)
histhfgoodvtx_corr.GetXaxis().SetNdivisions(404)

histpltgoodvtx_corr.SetMarkerSize(0.4)
histpltgoodvtx_corr.SetMarkerColor(ROOT.kBlue)
histpltgoodvtx_corr.SetMarkerStyle(23)
histpltgoodvtx_corr.GetXaxis().SetNdivisions(404)

histhftightvtx.SetMarkerSize(0.4)
histhftightvtx.SetMarkerColor(ROOT.kBlue)
histhftightvtx.SetMarkerStyle(23)
histhftightvtx.GetXaxis().SetNdivisions(404)

histplttightvtx.SetMarkerSize(0.4)
histplttightvtx.SetMarkerColor(ROOT.kBlue)
histplttightvtx.SetMarkerStyle(23)
histplttightvtx.GetXaxis().SetNdivisions(404)

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
    histhfgoodvtx_corr.SetBinError(nbin, 0)
    histpltgoodvtx_corr.SetBinError(nbin, 0)
    histhftightvtx.SetBinError(nbin,0)
    histplttightvtx.SetBinError(nbin,0)
    histhfvalidvtx.SetBinError(nbin,0)
    histpltvalidvtx.SetBinError(nbin,0)

histhfpc.GetYaxis().SetRangeUser(0.7,1.2)
histpltpc.GetYaxis().SetRangeUser(0.7,1.2)

histhfgoodvtx.GetYaxis().SetRangeUser(0.7, 1.2)
histpltgoodvtx.GetYaxis().SetRangeUser(0.7, 1.2)

histhfgoodvtx_corr.GetYaxis().SetRangeUser(0.7, 1.2)
histpltgoodvtx_corr.GetYaxis().SetRangeUser(0.7, 1.2)

histhftightvtx.GetYaxis().SetRangeUser(0.7, 1.2)
histplttightvtx.GetYaxis().SetRangeUser(0.7, 1.2)

histhfvalidvtx.GetYaxis().SetRangeUser(0.7, 1.2)
histpltvalidvtx.GetYaxis().SetRangeUser(0.7, 1.2)

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

tcan.Clear()
tcan.Update()
histhfgoodvtx_corr.Draw("P")
tcan.SaveAs("ratio_hfgoodvtx_corr_"+args.label+".png")
tcan.SaveAs("ratio_hfgoodvtx_corr_"+args.label+".eps")

tcan.Clear()
tcan.Update()
histpltgoodvtx_corr.Draw("P")
tcan.SaveAs("ratio_pltgoodvtx_corr_"+args.label+".png")
tcan.SaveAs("ratio_pltgoodvtx_corr_"+args.label+".eps")


tcan.Clear()
tcan.Update()
histhftightvtx.Draw("P")
tcan.SaveAs("ratio_hftightvtx_"+args.label+".png")
tcan.SaveAs("ratio_hftightvtx_"+args.label+".eps")

tcan.Clear()
tcan.Update()
histplttightvtx.Draw("P")
tcan.SaveAs("ratio_plttightvtx_"+args.label+".png")
tcan.SaveAs("ratio_plttightvtx_"+args.label+".png")

#histhfpc.Draw()
newfile.WriteTObject(histhfpc, "histhfpc")
newfile.WriteTObject(histpltpc, "histpltpc")
newfile.WriteTObject(histhfgoodvtx, "histhfgoodvtx")
newfile.WriteTObject(histpltgoodvtx, "histpltgoodvtx")
newfile.WriteTObject(histhfgoodvtx_corr, "histhfgoodvtx_corr")
newfile.WriteTObject(histpltgoodvtx_corr, "histpltgoodvtx_corr")
newfile.WriteTObject(histhftightvtx, "histhftightvtx")
newfile.WriteTObject(histplttightvtx, "histplttightvtx")
newfile.WriteTObject(histhfvalidvtx, "histhfvalidvtx")
newfile.WriteTObject(histpltvalidvtx, "histpltvalidvtx")
newfile.WriteTObject(gra_goodvtxpcc, "gra_goodvtxpcc")
newfile.WriteTObject(gra_tightvtxpcc, "gra_tightvtxpcc")
newfile.WriteTObject(pro_goodvtxpcc, "pro_goodvtxpcc")
newfile.WriteTObject(pro_pccgoodvtx, "pro_pccgoodvtx")
newfile.WriteTObject(pro_hfgoodvtxcorr, "pro_hfgoodvtxcorr")
newfile.WriteTObject(pro_tightvtxpcc, "pro_tightvtxpcc")
newfile.WriteTObject(pro_pcctightvtx, "pro_pcctightvtx")

newfile.Close()
