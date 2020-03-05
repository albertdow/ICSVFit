import os
from CRABClient.UserUtilities import config

config = config()

config.General.requestName = ''

config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = os.environ['CMSSW_BASE']+'/src/ICSVFit/ClassicSVfitTest/scripts/do_nothing_cfg.py'
config.JobType.scriptExe = ''
config.JobType.inputFiles = [os.environ['CMSSW_BASE']+'/src/ICSVFit/ClassicSVfitTest/scripts/FrameworkJobReport.xml', os.environ['CMSSW_BASE']+'/bin/'+os.environ['SCRAM_ARCH']+'/ClassicSVFitTest']
config.JobType.outputFiles = ['svfit_output.tar']

config.Data.outputPrimaryDataset = 'SVFit'
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 1
config.Data.totalUnits = 1
config.Data.publication = False
config.Data.outputDatasetTag = ''

config.Site.blacklist = ['T3_IT_Bologna']
config.Site.storageSite = 'T2_UK_London_IC'
