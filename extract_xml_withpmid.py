# This file is an adapted version of Titipat Achakulvisut, Daniel E. Acuna (2015) "Pubmed Parser" http://github.com/titipata/pubmed_parser.  http://doi.org/10.5281/zenodo.159504


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
import random
import requests
from itertools import chain
from collections import defaultdict
from lxml import etree
from lxml import html
from unidecode import unidecode
import glob
import pprint
import datetime
import tm_module as tm




def parse_pmid(medline):
    """Parse PMID from article

    Parameters
    ----------
    medline: Element
        The lxml node pointing to a medline document

    Returns
    -------
    pmid: str
        String version of the PubMed ID
    """
    if medline.find('PMID') is not None:
        pmid = medline.find('PMID').text
    else:
        pmid = ''
    return pmid

def parse_doi(medline):
    """Parse PMID from article

    Parameters
    ----------
    medline: Element
        The lxml node pointing to a medline document

    Returns
    -------
    pmid: str
        String version of the PubMed ID
    """
#    print(medline)
    if medline.find('Article/ELocationID') is not None:
        doi=medline.find('Article/ELocationID[@EIdType="doi"]').text
#        print(doi)
    elif medline.find('PubmedData/ArticleIdList/ArticleId[@IdType="doi"]') is not None:
        doi = medline.find('PubmedData/ArticleIdList/ArticleId[@IdType="doi"]').text
#        print(doi)
    else:
        doi = ''
    return doi

def parse_journal_info(medline):
    """Parse MEDLINE journal information

    Parameters
    ----------
    medline: Element
        The lxml node pointing to a medline document

    Returns
    -------
    dict_out: dict
        dictionary with keys including `medline_ta`, `nlm_unique_id`,
        `issn_linking` and `country`

    """
    journal_info = medline.find('MedlineJournalInfo')
    if journal_info is not None:
        if journal_info.find('MedlineTA') is not None:
            medline_ta = journal_info.find('MedlineTA').text or '' # equivalent to Journal name
        else:
            medline_ta = ''
        if journal_info.find('NlmUniqueID') is not None:
            nlm_unique_id = journal_info.find('NlmUniqueID').text or ''
        else:
            nlm_unique_id = ''
        if journal_info.find('ISSNLinking') is not None:
            issn_linking = journal_info.find('ISSNLinking').text
        else:
            issn_linking = ''
        if journal_info.find('Country') is not None:
            country = journal_info.find('Country').text or ''
        else:
            country = ''
    else:
        medline_ta = ''
        nlm_unique_id = ''
        issn_linking = ''
        country = ''
    dict_info = {'medline_ta': medline_ta.strip(),
                 'nlm_unique_id': nlm_unique_id,
                 'issn_linking': issn_linking,
                 'country': country}
    return dict_info



def date_extractor(journal, year_info_only):
    """Extract PubDate information from an Article in the Medline dataset.

    Parameters
    ----------
    journal: Element
        The 'Journal' field in the Medline dataset
    year_info_only: bool
        if True, this tool will only attempt to extract year information from PubDate.
        if False, an attempt will be made to harvest all available PubDate information.
        If only year and month information is available, this will yield a date of
        the form 'YYYY-MM'. If year, month and day information is available,
        a date of the form 'YYYY-MM-DD' will be returned.

    Returns
    -------
    PubDate: str
        PubDate extracted from an article.
        Note: If year_info_only is False and a month could not be
        extracted this falls back to year automatically.
    """
    day = None
    month = None
    issue = journal.xpath('JournalIssue')[0]
    issue_date = issue.find('PubDate')

    if issue_date.find('Year') is not None:
        year = issue_date.find('Year').text
        if not year_info_only:
            if issue_date.find('Month') is not None:
                month = month_or_day_formater(issue_date.find('Month').text)
                if issue_date.find('Day') is not None:
                    day = month_or_day_formater(issue_date.find('Day').text)
    elif issue_date.find('MedlineDate') is not None:
        year_text = issue_date.find('MedlineDate').text
        year = year_text.split(' ')[0]
    else:
        year = ""

    if year_info_only or month is None:
        return year
    else:
        return "-".join(str(x) for x in filter(None, [year, month, day]))


def parse_keywords(medline):
    """Parse keywords from article, separated by ;
    Parameters
    ----------
    medline: Element
        The lxml node pointing to a medline document
    Returns
    -------
    keywords: str
        String of concatenated keywords.
    """
    keyword_list = medline.find("KeywordList")
    keywords = list()
    if keyword_list is not None:
        for k in keyword_list.findall("Keyword"):
            if k.text is not None:
                keywords.append(k.text)
        keywords = "; ".join(keywords)
    else:
        keywords = ""
    return keywords

def parse_article_info(medline_doi, medline_art, year_info_only, nlm_category, time_start, context_choice):
    """Parse article nodes from Medline dataset

    Parameters
    ----------
    medline: Element
        The lxml node pointing to a medline document
    year_info_only: bool
        see: date_extractor()
    nlm_category: bool
        see: parse_medline_xml()

    Returns
    -------
    article: dict
        Dictionary containing information about the article, including
        `title`, `abstract`, `journal`, `author`, `affiliation`, `pubdate`,
        `pmid`, `other_id`, `mesh_terms`, and `keywords`. The field
        `delete` is always `False` because this function parses
        articles that by definition are not deleted.
    """
#    print(medline[0])
    doi = parse_doi(medline_doi)
    keywords = parse_keywords(medline_doi)
    article = medline_art.find('Article')

    if article.find('ArticleTitle') is not None:
        title = stringify_children(article.find('ArticleTitle')).strip() or ''
    else:
        title=''
    category = 'NlmCategory' if nlm_category else 'Label'
    if article.find('Abstract/AbstractText') is not None:
        # parsing structured abstract
        if len(article.findall('Abstract/AbstractText')) > 1:
            abstract_list = list()
            for abstract in article.findall('Abstract/AbstractText'):
                section = abstract.attrib.get(category, '')
                if section != 'UNASSIGNED':
                    abstract_list.append('\n')
                    abstract_list.append(abstract.attrib.get(category, ''))
                section_text = stringify_children(abstract).strip()
                abstract_list.append(section_text)
            abstract = '\n'.join(abstract_list).strip()
        else:
            abstract = stringify_children(article.find('Abstract/AbstractText')).strip() or ''
    elif article.find('Abstract') is not None:
        abstract = stringify_children(article.find('Abstract')).strip() or ''
    else:
       abstract=''

    if article.find('AuthorList') is not None:
        authors = article.find('AuthorList').getchildren()
        authors_info = list()
        affiliations_info = list()
        for author in authors:
            if author.find('Initials') is not None:
                firstname = author.find('Initials').text or ''
            else:
                firstname = ''
            if author.find('LastName') is not None:
                lastname = author.find('LastName').text or ''
            else:
                lastname = ''
            if author.find('AffiliationInfo/Affiliation') is not None:
                affiliation = author.find('AffiliationInfo/Affiliation').text or ''
            else:
                affiliation = ''
            authors_info.append((firstname + ' ' + lastname).strip())
            affiliations_info.append(affiliation)
        affiliations_info = '\n'.join([a for a in affiliations_info if a is not ''])
        authors_info = '; '.join(authors_info)
    else:
        affiliations_info = ''
        authors_info = ''

    journal = article.find('Journal')
    journal_name = ' '.join(journal.xpath('Title/text()'))
    pubdate = date_extractor(journal, year_info_only)

    pmid = parse_pmid(medline_art)
    og = 3
    #avant aussi or not doi


    dict_out = {'title': title,
                    'abstractfull': abstract,
                    'abstract': tm.clean_abstract(abstract, True, False, "stem", context_choice),
                    'abstractfull_sentence' : tm.clean_abstract(abstract, False, False, "stem", context_choice),
                   # 'journal': journal_name,
                   # 'author': authors_info,
                   # 'affiliation': affiliations_info,
                    'pubdate': pubdate,
                    'pmid': pmid,
                    'doi':pmid,
                    'cpds':"",
                    'keywords':keywords,
                    'scores':"",
                                        }
    return dict_out



def parse_medline_xml(path,time_start, context_choice, year_info_only=True, nlm_category=False):
    """Parse XML file from Medline XML format available at
    ftp://ftp.nlm.nih.gov/nlmdata/.medleasebaseline/gz/

    Parameters
    ----------
    path: str
        The path
    year_info_only: bool
        if True, this tool will only attempt to extract year information from PubDate.
        if False, an attempt will be made to harvest all available PubDate information.
        If only year and month information is available, this will yield a date of
        the form 'YYYY-MM'. If year, month and day information is available,
        a date of the form 'YYYY-MM-DD' will be returned.
        NOTE: the resolution of PubDate information in the Medline(R) database varies
        between articles.
        Defaults to True.
    nlm_category: bool, default False
        if True, this will parse structured abstract where each section if original Label
        if False, this will parse structured abstract where each section will be assigned to
        NLM category of each sections

    Returns
    -------
    article_list: list
        Dictionary containing information about articles in NLM format (see
        `parse_article_info`). Articles that have been deleted will be
        added with no information other than the field `delete` being `True`
    """
    tree = read_xml(path)
    medline_for_doi = tree.findall('//PubmedArticle')
    medline_citations = tree.findall('//MedlineCitationSet/MedlineCitation')
    if len(medline_citations) == 0:
        medline_citations = tree.findall('//MedlineCitation')
    medline = []
    medline.append(medline_for_doi)
    medline.append(medline_citations)
    article_list = []
    for i in range(len(medline[0])):
        article_info = parse_article_info(medline[0][i], medline[1][i], year_info_only, nlm_category,time_start, context_choice)
        if article_info:
            article_list.append(article_info)
    #article_list = list(map(lambda m: parse_article_info(m[0], year_info_only, nlm_category), medline))
    delete_citations = tree.findall('//DeleteCitation/PMID')
    dict_delete = \
        [
            {'title': None,
             'abstract': None,
             'journal': None,
             'author': None,
             'affiliation': None,
             'pubdate': None,
             'pmid': p.text,
             'other_id': None,
             'pmc': None,
             'mesh_terms': None,
             'keywords': None,
             'delete': True,
             'medline_ta': None,
             'nlm_unique_id': None,
             'issn_linking': None,
             'country': None
             } for p in delete_citations
            ]
    article_list.extend(dict_delete)
    return article_list



def read_xml(path):
    """
    Parse tree from given XML path
    """
    try:
        tree = etree.parse(path)
    except:
        try:
            tree = etree.fromstring(path)
        except Exception as e:
            print("Error: it was not able to read a path, a file-like object, or a string as an XML")
            raise
    if '.nxml' in path:
        remove_namespace(tree) # strip namespace for
    return tree


def stringify_children(node):
    """
    Filters and removes possible Nones in texts and tails
    ref: http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
    """
    parts = ([node.text] +
             list(chain(*([c.text, c.tail] for c in node.getchildren()))) +
             [node.tail])
    return ''.join(filter(None, parts))

def abstracts_to_db(abstracts_file, time_start, abstracts_db):
    """ insere le fichier xml 'abstracts_file' dans la bd 'abstracts_db'
    """
    dict_xml = parse_medline_xml(abstracts_file, time_start)
    abstracts_db.insert(dict_xml)

    return

def get_abstracts_from_pubmedfile(abstracts_file, context_choice):
    """ insere le fichier xml 'abstracts_file' dans la bd 'abstracts_db'
    """
    dict_xml = parse_medline_xml(abstracts_file, 0, context_choice)

    return dict_xml
