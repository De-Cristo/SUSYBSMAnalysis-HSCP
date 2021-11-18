#!/usr/bin/env python

import urllib
import string
import os,sys,time
import SUSYBSMAnalysis.HSCP.LaunchOnCondor as LaunchOnCondor  
import glob
import commands
import json
import collections # kind of map

goodLumis = {}
def LoadJson(jsonPath):
   jsonFile = open(jsonPath,'r')
   runList=json.load(jsonFile,encoding='utf-8').items()
   runList.sort()
   for run in runList :
      goodLumis[int(run[0])] = []
      for lumi in run[1] : goodLumis[int(run[0])].append(lumi)

def IsGoodRun(R):
   if(R in goodLumis): return True
   return False

def IsGoodLumi(R, L):
   for lumi in goodLumis[R]:
      if(L>=lumi[0] and L<=lumi[1]): return True
   return False


def IsFileWithGoodLumi(f):  
   #check if the file contains at least one good lumi section using DAS_CLIENT --> commented out because VERY SLOW!
   print 'das_client --limit=0 --query "lumi file='+f+' |  grep lumi.run_number,lumi.number"'      
   containsGoodLumi = False
   for run in commands.getstatusoutput('das_client --limit=0 --query "run file='+f+'"')[1].replace('[','').replace(']','').split(','):
      if(not IsGoodRun(int(run))):continue
      for lumi in commands.getstatusoutput('das_client --limit=0 --query "lumi file='+f+'"')[1].replace('[','').replace(']','').split(','):
         if(IsGoodLumi(run, lumi)):return True

   #FASTER technique only based on run number and file name parsing
   #run = int(F.split('/')[8])*1000+int(F.split('/')[9])
   #if(IsGoodRun(run)):return True
   #return False

   
def getChunksFromList(MyList, n):
  return [MyList[x:x+n] for x in range(0, len(MyList), n)]

#JSON = 'Calib.json'
JSON = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt'
#JSON = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/DCSOnly/json_DCSONLY_Run2015B.txt'#/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/DCSOnly/json_DCSONLY.txt'   
LOCALTIER   = 'T2_CH_CERN'
#DATASETMASK = '/StreamExpress/Run2015B-SiStripCalMinBias-Express-v1/ALCARECO'
#DATASETMASK = '/MinimumBias/Run2015B-SiStripCalMinBias-PromptReco-v1/ALCARECO'
#DATASETMASK = '/StreamExpress/Run2015B-SiStripCalMinBias-Express-v1/ALCARECO'
#DATASETMASK = '/ZeroBias/Run2015B-PromptReco-v1/RECO'
####DATASETMASK = ['/ZeroBias/Run2016F-SiStripCalMinBias-18Apr2017-v1/ALCARECO', '/ZeroBias/Run2016G-SiStripCalMinBias-18Apr2017-v1/ALCARECO']
#DATASETMASK = ['/ZeroBias/Run2016F-SiStripCalMinBias-18Apr2017-v1/ALCARECO']
#DATASETMASK = ['/ZeroBias/Run2016C-SiStripCalMinBias-18Apr2017-v1/ALCARECO', '/ZeroBias/Run2016D-SiStripCalMinBias-18Apr2017-v1/ALCARECO','/ZeroBias/Run2016E-SiStripCalMinBias-18Apr2017-v1/ALCARECO']

#DATASETMASK = ['/SingleMuon/Run2017B-09Aug2019_UL2017-v1/AOD'] #2017B SingleMuon
#DATASETMASK = ['/SingleMuon/Run2017D-09Aug2019_UL2017-v1/AOD'] #2017D SingleMuon
#DATASETMASK = ['/SingleMuon/Run2017F-09Aug2019_UL2017-v1/AOD'] #2017F SingleMuon

DATASETMASK = ['/ZeroBias/Run2017B-09Aug2019_UL2017-v1/AOD'] #2017B ZeroBias


EndPath     = "/eos/user/d/dapparu/thesis/hscp/DeDxCalib"
ISLOCAL     = False
TransferDirectlyToStorage = False
LoadJson(JSON)

def initProxy():
   if(not os.path.isfile(os.path.expanduser('~/private/x509_proxy')) or ((time.time() - os.path.getmtime(os.path.expanduser('~/private/x509_proxy')))>600)):
      print "You are going to run on a sample over grid using either CRAB or the AAA protocol, it is therefore needed to initialize your grid certificate"
      os.system('mkdir -p ~/private; voms-proxy-init --voms cms -rfc -valid 192:00 --out ~/private/x509_proxy')#all must be done in the same command to avoid environement problems.  Note that the first sourcing is only needed in Louvain
      #os.system('mkdir -p ~/private; voms-proxy-init -voms cms -rfc -valid 192:00')


def filesFromDataset(dataset,nof=100):
   ISLOCAL=False
   command_out = commands.getstatusoutput('das_client --limit=0 --query "site dataset='+dataset+' | grep site.name,site.dataset_fraction"')
   for site in command_out[1].split('\n'):
      if(LOCALTIER in site and '100.00%' in site): 
         ISLOCAL=True
         break

   NumberOfFiles = 0
   maxNofFiles = nof
   Files = []
   command_out = commands.getstatusoutput('das_client --limit=0 --query "file dataset='+dataset+'"')
   for f in command_out[1].split():
#      if(not IsFileWithGoodLumi(f)):continue
      if(ISLOCAL): Files += [f]
      else       : Files += ['root://cms-xrd-global.cern.ch/' + f]
      NumberOfFiles += 1
      if NumberOfFiles > maxNofFiles: break
   return Files

def filesFromDataset2(dataset):
   Files = []
   #Runs = ['278239', '278240', '278273'] #region 2 -- also 278018 , now removed because already processed
   # Runs = ['278308'] #region 3
   # Runs = ['279931'] #region 4
   #Runs  = ['278018', '278308', '279931', '280385'] #PostG old
   #Runs  = ['275777','275920','276525','276585','276870'] #PreG
   #Runs = [277992,278509,278345]#'278803','278805','278808','278820','278822','278874','278875','278923','278962','278975']
   Runs = [305040]
   for run in Runs:
      output = os.popen('das_client --limit=0 --query \'file run=%s dataset=%s\'' % (run, dataset)).read().split('\n')
      for f in output:
         if len(f)<5: continue
         Files.append([run, 'root://cms-xrd-global.cern.ch//' + f])
   return Files

def sublistFilesFromList(listFiles,segm=5):
    lR = []
    subl = []
    counter=0
    for inList in listFiles:
        if counter<segm:
            subl += [inList]
        if counter>=segm:
            counter=0
            lR += [subl]
            subl = []
        counter += 1
    return lR


#get the list of sample to process from das and datasetmask query
print("Initialize your grid proxy in case you need to access remote samples\n")
initProxy()

#   command_out = commands.getstatusoutput('das_client --limit=0 --query "dataset='+DATASETMASK+'"')
datasetList = DATASETMASK

#get the list of samples to process from a local file
#datasetList= open('DatasetList','r')
JobName = "DEDXSKIMMER"
FarmDirectory = "FARM_EDM_2017B_ZeroBias"
LaunchOnCondor.SendCluster_Create(FarmDirectory, JobName)
#LaunchOnCondor.Jobs_Queue = '2nd' #2days 
LaunchOnCondor.Jobs_Queue = '8nm' 
LaunchOnCondor.subTool = 'condor'


if not TransferDirectlyToStorage:
   os.system("mkdir -p /eos/user/d/dapparu/thesis/hscp/DeDxCalib/out2017B_ZeroBias/");
else:
   #os.system('mkdir -p %s/{275777,275920,276525,276585,276870}' % EndPath)
   os.system('mkdir -p %s/{Run2017B_ZeroBias}' % EndPath)
for DATASET in datasetList :
   DATASET = DATASET.replace('\n','')
   FILELIST = filesFromDataset(DATASET,100)
   print DATASET + " --> " + str(FILELIST)

   FILELIST2 = sublistFilesFromList(FILELIST,5)

   counterOfFiles=-1

   print FILELIST2

   LaunchOnCondor.Jobs_InitCmds = []
   #if(not ISLOCAL):LaunchOnCondor.Jobs_InitCmds = ['export X509_USER_PROXY=~/x509_user_proxy/x509_proxy; voms-proxy-init --noregen;']
   if(not ISLOCAL):LaunchOnCondor.Jobs_InitCmds = ['export X509_USER_PROXY=~/private/x509_proxy']

   #for inFileList in getChunksFromList(FILELIST2,1):
   for inFileList in FILELIST2:
      os.system("cp dEdxSkimmer_Template_cfg.py dEdxSkimmer_cfg.py")
      f = open("dEdxSkimmer_cfg.py", "a")
      f.write("\n")
      f.write("process.Out.fileName = cms.untracked.string('dEdxSkim.root')\n")
      f.write("\n")
      #for inFile in inFileList:
          #f.write("process.source.fileNames.extend(['"+inFile[1]+"'])\n")
          #f.write("process.source.fileNames.extend(['"+inFile+"'])\n")
          #print ("process.source.fileNames.extend(['"+inFile+"'])\n")
      f.write("process.source.fileNames.extend("+str(inFileList)+")\n")
      print ("process.source.fileNames.extend("+str(inFileList)+")\n")
      counterOfFiles+=1
      f.write("\n")
      f.write("#import PhysicsTools.PythonAnalysis.LumiList as LumiList\n")
      f.write("#process.source.lumisToProcess = LumiList.LumiList(filename = '"+JSON+"').getVLuminosityBlockRange()")
      f.write("\n")

      if("/ALCARECO" in DATASET):
         f.write("\n")
         f.write("process.tracksForDeDx.src = cms.InputTag('ALCARECOSiStripCalMinBias') #for SiStripCalMinBias ALCARECO format\n")
         f.write("\n")
      f.close()   
      if not TransferDirectlyToStorage:
         #LaunchOnCondor.Jobs_FinalCmds = ["cp dEdxSkim.root " + "/eos/user/d/dapparu/thesis/hscp/DeDxCalib/out/dEdxSkim_%s_%i.root && rm dEdxSkim.root" % (inFile[0], LaunchOnCondor.Jobs_Count)]
         #LaunchOnCondor.Jobs_FinalCmds = ["cp dEdxSkim.root " + "/eos/user/d/dapparu/thesis/hscp/DeDxCalib/out2017F/dEdxSkim_%s_%i.root" % (inFile[0], LaunchOnCondor.Jobs_Count)]
         #LaunchOnCondor.Jobs_FinalCmds = ["cp dEdxSkim.root " + "/eos/user/d/dapparu/thesis/hscp/DeDxCalib/out2017F/dEdxSkim_%s_%i.root" % (inFile, LaunchOnCondor.Jobs_Count)]
         LaunchOnCondor.Jobs_FinalCmds = ["cp dEdxSkim.root " + "/eos/user/d/dapparu/thesis/hscp/DeDxCalib/out2017B_ZeroBias/dEdxSkim_%i_%i.root" % (counterOfFiles, LaunchOnCondor.Jobs_Count)]
      else:
         LaunchOnCondor.Jobs_FinalCmds = ["lcg-cp -v -n 10 -D srmv2 -b file://${PWD}/dEdxSkim.root srm://ingrid-se02.cism.ucl.ac.be:8444/srm/managerv2\?SFN=%s/%s/dEdxSkim_%s_%i.root && rm -f dEdxSkim.root" % (EndPath, inFile[0], inFile[0], LaunchOnCondor.Jobs_Count)] # if you do not use zsh, change '\?' to '?'
      LaunchOnCondor.SendCluster_Push  (["CMSSW", "dEdxSkimmer_cfg.py" ])
#      os.system("rm -f dEdxSkimmer_cfg.py")

LaunchOnCondor.SendCluster_Submit()

