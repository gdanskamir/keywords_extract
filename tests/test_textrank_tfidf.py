#!/usr/bin/env python
#-*- coding:UTF-8 -*-

import sys
import re
import json
sys.path.append('../')
from collections import defaultdict
from collections import OrderedDict
from get_text_rank import TextRank
from get_tfidf import TfIdf
import math

for line in sys.stdin:
    json_data = json.loads(line.strip());
    text_rank = TextRank('idf_dict.big', 5, 20)
    tfidf_extract = TfIdf('idf_dict', 'idf_dict.big')

    total_term_list = [];
    idx = 0;
    while idx < len(json_data["regulationClause"]):
        term_list = json_data["regulationClause"][idx]["seg"];
        term_list_new = [i.encode('UTF-8', 'ignore') for i in term_list];
        total_term_list.extend(term_list_new)
        text_rank.add_sentence(term_list_new)
        idx = idx + 1
    text_rank.rank()
    tfidf_extract.tfidf(total_term_list)
    keywords = text_rank.gen_key_words();
    keywords_tfidf = tfidf_extract.gen_key_words();

    common_join = OrderedDict();
    for k,v in keywords.items():
        if k in keywords_tfidf:
            common_join[k] = 0.1 * v + keywords_tfidf[k]
    

    #print "\t".join([json_data["normalRegulationName"], json_data["@id"]]).encode('UTF-8', 'ignore') \
    #        + "\t" + json.dumps(common_join, ensure_ascii=False)

    print "\t".join([json_data["normalRegulationName"], json_data["@id"]]).encode('UTF-8', 'ignore') \
            + "\t" + json.dumps(keywords, ensure_ascii=False) \
            + "\t" + json.dumps(keywords_tfidf, ensure_ascii=False)

