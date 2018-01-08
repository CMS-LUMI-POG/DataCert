import sys
import ROOT

#example call to brilcalc
#brilcalc lumi --normtag=pccLUM15001 -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-274443_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt -u 'hz/ub' -o pcc.csv --output-style=csv --byls --tssec
ROOT.gROOT.SetBatch(ROOT.kTRUE)

def dictFromCSVFile(file):
    lines=file.readlines()
    dict={}
    for line in lines:
        try:
            items=line.replace(':',',').split(",")
            dict[(int(items[1]),int(items[0]),int(items[2]))]=[int(items[4]),float(items[8])]
        except:
            pass
    return dict

filename1=sys.argv[1]
filename2=sys.argv[2]
nBXfileName=sys.argv[3]
filelabel=str(sys.argv[4])

NBXPerFill={}
nbxfile=open(nBXfileName)
for line in nbxfile.readlines():
    items=line.split(",")
    try:
        fill=int(items[0])
        NBX=int(items[1])
        NBXPerFill[fill]=NBX
    except:
        print "Problem with line",line

nbxfile.close()

nBX=1
tLS=23.31

requireContinuity=True

time0=0

file1=open(filename1)
file2=open(filename2)

dict1=dictFromCSVFile(file1)
dict2=dictFromCSVFile(file2)

total1=0
total2=0

total1PerFill={}
total2PerFill={}

overtlapKeys=list(set(dict1).intersection(dict2))
overtlapKeys.sort()

print len(dict1),len(dict2),len(overtlapKeys)

label=filename2.split("_")[0]+"/"+filename1.split("_")[0]
combineNLS=15

can=ROOT.TCanvas("can","",1400,700)
ratio=ROOT.TH1F("ratio",";ratio "+label+";",200,0,2)

narrowWidth=0.05
ratioNarrow=ROOT.TH1F("ratioNarrow",";Ratio of luminosities per "+str(combineNLS)+" LS;Integrated lumi (fb^{-1})",200,1-narrowWidth,1+narrowWidth)
#these are place holders, to gather averages, should be an easier way to do this
ratioNarrowRun=ROOT.TH1F("ratioNarrowRun",";ratio "+label+";",300,0.85,1.15)
ratioNarrowFill=ROOT.TH1F("ratioNarrowFill",";ratio "+label+";",300,0.85,1.15)
#these are the actual histograms filled by these placeholder averages

ratioVsTime=ROOT.TGraph()
ratioVsInst=ROOT.TGraph()
ratioVsInstProfile=ROOT.TProfile("ratioVsInstProfile",";Average Inst. Luminosity (Hz/#muB);Average "+label,50,0,8)
ratioVsTime.SetTitle(label+";Time (s);Ratio per "+str(combineNLS))
ratioVsInst.SetTitle(";Average Inst. Luminosity (Hz/#muB);"+label)
ratioVsInst_perFill={}

fout = ROOT.TFile(str(sys.argv[4])+"_monitor_plots.root", "recreate")

baddies={}
veryOffLS={}
iCount=1
iBin=0
num=0
den=0
iRatio=0

averageRatioOfRun=0
averageRatioOfFill=0
currentRun=1
currentFill=1
binRun=0
binFill=0

ratioRun=ROOT.TGraphErrors()
ratioFill=ROOT.TGraphErrors()
ratioRun.SetTitle(label+";Run;Ratio")
ratioFill.SetTitle(label+";Fill;Ratio")

lastlumi=-99
lastratio=0
nSkipped=0
totSkipped=0
for key in overtlapKeys:
    try:
        if not total1PerFill.has_key(key[0]):
            print "setting total to 0 for fill", key[0]
            total1PerFill[key[0]]=0
            total2PerFill[key[0]]=0
        if iCount==1:
            time0=dict1[key][0]
            currentFill=key[0]
            currentRun=key[1]
        newKey=(key[0],key[1])
        newKey=key[0]
        if not ratioVsInst_perFill.has_key(newKey):
            ratioVsInst_perFill[newKey]=ROOT.TGraph()
            iRatio=0
            lastlumi=-99
            lastratio=0
        if requireContinuity:
            if lastlumi/NBXPerFill[key[0]]>1.5 and abs(dict1[key][1]/lastlumi-1) > 0.02:
                print "SKIPPING BECAUSE CHANGE TOO GREAT", dict1[key][1], lastlumi
                lastlumi=dict1[key][1]
                lastratio=dict1[key][1]/dict2[key][1]
                nSkipped=nSkipped+1
                totSkipped=totSkipped+dict1[key][1]*tLS/1.e9
                continue
            elif lastlumi/NBXPerFill[key[0]]>1.5 and abs(dict1[key][1]/dict2[key][1]-lastratio) > 0.02:
                print "SKIPPING BECAUSE RATIO CHANGED TOO MUCH", dict1[key][1], lastratio
                lastlumi=dict1[key][1]
                lastratio=dict1[key][1]/dict2[key][1]
                nSkipped=nSkipped+1
                totSkipped=totSkipped+dict1[key][1]*tLS/1.e9
                continue
            elif dict1[key][1]/NBXPerFill[key[0]]<1.5:
                print "SKIPPING BECAUSE TOO LOW", dict1[key][1]/NBXPerFill[key[0]]
                lastlumi=dict1[key][1]
                nSkipped=nSkipped+1
                lastratio=dict1[key][1]/dict2[key][1]
                totSkipped=totSkipped+dict1[key][1]*tLS/1.e9
                continue
        
        lastratio=dict1[key][1]/dict2[key][1]
        lastlumi=dict1[key][1]
       
 
        if abs(dict1[key][1]/dict2[key][1]-1)>.05:
            if newKey not in baddies:
                baddies[newKey]=1
            else:
                baddies[newKey]=baddies[newKey]+1
        #print key,dict1[key][1]/dict2[key][1]
        if abs(dict1[key][1]/dict2[key][1]-1)>.5:
            if not veryOffLS.has_key(key[1]):
                veryOffLS[key[1]]=[]
            veryOffLS[key[1]].append(key[2])
            print "50 % off",key, dict1[key][1], dict2[key][1]
            continue
        num=num+dict2[key][1]
        den=den+dict1[key][1]
        total2=total2+dict2[key][1]*tLS*1.e-9
        total1=total1+dict1[key][1]*tLS*1.e-9
        total1PerFill[key[0]]=total1PerFill[key[0]]+dict1[key][1]*tLS*1.e-9
        total2PerFill[key[0]]=total2PerFill[key[0]]+dict2[key][1]*tLS*1.e-9

        if iCount%combineNLS==0:
            ratio.Fill(num/den)
            ratioNarrow.Fill(num/den,den*tLS)
            ratioNarrowRun.Fill(num/den,den*tLS)
            ratioNarrowFill.Fill(num/den,den*tLS)
            ratioVsTime.SetPoint(iBin,dict1[key][0]-time0,num/den)
            ratioVsInst.SetPoint(iBin,den/NBXPerFill[key[0]]/combineNLS,num/den)
            ratioVsInstProfile.Fill(den/NBXPerFill[key[0]]/combineNLS,num/den)
            print "fill",key,iRatio, den/NBXPerFill[key[0]]/combineNLS,num/den
            ratioVsInst_perFill[newKey].SetPoint(iRatio, den/NBXPerFill[key[0]]/combineNLS,num/den)
            num=0
            den=0
            iBin=iBin+1
            iRatio=iRatio+1

            if currentRun != key[1]:
                ratioRun.SetPoint(binRun,currentRun,ratioNarrowRun.GetMean())
                if ratioNarrowRun.GetMean()>1.03 or ratioNarrowRun.GetMean()<0.97:
                    print currentRun
                currentRun = key[1]
                binRun = binRun + 1
                ratioNarrowRun.Reset()
            if currentFill != key[0]:
                print currentFill,total1PerFill[currentFill],total2PerFill[currentFill]
                if ratioNarrowFill.GetMean()>0.5:
                    ratioFill.SetPoint(binFill,currentFill,ratioNarrowFill.GetMean())
                    binFill=binFill+1
                else: 
                    print key[0],"mean",ratioNarrowFill.GetMean(),"skipping"
                currentFill = key[0]
                ratioNarrowFill.Reset()

        iCount=iCount+1

    except:
        pass

print "TOTAL SKIPPED",nSkipped,totSkipped
print "total",total1,total2,total1/total2
offRuns=veryOffLS.keys()
offRuns.sort()
for run in offRuns:
    veryOffLS[run].sort()
    print run,veryOffLS[run]

slightlyOffRuns=baddies.keys()
slightlyOffRuns.sort()
"# LS off by a few percent"
for run in slightlyOffRuns:
    print run,baddies[run]


ratioVsInst.GetYaxis().SetRangeUser(0.95,1.05)
ratioVsInst.GetXaxis().SetRangeUser(2,8)
ratioVsInst.Draw("AP")
can.Update()
can.SaveAs(filelabel+"_vsInstLumi.png")


fout.WriteTObject(can,filelabel+"_vsInstLumi.png")
ratioVsInstProfile.SetLineColor(ROOT.kRed)
ratioVsInstProfile.Draw()
#ratioVsInstProfile.GetYaxis().SetRangeUser(0.95,1.08)
#p3 = ROOT.TF1("p3","[0]*x+[1]*x*x+[2]*x*x*x",0,10)
ratioVsInstProfile.Fit("pol1")
can.Update()
can.SaveAs(filelabel+"_vsInstLumiPro.png")
fout.WriteTObject(can,filelabel+"_vsInstLumiPro.png")
ratio.Draw()
can.Update()
ratioNarrow.Scale(1.e-9)
ratioNarrow.Draw("hist")
print "binned ratio Integral(/fb), MEAN, RMS",ratioNarrow.Integral(),ratioNarrow.GetMean(),ratioNarrow.GetRMS()
can.Update()
can.SaveAs(filelabel+"_binnedRatio.png")
fout.WriteTObject(can,filelabel+"_binnedRatio.png")
ratioVsTime.Draw("AP")
can.Update()
can.SaveAs(filelabel+"_vsTime.png")
fout.WriteTObject(can,filelabel+"_vsTime.png")


line_Plot = ROOT.TGraphErrors()
ip=0
line_hist_weighted = ROOT.TH1F("line_hist_weighted", "Slopes weighted by lumi;Slope [(Hz/ub)^{-1}];Integrated Lumi (fb^{-1})", 100, -0.015, 0.015)
line_hist = ROOT.TH1F("line_hist", "line_hist", 100, -0.015, 0.015)
for key_fill in ratioVsInst_perFill.keys():
    try:
        if ratioVsInst_perFill[key_fill].GetN() < 12:
            continue
        ratioVsInst_perFill[key_fill].Fit("pol1", "M")
        fitResult = ratioVsInst_perFill[key_fill].GetFunction("pol1")
        #ratioVsInst_perFill[key_fill].Draw()
        #can.Update
        #can.SaveAs(filelabel+"Linearity_"+str(key_fill)+".png")
        value = fitResult.GetParameter(1)
        error = fitResult.GetParError(1)
        if error> 0.0008:
            print "large error",key_fill
        #    continue
        line_Plot.SetPoint(ip, float(key_fill), value)
        line_Plot.SetPointError(ip, 0, error)
        line_hist_weighted.Fill(value, total1PerFill[key_fill])
        line_hist.Fill(value)
        fout.WriteTObject(ratioVsInst_perFill[key_fill], "ratio"+str(key_fill))
        ip+=1
        line_Plot.GetXaxis().SetTitle("Fill Number")
    except:
        print "give up"

can.Update
can.SetTickx()
can.SetTicky()
line_Plot.SetMarkerStyle(ROOT.kFullCircle)
line_Plot.GetYaxis().SetRangeUser(-0.02, 0.02)
line_Plot.GetYaxis().SetTitle("Slope [(Hz/ub)^{-1}]")
line_Plot.GetXaxis().SetTitle("Fill Number")
line_Plot.Draw("APE")
can.SaveAs(filelabel+"Linearity_perFill.png")
fout.WriteTObject(can,"linearity_perFill")


ratioRun.Draw("APE")
can.SaveAs(filelabel+"_ratioPerRun.png")

ratioFill.Draw("APE")
can.SaveAs(filelabel+"_ratioPerFill.png")

line_hist_weighted.Draw("hist")
print "mean slope, rms",line_hist_weighted.GetMean(),line_hist_weighted.GetRMS()
can.SaveAs(filelabel+"_binnedLinearity.png")

fout.WriteTObject(line_Plot,"line_Plot")
fout.WriteTObject(line_hist,"line_hist")
fout.WriteTObject(line_hist_weighted,"line_hist_wighted")
fout.WriteTObject(ratioVsTime,"ratioVsTime")
fout.WriteTObject(ratioVsInst,"ratioVsInst")
fout.WriteTObject(ratioVsInstProfile,"ratioVsInstProfile")
fout.WriteTObject(ratioRun,"ratioRun")
fout.WriteTObject(ratioFill,"ratioFill")
fout.Close()
