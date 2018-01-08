##Basic Git Instructions

0. Create your own fork of CMS-LUMI-POG/DataCert (upper right)  
1. Check out the group's version of the tools (easiest way to keep in sync)  
  a) git clone https://github.com/CMS-LUMI-POG/DataCert  
2. Make a remote to your fork  
  a) git remote add YOURGITUSERNAME http://github.com/YOURGITUSERNAME/DataCert  
3. Check in your edited files  
  a) git add file1 file2  
  b) git commit -m "file1 and file2 are changed because..."  
4. push to YOUR fork in a BRANCH  
  a) git checkout -b update-whatiam-date  
  b) git push YOURGITUSERNAME update-whatiam-date  
5. Make a pull request (PR) with your changes update-newcurrents-data  
  a) at https://github.com/CMS-LUMI-POG/DataCert  
  b) let someone review and merge into CMS-LUMI-POG's "master"  
6. Keep your master in sync with CMS-LUMI-POG/DataCert's master  
  a) git checkout master  
  b) git push YOURGITUSERNAME master  
  
  
  
# Luminosity comparisons

Get csv files from brilcalc using normtag_LUMINOMETER.json to filter bad data.  
Examples below:

for nt in normtag_hfet.json normtag_dt.json normtag_pcc.json normtag_hfoc.json normtag_bcm1f.json;
  do
    brilcalc lumi --normtag=${nt} -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON_MuonPhys.txt -u 'hz/ub' -o ${nt}.csv --output-style=csv --byls --tssec
  done
  
python compareTwoCSVsFromBRILCALC.py normtag_dt.json.csv normtag_hfet.json.csv NBX_perFill_2017.csv DTHFET


# Certification Instructions (Mostly depricated)

DataCert is weekly certification of luminosity for CMS data  

Below are examples of how to use the data certification scripts.  The goal is to 
efficiently go from PCCNtuples to an intermediate flat tree (certtree) and finally 
to series of luminosity plots per CMS run number.


All files take arguments using parser (-o option or --myoption=option syntax).  For 
all of them you can do:  
python my.py -h 
for help understanding options.


###makeDummyJSON.py
Produces a json file with runs given as input and an excessive luminosity section 
range that will cover all the LSs in a single run.  Very simple script.  Usage:

python makeDummyJSON.py run1 run2 ... runN  
Output:  jsondummy_run1_runN.txt


###retrieveBRILData.py
This is a wrapper script for brilcalc.  It produces a pickle file with the brildata 
which will be read by makeDataCertTree.py.  The usage is below.  Make sure to use 
"-o" to overwrite (the checking algorithm isn't working right for json files).

source brilcalc_env.sh  
python retrieveBRILData.py -j jsondummy_run1_runN.txt -o


###makeDataCertTree.py
This script makes takes input from pcc ntuples and the pickled brildata files 
originating from brilcalc.  The basic use of this script takes the pcc file and the 
directory where the brilcalc pickle files are located.  There are several features 
which should be useful:  setting the minimum LHC fill number for instance.

E.g.  
python makeDataCertTree.py --pccfile=/store/user/capalmer/ZeroBias1/PCC_Zerobias1_RunCert_0Bfield_LStest2/150626_191443/0000/pcc_Data_LS_12.root --brildir=brildata

E.g.  (BRIL only output)  
python makeDataCertTree.py --brildir=brildata -l BRILONLY
Output:  dataCertification_254227_254332_BRILONLY.root



###mkAndSubmitJobs.py
Most of the time you will use this script as a wrapper for makeDataCertTree.py.

E.g.  
python mkAndSubmitJobs.py -p /store/user/capalmer/ZeroBias1/PCC_Zerobias1_RunCert_0Bfield_LStest2/150626_191443/0000 -d MyJobsGoInThisDir -s

-s will submit your jobs to the queue as well.  The default is to NOT submit the 
jobs but just create the job_\#\.sh files in MyJobsGoInThisDir.  When submitting 
the jobs batch-wise only run,LS entries with CMS and BRIL data are saved (-b option).



###hadd step
After successfully getting all the output back from your jobs. You need to (by 
hand) hadd the root files:  
E.g.  
hadd dataCertification_246908_248038_merged.root MyJobsGoInThisDir/dataCertification_246908_248038_\*.root



###createJSONOfRunLS.py
Only entries with both CMS and BRIL data are saved here.  You need to add run,LS 
entries where there are no pixel clusters and only BRIL luminometers have provided 
data.  Using this script is the first step in that process.  It reads all the 
run,LS entries in a root file and writes a JSON file in the typical CMS format:  
E.g.  
python createJSONOfRunLS.py -f FullTest/dataCertification_246908_248038_merged.root -l LABEL  
Output:  jsonOfReadRunLSsLABEL.txt  



###filterOutJSON.py
This takes a JSON file and a certtree.  If the run,LS pair of an entry in the tree 
is NOT in the JSON file, then the entry will be saved exactly in a new tree.  
E.g.  
python filterOutJSON.py -r dataCertification_246908_248038_BRILONLY.root -j jsonOfReadRunLSsLABEL.txt  
Output:  dataCertification_246908_248038_BRILONLY_filtered.root  



###hadd CMS+BRIL tree with filtered BRILONLY tree
hadd -f dataCertification_246908_248038_complete.root dataCertification_246908_248038_merged.root dataCertification_246908_248038_BRILONLY_filtered.root



###dataCertPlots.py
To look in the tree and auto generate a list of runs use -a:  
E.g.  
python dataCertPlots.py -b -c dataCertification_246908_248038_all.root -a

Otherwise give a comma separated (NO SPACES) list with -r:  
E.g.  
python dataCertPlots.py -b -c dataCertification_246908_248038_all.root -r 246908,248038  



