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
#-------------------------------------------

import datetime
import csv
import tm_module as tm
import pprint as pprint
import random


def create_collection_event(event_filename):
    """Method to take from a file (event_filename) a list of event from the aopwiki website.
    The file must be a csv with a first col the aopwiki_id, then the type of the event, then the 		name of the event.
    ARGUMENT: event_filename -> the name of the file with the information about the event
    RETURN: list_events -> a dictionnary with all the events.
    """
    list_events = []
    list_id = []
    with open(event_filename,mode="r") as infile:
        reader = csv.reader(infile)
        for rows in reader:
            dict_event = {}
            id_event = rows[0]
            name = rows[0]
            if id_event not in list_id:
                dict_event["name"] = name
                dict_event["stemname"] = tm.clean_abstract(name, True, True, "stem", False)
                dict_event["udate"] = datetime.datetime.now()
                dict_event["indi"] = random.randint(1,4)
                list_events.append(dict_event)
            else:
                for event in list_events:
                    if event["id"] == id_event:
                        event["type"].append(t_event)
                        break
                    list_id.append(id_event)
    return list_events
