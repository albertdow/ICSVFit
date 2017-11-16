#include <iostream>
#include <string>
#include <stdlib.h>
#include <stdint.h>

#include "TFile.h"
#include "TTree.h"
#include "UserCode/ICHiggsTauTau/interface/Candidate.hh"
#include "UserCode/ICHiggsTauTau/interface/Met.hh"
#include "TauAnalysis/ClassicSVfit/interface/ClassicSVfit.h"
#include "TauAnalysis/ClassicSVfit/interface/MeasuredTauLepton.h"
#include "TauAnalysis/ClassicSVfit/interface/svFitHistogramAdapter.h"
#include "TSystem.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"

using namespace classic_svFit;

int main(int argc, char* argv[]){

  if (argc != 2 && argc != 3){
    std::cerr << "Need 1 or 2 args: <input> (<file_prefix>)" << std::endl;
    exit(1);
  }


  std::string file_prefix = "";
  if(argc==3) file_prefix = argv[2];
  std::string input_file = argv[1];
  std::string output_file = input_file;

  if (output_file.find("input.root") != input_file.npos) {
    std::size_t pos = output_file.find("input.root");
    output_file.replace(pos, std::string("input.root").length(), "output.root");
  } else {
    std::cerr << "The input file is not named correctly" << std::endl;
    return 1;
  }
  TFile *input = TFile::Open((file_prefix+input_file).c_str());
  if (!input) {
    std::cerr << "The input file could not be opened" << std::endl;
    return 1;
  }
  TTree *itree = dynamic_cast<TTree *>(input->Get("svfit"));
  if (!itree) {
    std::cerr << "The input tree could not be found" << std::endl;
    return 1;
  }

  ic::Candidate *c1 = NULL;
  ic::Candidate *c2 = NULL;
  ic::Met *met = NULL;
  unsigned event = 0;
  unsigned lumi = 0;
  unsigned run = 0;
  ULong64_t objects_hash = 0;
  unsigned mode = 0;
  int dm1 = -1;
  int dm2 = -1;
  double svfit_mass;
  double svfit_transverse_mass;
  ic::Candidate *svfit_vector = NULL;

  TH1::AddDirectory(kFALSE);

  itree->SetBranchAddress("event", &event);
  itree->SetBranchAddress("lumi", &lumi);
  itree->SetBranchAddress("run", &run);
  itree->SetBranchAddress("objects_hash", &objects_hash);
  itree->SetBranchAddress("lepton1", &c1);
  itree->SetBranchAddress("dm1", &dm1);
  itree->SetBranchAddress("lepton2", &c2);
  itree->SetBranchAddress("dm2", &dm2);
  itree->SetBranchAddress("met", &met);
  itree->SetBranchAddress("decay_mode", &mode);

  TFile *output = new TFile(output_file.c_str(),"RECREATE");
  TTree *otree = new TTree("svfit","svfit");
  otree->Branch("event", &event, "event/i");
  otree->Branch("lumi", &lumi, "lumi/i");
  otree->Branch("run", &run, "run/i");
  otree->Branch("objects_hash", &objects_hash, "objects_hash/l");
  otree->Branch("svfit_mass", &svfit_mass);
  otree->Branch("svfit_transverse_mass", &svfit_transverse_mass);
  otree->Branch("svfit_vector", &svfit_vector);
  
  for (unsigned i = 0; i < itree->GetEntries(); ++i) {
    itree->GetEntry(i);
    std::pair<ic::Candidate, std::vector<double>> result;
    
    // define MET
    double measuredMETx =  met->vector().px();
    double measuredMETy = met->vector().py();

    // define MET covariance
    TMatrixD covMET(2, 2);
    covMET(0,0) = met->xx_sig();
    covMET(1,0) = met->yx_sig();
    covMET(0,1) = met->xy_sig();
    covMET(1,1) = met->yy_sig();

    std::vector<MeasuredTauLepton> measuredTauLeptons;
    if (mode == 0) {
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToMuDecay, c1->pt(), c1->eta(), c1->phi(), 0.10566)); 
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToHadDecay,  c2->pt(), c2->eta(), c2->phi(), c2->M(), dm2));         
    } else if (mode == 1){
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToElecDecay, c1->pt(), c1->eta(), c1->phi(), 0.000511));
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToMuDecay, c2->pt(), c2->eta(), c2->phi(), 0.10566));
    } else if (mode == 2){
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToElecDecay, c1->pt(), c1->eta(), c1->phi(), 0.000511));
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToHadDecay,  c2->pt(), c2->eta(), c2->phi(), c2->M(), dm2));
    } else if (mode == 3){
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToHadDecay,  c1->pt(), c1->eta(), c1->phi(), c1->M(), dm1));
      measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToHadDecay,  c2->pt(), c2->eta(), c2->phi(), c2->M(), dm2));
    } else{
      std::cout<<"Mode "<<mode<<" not valid"<<std::endl;
      exit(1);
    }

    int verbosity = 0;
    ClassicSVfit svFitAlgo(verbosity);
    svFitAlgo.addLogM_fixed(true, 6.);
    svFitAlgo.integrate(measuredTauLeptons, measuredMETx, measuredMETy, covMET);
    bool isValidSolution = svFitAlgo.isValidSolution();

    if (isValidSolution){
      svfit_mass = static_cast<DiTauSystemHistogramAdapter*>(svFitAlgo.getHistogramAdapter())->getMass();
      svfit_transverse_mass = static_cast<DiTauSystemHistogramAdapter*>(svFitAlgo.getHistogramAdapter())->getTransverseMass();
     svfit_vector->set_vector((ROOT::Math::PtEtaPhiEVector)ROOT::Math::PtEtaPhiMVector(static_cast<DiTauSystemHistogramAdapter*>(svFitAlgo.getHistogramAdapter())->getPt(), static_cast<DiTauSystemHistogramAdapter*>(svFitAlgo.getHistogramAdapter())->getEta(), static_cast<DiTauSystemHistogramAdapter*>(svFitAlgo.getHistogramAdapter())->getPhi(), svfit_mass));
    } else {
      svfit_mass = -1;
      svfit_transverse_mass = -1;
    }
    svfit_vector->set_id(objects_hash);
    std::cout << "Mass: " << svfit_mass << "\tVector Mass: " << svfit_vector->M() << "\tVector pT: " << svfit_vector->pt() << std::endl;
    otree->Fill();
  }
  output->Write();
  delete otree;
  output->Close();
  delete output;

  input->Close();
  delete input;

  return 0;
}



