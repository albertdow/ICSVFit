#!/usr/bin/env python
import fnmatch
import os
import ROOT
import sys
from optparse import OptionParser
import shlex
from subprocess import Popen,PIPE

def run_command(command):
    print command
    p = Popen(shlex.split(command), stdout = PIPE, stderr = PIPE)
    out, err = p.communicate()
    print out, err
    return out, err

JOBWRAPPER             = './scripts/generate_job.sh'
JOBSUBMIT             = 'true'
if "JOBWRAPPER" in os.environ: JOBWRAPPER = os.environ["JOBWRAPPER"] 
if "JOBSUBMIT"  in os.environ: JOBSUBMIT  = os.environ["JOBSUBMIT"]
print "Using job-wrapper:    " + JOBWRAPPER
print "Using job-submission: " + JOBSUBMIT

parser = OptionParser()
parser.add_option("--jobwrap", dest="wrap",
                  help="Specify the job-wrapper script. The current wrapper is '%(JOBWRAPPER)s'."
                  " Using the --wrapper option overrides both the default and the environment variable. " % vars())
parser.add_option("--jobsub", dest="sub",
                  help="Specify the job-submission method. The current method is '%(JOBSUBMIT)s'"
                  " Using the --jobsub option overrides both the default and the environment variable. " % vars())
parser.add_option("-i","--input_folder", dest="input",
                  help="Scan the specified folder recursively looking for svfit input files.")
parser.add_option("--submit", dest="submit", action='store_true', default=False,
                  help="Generate and submit jobs")
parser.add_option("--verify", dest="verify", action='store_true', default=False,
                  help="Run verification of output, if --submit is also set then only jobs failing verification will be resubmitted.")
parser.add_option("--channels", dest="channels", default='em,et,mt,tt',
                  help="Comma seperated list of channels to process, other channels will be ignored.")
parser.add_option("--year", dest="year", default=2017,
                  help="Which year to run for")
parser.add_option("--algo", dest="algo", default='fastMTT',
                  help="Which algorithm to use: [ClassicSVFitTest, fastMTT]")


(options, args) = parser.parse_args()

channels = options.channels.split(',')

if options.wrap: JOBWRAPPER=options.wrap
if options.sub: JOBSUBMIT=options.sub

filesSeen = 0
filesVerified = 0

# files = ["TTToSemiLeptonic","DYJetsToLL-LO-ext1"]
# files = ["DY1JetsToLL-LO-ext"]
# runFiles = ["svfit_{}_{}_{}_input.root".format(x, options.channels, options.year) for x in files]
# runFiles = ['svfit_GluGluHToTauTau_M-125-ext_mt_2017_output.root', 'svfit_DYJetsToLL-LO_mt_2017_output.root', 'svfit_EmbeddingMuTauE_mt_2017_output.root', 'svfit_GluGluToPseudoscalarHToTauTauPlusTwoJets_M125_amcatnloFXFX_mt_2017_output.root', 'svfit_W3JetsToLNu-LO_mt_2017_output.root', 'svfit_WplusHToTauTau_M-125_mt_2017_output.root', 'svfit_EmbeddingMuTauD_mt_2017_output.root', 'svfit_SingleMuonF_mt_2017_output.root','svfit_EmbeddingMuTauC_mt_2017_output.root', 'svfit_SingleMuonC_mt_2017_output.root', 'svfit_TTToSemiLeptonic_mt_2017_output.root', 'svfit_WZTo1L1Nu2Q_mt_2017_output.root', 'svfit_WZTo3LNu_mt_2017_output.root', 'svfit_W4JetsToLNu-LO_mt_2017_output.root', 'svfit_GluGluToHToTauTauPlusTwoJets_M125_amcatnloFXFX_mt_2017_output.root', 'svfit_ZHToTauTau_M-125_mt_2017_output.root', 'svfit_T-tW_mt_2017_output.root', 'svfit_EmbeddingMuTauF_mt_2017_output.root','svfit_Tbar-tW_mt_2017_output.root', 'svfit_WminusHToTauTau_M-125_mt_2017_output.root', 'svfit_TTTo2L2Nu_mt_2017_output.root', 'svfit_WZTo2L2Q_mt_2017_output.root', 'svfit_DY1JetsToLL-LO_mt_2017_output.root', 'svfit_SingleMuonB_mt_2017_output.root', 'svfit_SingleMuonD_mt_2017_output.root', 'svfit_WWToLNuQQ-ext_mt_2017_output.root', 'svfit_ZZTo4L-ext_mt_2017_output.root', 'svfit_GluGluToMaxmixHToTauTauPlusTwoJets_M125_amcatnloFXFX_mt_2017_output.root','svfit_ZZTo2L2Q_mt_2017_output.root', 'svfit_EmbeddingMuTauB_mt_2017_output.root', 'svfit_SingleMuonE_mt_2017_output.root', 'svfit_WWToLNuQQ_mt_2017_output.root', 'svfit_DYJetsToLL-ext_mt_2017_output.root']

for root, dirnames, filenames in os.walk(options.input):
    for filename in fnmatch.filter(filenames, '*svfit_*_{}_input.root'.format(options.year)):
        # if filename not in runFiles: continue
        if not any('_'+chan+'_' in filename for chan in channels): continue
        fullfile = os.path.join(root, filename)
        outfile = fullfile.replace('input.root','output.root')
        print 'Found input file: '+fullfile
        filesSeen += 1
        submitTask = True
        if options.verify:
            if (os.path.isfile(outfile)):
                print 'Found output file: '+outfile
                fin =  ROOT.TFile(fullfile)
                tin = fin.Get("svfit")
                fout =  ROOT.TFile(outfile)
                tout = fout.Get("svfit")
                if fout and tout:
                    if tin.GetEntries() == tout.GetEntries():
                        print 'Both input and output trees have ' + str(tin.GetEntries()) + ' entries, passed verification'
                        submitTask = False
                        filesVerified += 1
                    else:
                        print 'Failed verification, input and output trees with different numbers of entries!'
                    fin.Close()
                    fout.Close()
                else:
                    print 'Failed verification, unable to open output file'
                    fin.Close()
            else:
              print 'Failed verification, output file not found!'

        if submitTask and options.submit:
            job = fullfile.replace('_input.root','.sh')
            os.system('{} "{} {}" {}'.format(JOBWRAPPER,options.algo,fullfile,job))
            os.system('{} {}'.format(options.sub, job))

print 'TOTAL SVFit FILES:    '+str(filesSeen)
print 'VERIFIED SVFit FILES: '+str(filesVerified)
