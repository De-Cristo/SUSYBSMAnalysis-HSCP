# Heavy Stable Charged Particle

## Table of Contents

1.  [Setup working area](#setup-working-area)
1.  [Run the code](#run-the-code)
    * [Step 0](#step-0)
    * [Step 1](#step-1)
    * [Step 2](#step-2)
1.  [Compute Lumi](#compute-lumi)
<!--1.  [Pileup reweighting](#pileup-reweighting)-->

## Setup working area

```bash
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_6_30
cd CMSSW_10_6_30/src/
cmsenv
```

For the following step you should have a ssh key associated to your GitHub account.
For more information, see [connecting-to-github-with-ssh-key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).

```bash
git clone -b master git@github.com:De-Cristo/SUSYBSMAnalysis-HSCP.git SUSYBSMAnalysis 
```

To compile the code, run
```bash
cd SUSYBSMAnalysis
scram b -j
```

## Run the code

|Steps:  |                                                             |
|:---    |:------                                                      |
|Step 0  |  Produce EDM-tuples from AOD                                 |
|Step 1  |  Produce bare ROOT-tuples (histograms and trees) from step 0                   |
|Step 2  |  Estimate Background using histograms from Step 1  |
|Step 3  |  Make plots                                                 | 
|Step 4  |  Compute Limits                                             | 

### Step 0

**Get the main script first**
```bash
cp HSCP/test/HSCParticleProducer_cfg.py .
```
Have a look at `HSCParticleProducer_cfg.py` to see all available options.

**Get proxy**
```bash
voms-proxy-init --voms cms -valid 192:00
```

**Run locally (updated)**

Before running locally:
```bash
#file exists? Note that site of type "TAPE" has no user access
dasgoclient -query="site file=/store/data/Run2017B/SingleMuon/AOD/15Feb2022_UL2017-v1/2820000/0014B98B-5C06-A140-82C4-38E4C1BE6366.root"
```

How to run
```bash
cmsRun HSCParticleProducer_cfg.py \
        LUMITOPROCESS=HSCP/test/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt \
        inputFiles=root://cms-xrd-global.cern.ch//store/data/Run2017B/SingleMuon/AOD/15Feb2022_UL2017-v1/2820000/0014B98B-5C06-A140-82C4-38E4C1BE6366.root \
        maxEvents=20000
```
You can also use `inputFiles_load=input.txt`, where `input.txt` contains a list of files.

Don't forget to copy needed files:
```bash
cp HSCP/data/CorrFact*Pix*.txt .
cp HSCP/data/template*.root .
cp HSCP/data/MuonTimeOffset.txt .
```


### Step 1

|Analysis Type:  | |
|:---    |:------  |
|Type 0  |  Tk only |
|Type 1  |  Tk+Muon |
|Type 2  |  Tk+TOF  |
|Type 3  |  TOF only | 
|Type 4  |  Q>1 | 
|Type 5  |  Q<1 | 

#### EDAnalyzer on top of EDM files (created during the previous step) (updated)

Main script(don't use now): `cp Analyzer/test/HSCParticleAnalyzer_cfg.py .`

**Causious! The following files are 'ProducerAnalyzer', combine of Step0 and Step1?**

**For Data:** `cp Analyzer/test/Licheng/HSCParticleProducerAnalyzer_master_cfg.py .`

**For Signal:** `cp Analyzer/test/Licheng/HSCParticleProducerAnalyzer_2018_SignalMC_cfg.py .`

**For Background MC:** `cp Analyzer/test/Licheng/HSCParticleProducerAnalyzer_2018_mc_cfg.py .`

```bash
cmsRun HSCParticleProducerAnalyzer_master_cfg.py LUMITOPROCESS=HSCP/test/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt maxEvents=20000
```

This step will provide a root file contains histograms with the name `Histos_numEvent20000.root`

Original Step1 only:

```bash
cmsRun HSCParticleAnalyzer_cfg.py inputFiles=file:HSCP.root maxEvents=100
```

Where the `HSCParticleAnalyzer_cfg.py` need to be changed to the name of the scripts that be copied and `HSCP.root` is the same file that produced in step0.

Or, if there are many files: 
```bash
ls HSCP*.root|sed 's/^/file:/'>list.txt
cmsRun HSCParticleAnalyzer_cfg.py inputFiles_load=list.txt
```

**For Fast Check with simple cpp executive:** 

```
cd FastChecker
source compile_n_run.sh
```