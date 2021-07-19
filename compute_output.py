# -*- coding: utf-8 -*-
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

# http://cecill.info/licences/Licence_CeCILL_V2.1-en.txt


import nltk.corpus
import nltk.stem
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize

def results_to_tsv(dict_abstracts, output_file, list_events):
    """ write the result into a tsv (tab-separated values)
    ARGUMENTS : dict_abstracts -> the dictonnary with our results
    output_file -> the file used to store the results
    list_events -> the events used
    """
    output_file.write("date \t title \t pmid \t event \n")
    for abstract in dict_abstracts:
        if 'score' in abstract:
            abst_title = abstract['title']
            abst_id = abstract['pmid']
            abst = " ".join(abstract['abstractfull'].split('\n'))
            abst_k = abstract['keywords']
            abst_date = abstract["pubdate"]
            for event, event_values in abstract['score'].items():
                for ev in list_events:
                    if ev['name'] == event:
                        info_abst = "{}\t{}\t{}\t{}\n".format(abst_date, abst_title, abst_id, event)
                        output_file.write(info_abst)
    return
    
def results_abstracts_to_tsv(dict_abstracts, output_file, list_events):
    """ write the result into a tsv (tab-separated values)
    ARGUMENTS : dict_abstracts -> the dictonnary with our results
    output_file -> the file used to store the results
    list_events -> the events used
    """
    output_file.write("date \t title \t pmid \t event \n")
    for abstract in dict_abstracts:
        if 'score' in abstract:
            abst_title = abstract['title']
            abst_id = abstract['pmid']
            abst = " ".join(abstract['abstractfull'].split('\n'))
            abst_k = abstract['keywords']
            abst_date = abstract["pubdate"]
            for event, event_values in abstract['score'].items():
                for ev in list_events:
                    if ev['name'] == event:
                        info_abst = "{}\t{}\t{}\t{}\t{}\n".format(abst_date, abst_title, abst_id, event, abst)
                        output_file.write(info_abst)
    return

def results_abstracts_txt(dict_abstracts, output_file, list_events):
    """ write the result into a tsv (tab-separated values)
    ARGUMENTS : dict_abstracts -> the dictonnary with our results
    output_file -> the file used to store the results
    list_events -> the events used
    """
    output_file.write("date \t title \t pmid \t event \n")
    for abstract in dict_abstracts:
        if 'score' in abstract:
            abst_title = abstract['title']
            abst_id = abstract['pmid']
            abst = " ".join(abstract['abstractfull'].split('\n'))
            abst_k = abstract['keywords']
            abst_date = abstract["pubdate"]
            list_e=""
            for event, event_values in abstract['score'].items():
                for ev in list_events:
                    if ev['name'] == event:
                        list_e=list_e + ev['name'] +", "
            info_abst = "{}\n{}\n{}\n{}\n{}\n\n --------------------------------------- \n\n".format(abst_title, abst_date, abst_id, list_e, abst)
            output_file.write(info_abst)
    return
