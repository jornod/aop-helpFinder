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
import networkx as nx
import tm_module as tm
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize


def compute_scores(abstract, events, ratio_intro):
    ''' METHOD: compute the score of presence of the event in the abstract, return also the different position in the abstract.
	ARGUMENTS: abstract -> a string with the abstract
		   events -> the list of the events
	RETURN: dico -> a dictionnary with the name if the event as key and the 2 scores
    '''
    len_abstract = len(abstract['abstract'])
    sentences = abstract['abstract']
    sentences_full = abstract['abstractfull_sentence']
    dico={}

    for event in events:
        score = []
        words_found = []
        if event["stemname"]!='':
            score, localisation, sentence, words_found = find_event(sentences, sentences_full, event["stemname"])
        if(score):
            # If there is a score, we then check the position in the abstract 
            localisation, ratio_localisation = real_localisation(abstract, sentence)
            score, localisation, sentence, words_found, ratio_localisation = check_position(score, localisation, sentence, words_found, ratio_localisation, ratio_intro)
            if(score):        
                dico[str(event["name"])]={}
                dico[str(event["name"])]["multiscore"]=score
                dico[str(event["name"])]["localisation"]=localisation
                dico[str(event["name"])]["sentence"]=sentence
                dico[str(event["name"])]["words_to_find"]=len(event["stemname"].split())
                dico[str(event["name"])]["words_found"]= words_found
    return(dico)

def find_event(sentences, sentences_full, event):
    #print(sentences, sentences_full, event, '\n\n\n') #Thomas
    ''' METHOD: find a event in a list of sentences and compute the score
    ARGUMENTS: sentences -> a string with the sentences (for example an abstract)
    event -> a string with one event
    RETURN: score, localisation -> the score associated to the event and the abstract, and the localisation of the event (index of the list of sentences) , sentence and number of words found in the sentence
    '''
    event_split = list(set(event.split()))
    if not event_split:
        return
    score = []
    words_found = []
    localisation = []
    phrase = []
    ind = 0
    for i in range(len(sentences)):
        best, cpt = presence_score(sentences,event_split,i)
        if (abs(1-best/len(event_split)) <= 1 and best!=0):
            score.append(best/len(event_split))
            localisation.append(i)
            words_found.append(cpt)
            phrase.append(sentences_full[i])
        ind += 1
    return score, localisation, phrase, words_found



def presence_score(sentence, event,i):
	''' METHOD: check if a event is in a sentence in a text (sentences)
	    ARGUMENTS: sentences -> a string with the sentences (for example an abstract)
		       event -> a list of the words from one event
		       i -> the index of the sentence
	    RETURN: best -> the best score found ; cpt -> number of words found
    '''
	best = 0
	cpt = 0
	index = {}
	words = sentence[i].split()
	for e in event:
		if e in words:
			cpt += 1
			index[e] = [pos+1 for pos, value in enumerate(words) if value == e]
	proportion = cpt/len(event)
	if 0.75 <= proportion and len(event) != 1:
		values = index.values()
		values = [sorted(value) for value in values]
		values = sorted(values, key = lambda k: k[-1])
		G = nx.Graph()
		for i in range(len(values) -1):
			for j in range(len(values[i])):
				for l in range(len(values[i + 1])):
					G.add_edge(values[i][j], values[i+1][l], weight = abs(values[i+1][l]-values[i][j]))
		shortest_paths = {}
		for start in values[0]:
			for end in values[-1]:
				shortest_path = nx.dijkstra_path(G, start, end)
				tot_weight = nx.dijkstra_path_length(G, start, end)
				shortest_paths[tot_weight +1] = shortest_path
		best = min(shortest_paths, key = shortest_paths.get)
	elif proportion == 1.0 and len(event) ==1 :
		best = 1.0
	return best, cpt


def real_localisation(abstract, sentences_found):
    # Find the real localization of the sentence found in the complete abstract (without preprocessing)
    # Returns the position of the sentence in the abstract as an index and a ratio between 0 and 1
    sentences_without_tm = sent_tokenize(abstract["abstractfull"])
    len_abstract = len(sentences_without_tm)
    ratio_localisation = []
    index_localisation = []
    for sentence_found in sentences_found :
        real_localisation = - 1
        for i in range(len_abstract):
            if ' '.join(word_tokenize(sentences_without_tm[i]))== sentence_found :
                real_localistation = i
        ratio = real_localistation/len_abstract
        index_localisation.append(real_localistation)
        ratio_localisation.append(ratio)
    return index_localisation, ratio_localisation

def check_position(score, localisation, sentence, words_found, r_localisation, limit):
    # Remove the score if the found sentence is below the limit 
    cpt = 0
    for j in range(len(r_localisation)):
        i = j - cpt 
        if r_localisation[i] <= limit :
            del score[i]
            del localisation[i]
            del sentence[i]
            del r_localisation[i]
            del words_found[i]
            cpt += 1
    return score, localisation, sentence, words_found, r_localisation


def update_score_in_db(abstracts_db, abstract_id, scores):
    abstracts_db.update({"_id":abstract_id},{"$set": {"scores":scores}})
    return
