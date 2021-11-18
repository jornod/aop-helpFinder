# AOP-helpFinder 

## authors and contact: 

         Florence Jornod - INSERM UMRS 1124
         Thomas Jaylet - Université de Paris - France
         Karine Audouze - Université de Paris - France
        

         systox@paris-descartes.fr


 _AOP-helpFinder is provided without any warranty. But if you have any probleme please feel free to contact us by mail._


##  How to cite 
If you use AOP-helpFinder, please cite :

Jornod et al. **AOP-helpFinder webserver: a tool for comprehensive analysis of the literature to support adverse outcome pathways development.** Bioinformatics. 2021 oct 30; doi: https://doi.org/10.1093/bioinformatics/btab750.

## What is AOP-helpFinder ? 

AOP-helpFinder is a tool developed to help AOP development (Carvaillo JC Environ Health Perspect. 2019 Apr;127(4):47005).

It is based on text mining and parsing process on scientific abstracts. AOP-helpFinder identify links between stressors and molecular initiating event, key events and adverse outcomes through abstracts from the PubMed database (https://pubmed.ncbi.nlm.nih.gov/). 

AOP-helpFinder was implemented under the H2020 Human Biomonintoring in Europe (HBM4EU) project, Work Package 13.1.
HBM4EU has received funding from the European Union’s H2020 research and innovation programme under grant agreement No 733032.

## What is AOP-helpFinder web server ?

AOP-helpFinder web server is a web tool for identification and extraction of associations between stressors and biological events at various level of the biological organization (molecular initiating event (MIE), key event (KE), and adverse outcome (AO)). 
The web server is based on an updated version of the AOP-helpFinder tool (https://github.com/jornod/aop-helpFinder).

For more information please read https://doi.org/10.1093/bioinformatics/btab750.

## Licence

This software is governed by the CeCILL license under French law and abiding by the rules of distribution of free software.  You can  use,  modify and/ or redistribute the software under the terms of the CeCILL license as circulated by CEA, CNRS and INRIA at the following URL

http://cecill.info/licences/Licence_CeCILL_V2.1-en.txt

## Structure of the folder

results/ 
		-> stats.txt 
			- a file with a resume for each stressor. For each stressor you have the number of abstracts found from the PubMed database, the number of abstracts with at least one link to an event, and the number of links between the stressor and events.

		-> output-XX.tsv (XX is the name of the selected stressor)
		    - result for the stressor XX. For each link you have the year, the title of the abstract, the DOI and the found event.

		-> resume-XX.tsv (XX is the name of the selected stressor)
		    - resume for the stressor XX with the number of PubMed abstracts, the number of events found, and the total number of links. Then for each found event, the number of associated abstracts. 
