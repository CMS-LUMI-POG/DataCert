import sys
import ROOT


#example call to brilcalc
#brilcalc lumi --normtag=pccLUM15001 -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-274443_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt -u 'hz/ub' -o pcc.csv --output-style=csv --byls --tssec

def dictFromCSVFile(file):
    lines=file.readlines()
    dict={}

    for line in lines:
        try:
            #254231:4201,1:1,1439442880,STABLE BEAMS,6500,1357.453,1338.269,0.0,DT
            items=line.replace(':',',').split(",")
            #print items
            #print items[1],items[0],items[2],items[9]
            
            dict[(int(items[1]),int(items[0]),int(items[2]))]=[int(items[4]),float(items[8])]
        except:
            print "can't parse",line
            print items
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
        #run=int(items[0])
        fill=int(items[0])
        NBX=int(items[1])
        NBXPerFill[fill]=NBX
    except:
        print "Problem with line",line

nbxfile.close()

nBX=1

time0=0

file1=open(filename1)
file2=open(filename2)

dict1=dictFromCSVFile(file1)
dict2=dictFromCSVFile(file2)

total1=0
total2=0

overtlapKeys=list(set(dict1).intersection(dict2))
overtlapKeys.sort()

print len(dict1),len(dict2),len(overtlapKeys)

label=filename2.split("_")[0]+"/"+filename1.split("_")[0]

can=ROOT.TCanvas("can","",700,700)
ratio=ROOT.TH1F("ratio",";ratio "+label+";",200,0,2)
ratioNarrow=ROOT.TH1F("ratioNarrow",";ratio "+label+";",200,0.96,1.04)
ratioVsTime=ROOT.TGraph()
ratioVsInst=ROOT.TGraph()
ratioVsInstProfile=ROOT.TProfile("ratioVsInstProfile",";Average Inst. Luminosity (Hz/#muB);Average "+label,50,0,0.3,0.5,1.5)
ratioVsTime.SetTitle(";Time (s);"+label)
ratioVsInst.SetTitle(";Average Inst. Luminosity (Hz/#muB);"+label)

baddies={}
iCount=1
iBin=0
num=0
den=0
combineNLS=15
for key in overtlapKeys:
    try:
        if iCount==1:
            time0=dict1[key][0]
        #if dict2[key][1]<1000 or dict1[key][1]<1000:
        #    continue
        if abs(dict1[key][1]/dict2[key][1]-1)>.2:
            #print key,dict1[key],dict2[key],1-dict2[key]/dict1[key]
            newKey=(key[0],key[1])
            print key
            if newKey not in baddies:
                baddies[newKey]=1
            else:
                baddies[newKey]=baddies[newKey]+1
            continue
        num=num+dict2[key][1]
        den=den+dict1[key][1]
        total2=total2+dict2[key][1]
        total1=total1+dict1[key][1]
        if iCount%combineNLS==0:
            ratio.Fill(num/den)
            ratioNarrow.Fill(num/den)
            ratioVsTime.SetPoint(iBin,dict1[key][0]-time0,num/den)
            ratioVsInst.SetPoint(iBin,den/NBXPerFill[key[0]]/combineNLS,num/den)
            ratioVsInstProfile.Fill(den/NBXPerFill[key[0]]/combineNLS,num/den)
            num=0
            den=0
            iBin=iBin+1
            
        iCount=iCount+1

    except:
        print "fail",key
        pass

print "Totals",total1*23.31e-3,total2*23.31e-3, total2/total1

badkeys=baddies.keys()
badkeys.sort()
for key in badkeys:
    if  baddies[key]>10:
        print key, baddies[key]

print "my label",label

ratioVsInst.Draw("AP")
can.Update()
can.SaveAs(filelabel+"_vsInstLumi.png")
ratioVsInstProfile.SetLineColor(ROOT.kRed)
ratioVsInstProfile.Draw()
ratioVsInstProfile.GetYaxis().SetRangeUser(0.95,1.08)
ratioVsInstProfile.Fit("pol1")
can.Update()
can.SaveAs(filelabel+"_vsInstLumiPro.png")
ratio.Draw()
can.Update()
ratioNarrow.Draw()
#ratioNarrow.Fit("gaus")
can.Update()
can.SaveAs(filelabel+"_binnedRatio.png")
ratioVsTime.Draw("AP")
can.Update()
can.SaveAs(filelabel+"_vsTime.png")
