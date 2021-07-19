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
import tm_module as tm
import compute_scores as cscores
import spacy
nlp = spacy.load("en_core_web_sm")



def del_event_values(event_values, i):
    del event_values["multiscore"][i]
    del event_values["sentence"][i]
    del event_values["localisation"][i]
    del event_values["words_found"][i]
    del event_values["ismodulateur"][i]
    del event_values["modal"][i]
    return event_values

"""
Supprime l'event si un verbe modal est retrouvé dans la phrase (si modal_supp = True)
Supprime l'event si le verbe modulateur n'est pas retrouvé dans la phrase (si modulateur_supp = False)
Si les 2 sont True -> Supprime les 2 cas en meme temps
"""
def suppression(event_values, modal_supp, modulateur_supp):
    cpt = 0
    longueur = len(event_values["ismodulateur"])
    for j in range(longueur):
        i = j 
        i = i - cpt
        if modal_supp is True and modulateur_supp is True :
            if (event_values["ismodulateur"][i] is False) or (event_values["modal"][i] is True) : # Si pas
                event_values = del_event_values(event_values,i)
                cpt = cpt + 1

        elif modal_supp is True and modulateur_supp is False :
            if event_values["modal"][i] is True :
                event_values = del_event_values(event_values, i)
                cpt = cpt + 1

        elif modal_supp is False and modulateur_supp is True : 
            if event_values["ismodulateur"][i] is False :
                event_values = del_event_values(event_values, i)
                cpt = cpt + 1

    return event_values





"""
Supprime l'event si l'event n'est plus retrouvé suite à la lemmatisation
"""
def filter(abstract, event_values, event):
    if not event_values["multiscore"] :
        del abstract["score"][event]
        if not abstract["score"] :
            del abstract["score"]
    return abstract



def modulateur_detection(ev, lemma_supp):
            modulateur = None
            event = ev["lemma_name"]
            doc_c = nlp(event.capitalize())
            doc_l = nlp(event.lower())
            if doc_c[0].pos_ =="VERB" and doc_l[0].pos_ == "VERB" and (len(event.split()) > 3) :
                if lemma_supp is True :
                    event = event.split()[1:]
                    event = ' '.join(event)
                    modulateur = doc_l[0].text
                else : 
                    event = ev["stemname"]
                    modulateur = event.split()[0]
                    event = event.split()[1:]
                    event = ' '.join(event)
            if lemma_supp is True :
            	return event, modulateur
            if lemma_supp is False and modulateur is not None :
            	return event, modulateur
            if lemma_supp is False and modulateur is None :
            	return ev["stemname"], modulateur

"""
lemmatisation, detection des verbes modaux et du modulateur d'un event sur le dictionnaire de resultat
Permet d'ajouter un/plusieurs filtres supplémentaires sur les resultats
dict_abstracts -> dictionnaire d'abstracts avec les resultats
list_events -> liste des events d'intérets fournis en input
lemma_supp, modal_supp et modulateur_supp -> booleen (True,False) permettant de choisir si on filtre ou non les resultats
"""
def results_filter(dict_abstracts, list_events, lemma_supp, modal_supp, modulateur_supp, context_choice):

    for abstract in dict_abstracts:
        if 'score' in abstract:
            for event, event_values in abstract['score'].copy().items():
                for ev in list_events:
                    if ev['name'] == event :
                        sentence_full = event_values["sentence"]
                        sentence = []
                        modal_lemma = []
                        for element in sentence_full :

                            sentence_lemma, modal = tm.clean_abstract(element, True, False, "lemma",context_choice)
                            # Si on veut lemma --> on garde les phrases lemma
                            if lemma_supp is True : 
                                sentence.append(' '.join(sentence_lemma))
                            # Sinon on garde les phrases stem 
                            else :
                                sentence_stem = tm.clean_abstract(element, True, False, "stem",context_choice)
                                sentence.append(' '.join(sentence_stem))
                            modal_lemma.append(modal)

                        
                        ev["ev_without_modul"], modulateur = modulateur_detection(ev, lemma_supp)


                        modul_list = []
                        if modulateur is not None :
                            for phrase in sentence :
                                if phrase.find(modulateur) == - 1:
                                    modul_list.append(False)
                                else : 
                                    modul_list.append(True)
                        else :
                            for phrase in sentence :
                                modul_list.append(None)
                        event_values["ismodulateur"] = modul_list    


                        if lemma_supp is True :
                            ev_to_score = ev["lemma_name"]

                        else :
                            ev_to_score = ev["stemname"]

                        if modulateur_supp is True :
                            ev_to_score = ev["ev_without_modul"]


                        multiscore, localisation, sentence, words_found = cscores.find_event(sentence, sentence_full, ev_to_score)
                        event_values["words_to_find"] = len(ev_to_score.split())

                        event_values["multiscore"] = multiscore 
                        event_values["sentence"] = sentence
                        event_values["words_found"] = words_found
                        event_values["modal"] = modal_lemma



                        localisation_list = []
                        modal_list = []
                        modulateur_list = []
                        for element in localisation :
                            localisation_list.append(event_values["localisation"][element])
                            modal_list.append(event_values["modal"][element])
                            modulateur_list.append(event_values["ismodulateur"][element])

                        event_values["localisation"] = localisation_list
                        event_values["modal"] = modal_list
                        event_values["ismodulateur"] = modulateur_list

                        if (modal_supp is True) or (modulateur_supp is True) :
                            event_values = suppression(event_values, modal_supp, modulateur_supp)

                        abstract = filter(abstract, event_values, event)

    return dict_abstracts
