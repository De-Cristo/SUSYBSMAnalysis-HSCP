import sys, os, time, re
import numpy as np
#from common_functions import *
from optparse import OptionParser
parser = OptionParser(usage="Usage: python %prog codeVersion")
(opt,args) = parser.parse_args()

datasetList = [
"/ZToMuMu_M-50To120_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
"/ZToMuMu_M-120To200_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
"/ZToMuMu_M-200To400_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
"/ZToMuMu_M-400To800_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
"/ZToMuMu_M-800To1400_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
"/ZToMuMu_M-1400To2300_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v1/AODSIM",
"/ZToMuMu_M-2300To3500_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
"/ZToMuMu_M-3500To4500_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v1/AODSIM",
"/ZToMuMu_M-4500To6000_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
"/ZToMuMu_M-6000ToInf_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18RECO-106X_upgrade2018_realistic_v11_L1v1-v2/AODSIM",
]

codeVersion = sys.argv[1]
#just the number, like 18p2

if not os.path.exists("submittedConfigs"): os.makedirs("submittedConfigs")

if not os.path.exists("4crab_Template.py"):
  TEMPLATE = '''
from CRABClient.UserUtilities import config
config = config()

config.section_('General')
config.General.requestName = 'Analysis_2018_ROVIDMINTA_CodeVVERZIO_v1'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True

config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'HSCParticleProducerAnalyzer_2018_mc_cfg.py'
config.JobType.allowUndistributedCMSSW = True
config.JobType.maxJobRuntimeMin = 3000
config.JobType.maxMemoryMB = 4500
config.JobType.inputFiles = ['SUSYBSMAnalysis/HSCP/data/template_2018MC_v4.root','SUSYBSMAnalysis/HSCP/data/MuonTimeOffset.txt']

config.section_('Data')
config.Data.inputDataset = 'MINTA'
#config.Data.inputDBS = 'phys03'
#config.Data.splitting = 'Automatic'
config.Data.splitting = 'LumiBased'
    #config.Data.unitsPerJob = 1 #20
#config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 75
#config.Data.totalUnits = config.Data.unitsPerJob * 800
config.Data.outputDatasetTag = config.General.requestName
config.Data.outLFNDirBase = '/store/user/tvami/HSCP'
config.Data.ignoreLocality = True
config.Data.publication = False
config.Data.partialDataset = True

config.section_('Site')
config.Site.whitelist = ['T2_DE_DESY','T2_CH_CERN','T2_IT_Bari','T1_IT_*','T2_US_*', 'T3_US_FNALLPC','T2_HU_Budapest','T2_FR_*', 'T2_UK_London_IC']
config.Site.blacklist = ['T2_US_Nebraska']
config.Site.storageSite = 'T2_HU_Budapest'
  '''

  with open("4crab_Template.py", "w") as text_file:
      text_file.write(TEMPLATE)

for i in datasetList:
  print("Submit for sample "+i)
  os.system("cp 4crab_Template.py 4crab_toSubmit.py")
  replaceVERZIO = "sed -i 's/VERZIO/"+codeVersion+"/g' 4crab_toSubmit.py"
  os.system(replaceVERZIO)
  shortSampleName = i[1:(i.find('TuneCP5'))-1]
  replaceROVIDMINTA = "sed -i 's/ROVIDMINTA/"+shortSampleName+"/g' 4crab_toSubmit.py"
  os.system(replaceROVIDMINTA)
  replaceMINTA = "sed -i 's/MINTA/"+i.replace("/","\/")+"/g' 4crab_toSubmit.py"
  os.system(replaceMINTA)
  os.system("crab submit -c 4crab_toSubmit.py")
  os.system("mv 4crab_toSubmit.py submittedConfigs/.")

os.system("rm 4crab_Template.py")
