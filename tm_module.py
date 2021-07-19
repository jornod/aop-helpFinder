#!/usr/bin/python3
# -*- coding: utf-8 -*-

######################################
# DESCRIPTION
######################################

# Text Mining Module
# Coded by Jean-Charles Carvaillo

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
"""
Text mining module
"""

######################################
# IMPORT
######################################

# set the path of nltk_data
import nltk.data
nltk.data.path.append('./data/nltk_data/')

import nltk.corpus
import nltk.stem
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize
import re
import string


import spacy
"""
Spacy :
    - Reference : https://github.com/explosion/spaCy
    - Installation : https://spacy.io/usage
"""

######################################
# FUNCTION
######################################




def clean_abstract(abstract, clean_all, case, process, context_choice):
    """Method to clean and simplify an abstract by text mining process.
        1. Split abstract by sentences
        2. Split sentences by words
        3. Remove sentences which contain a negation or context word 
        4. Remove stopwords from words in a sentence
        5. Stem process

    clean_all -> True or False :
    	True = All the cleaning steps are carried out = 1+2+3+4+5
    	False = Only the steps of splitting and removing negative sentences are performed -> Allows to retrieve the entire sentence (whole words + stopwords) = 1+2+3
    
    process : "lemma" or "stem"
        "lemma" = lemmatization -> look at surrounding text to determine a given word's part
        "stem" = stemming -> keep only root

    
    Return:
        abstract (str): cleaned and simplified abstract

    """
    # set list of tools
    negations = ['never', 'neither', 'no', 'none', 'nor', 'not', 'ain',
                 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven',
                 'isn', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn',
                 'weren', 'won', 'wouldn']

    context_word = [ "investigated", "investigate", "examined", "examine", "studied",
                "tested", "assayed", "measured", "evaluated", "objective", "objectives",
                "method", "methods", "background", "aimed", "context", "assesses", "explored",
                "aim","assays", "evaluate", "explore", "goal", "analyzed", "monitored",
                "abbreviations", "performed", "examining", "conducted", "compiles",
                "purpose", "recruiter", "assessed", "assess", "explores"]
	#To remove regardless of the writing style (upper, lower, capitalize)    
    contexts = []
    for word in context_word :
    	contexts.append(word.capitalize())
    	contexts.append(word.upper())
    	contexts.append(word.lower())

                 
    punctuation = list(string.punctuation)
    stop = nltk.corpus.stopwords.words('english') + punctuation + ['\'s']

    # 1. split abstract by sentences
    sents = sent_tokenize(abstract)

    sents = [sent for sent in sents if not (bool(re.search('\d', sent) and
             'body weight' in sent))]

    # 2. split sentences by words
    abstract = [word_tokenize(sent) for sent in sents]

    # 3. remove sentences which contain a negation or context word
    abstract = [sent for sent in abstract if not
                any(negation in sent for negation in negations)]
    if(context_choice is True):
        abstract =  abstract = [sent for sent in abstract if not
                    any(context in sent for context in contexts)]

    # 4. remove stopwords in sentences
    if clean_all is True :
        for i in range(len(abstract)):
            abstract[i] = [word for word in abstract[i] if word not in stop]

    # 5. stem process

    for i in range(len(abstract)):
        if clean_all is True :
            #print(abstract[i])
            if process == "stem" :
                abstract[i] = stem_process(abstract[i])
            elif process == "lemma" :
                abstract[i], modal = lemma_process(abstract[i])
        abstract[i] = ' '.join(abstract[i])
        # List of list --> List

    # 6. AOD or KEr search case
    if case is True:
        abstract = ' '.join(abstract)
        if process == "stem" :
            return abstract
        elif process == "lemma" :
            return abstract, modal
    else:
        if process == "stem" :
            return abstract
        elif process == "lemma" : 
            return abstract, modal


def stem_process(words):
    """Method to stem each words in a list.

    Return:
        words (list): a list which contains stemmed words.

    """
    # snowball stemmers developed by Martin Poter
    sno = nltk.stem.SnowballStemmer('english')
    # search if a particular word is in words
    for i in range(len(words)):
        words[i] = sno.stem(words[i])
    return words


def lemma_process(words):
    #print(words)
    nlp = spacy.load("en_core_web_sm")
    words = ' '.join(words)
    #print(words)
    doc = nlp(words.lower())
    lemma_list = []
    modal = False
    for token in doc:
        lemma_list.append(token.lemma_)
        if token.tag_ == "MD" : 
            modal = True
    #print(lemma_list)
    return lemma_list, modal




######################################
# Main()
######################################

if __name__ == '__main__':
    abstract = "Mitophagy ( an autophagic process that specifically involves damaged mitochondria ) may be involved , as judged from the decreased amount of mitochondrial DNA ."
    abstract1 = clean_abstract(abstract, True ,False, "lemma")
    print(abstract1)
    abstract2 = clean_abstract(abstract, True, False, "stem")
    print(abstract2)
