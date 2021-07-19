# -*- coding: utf-8 -*-
#authors: Florence Jornod - INSERM UMRS 1124
#         Thomas Jaylet - Université de Paris - France
#         Karine Audouze - Université de Paris - France

#contact: systox@paris-descartes.fr


#AOP-helpFinder is provided without any warranty. But if you have any probleme please feel free to contact us by mail.

#------- WHAT IS AOPHELPFINDER? -------------

#AOP-helpFinder is a tool developed to help AOP development (Jean-Charles Carvaillo: https://github.com/jecarvaill/aop-helpFinder)(Environ Health Perspect. 2019 Apr;127(4):47005).

#It is based on text mining and parsing process on scientific abstracts. AOP-helpFinder identify links between stressors and molecular initiating event, key events and adverse outcomes through abstracts from the PubMed database (https://pubmed.ncbi.nlm.nih.gov/). 

#AOP-helpFinder was implemented under the H2020 Human Biomonintoring in Europe (HBM4EU) project, Work Package 13.1.
#HBM4EU has received funding from the European Union’s H2020 research and innovation programme under grant agreement No 733032.

#------- LICENCE ---------------------------

#This software is governed by the CeCILL license under French law and abiding by the rules of distribution of free software.  You can  use,  modify and/ or redistribute the software under the terms of the CeCILL license as circulated by CEA, CNRS and INRIA at the following URL

#http://cecill.info/licences/Licence_CeCILL_V2.1-en.txt

#-------------------------------------------
import sys
import re
import time
import os
import lxml
import extract_xml_withpmid as exxml
import compute_scores as cscores
import compute_output as cout
import create_collection_event as ev
import datetime
import results_filter as rf 
import tm_module as tm
import time
start_time = time.time()


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--abst", type=str, help="abstracts file, pubmed xml")
parser.add_argument("--events", type=str, help="events file, pubmed xml")
parser.add_argument("--outputtype", type=str)
parser.add_argument("--cleaning", type=str)
parser.add_argument("--output", type=str, help="output filename")
parser.add_argument("--stats", type=str)
parser.add_argument("--context_choice", type=bool, help="use modulateur")
parser.add_argument("--intro", type=int)
args = parser.parse_args()



abstracts_file = args.abst
events_file = args.events
output_name = args.output
cleaning=args.cleaning
outputtype=args.outputtype
intro=args.intro/100.0
if(outputtype=="tsv_abstracts"):
    output_abstr=True
    output_abstr_txt=False
elif(outputtype=="txt_format"):
    output_abstr_txt=True
    output_abstr=False
else:
    output_abstr=False    
    output_abstr_txt=False
    
if(cleaning=="cleaning-yes"):
    lemma_supp=True
    modal_supp=True
    modulateur_supp=True
    context_choice=True
else:
    lemma_supp=False
    modal_supp=False
    modulateur_supp=False
    context_choice=False



if lemma_supp is True or modal_supp is True or modulateur_supp is True:
    res_filter=True
else:
    res_filter=False
    
stat=args.stats   
stats_file =open(stat,"a")
chem_name = abstracts_file.split(".")[0].split("/")[7].replace("-"," ")


dict_abstracts = exxml.get_abstracts_from_pubmedfile(abstracts_file,context_choice)

stats_file.write(chem_name + "\t" + str(len(dict_abstracts)))



list_events = ev.create_collection_event(events_file)

print(abstracts_file + "   " + str(len(dict_abstracts)))


for abstract in dict_abstracts:
    score = cscores.compute_scores(abstract,list_events,intro)
    if score:
        abstract['score']=score

if res_filter is True : 
	for event in list_events :
		lemma_name, __ = tm.clean_abstract(event["name"], True, True, "lemma",context_choice)
		event["lemma_name"] = lemma_name
	dict_abstracts = rf.results_filter(dict_abstracts, list_events, lemma_supp, modal_supp, modulateur_supp,context_choice)

filename= output_name

if(output_abstr):
    output_file=open(filename+".tsv","w")
    cout.results_abstracts_to_tsv(dict_abstracts, output_file, list_events)
elif(output_abstr_txt):
    output_file=open(filename+".txt", "w")
    output_file_tsv=open(filename+".tsv","w")
    cout.results_abstracts_txt(dict_abstracts, output_file, list_events)
    cout.results_to_tsv(dict_abstracts, output_file_tsv, list_events)
else:
    output_file=open(filename+".tsv","w")
    cout.results_to_tsv(dict_abstracts, output_file, list_events)

