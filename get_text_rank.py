#!/usr/bin/env python
#-*- coding:UTF-8 -*-

import sys
import re
import json
from collections import defaultdict
from collections import OrderedDict
import math

class KeywordExtract(object):
    stop_words = {}
    min_term_len = 2
    def term_len(self, term):
        return len(term.decode('UTF-8', 'ignore'))
    def __init__(self, stop_words_dict=""):
        if stop_words_dict != "":
            for i in open(stop_words_dict):
                self.stop_words[i.strip().split('\t')[0]] = 0

class TextRank(KeywordExtract):
    window_size = 5
    iter_times = 20
    p = 0.85

    def __init__(self, stop_words_dict="", window_size=5, iter_times=20):
        KeywordExtract.__init__(self, stop_words_dict)
        self.window_size = window_size
        self.iter_times = iter_times

        self.graph = defaultdict(list);
        self.pr = {};

    def add_edge(self, start, end, weight=1.0):
        self.graph[start].append(end)
        self.graph[end].append(start)
    

    def split(self, term_list):
        term_list_ret = []
        small_phase = []
        for i in term_list:
            if i in ["：", ":", "，", ',', "。"]:
                if len(small_phase) > 0:
                    term_list_ret.append(small_phase);
                    small_phase = []
            else:
                if i.strip() != "":
                    small_phase.append(i)
        if len(small_phase) > 0:
           term_list_ret.append(small_phase);
        return term_list_ret


    def add_sentence(self, term_list_line):
        term_list_split = self.split(term_list_line);
        for term_list in term_list_split:
            i = 0;
            while i < len(term_list):
                if term_list[i] in self.stop_words or self.term_len(term_list[i]) < self.min_term_len:
                    i = i + 1
                    continue
                j = i + 1
                while j < len(term_list) and j < i + self.window_size:
                    if term_list[j] not in self.stop_words and self.term_len(term_list[j]) >= self.min_term_len:
                        self.add_edge(term_list[i], term_list[j])
                    j = j + 1
                i = i + 1

    def rank(self):
        for k,v in self.graph.items():
            self.pr[k] = 1.0
        i = 0
        while i < self.iter_times:
            i = i + 1
            for k, v in self.graph.items():
                pr_c = 0.0
                for item in v:
                    pr_c = 1.0 * self.pr[item] / len(self.graph[item]) + pr_c;
                self.pr[k] = pr_c*self.p + 1 - self.p
            #print >>sys.stderr, "iter: ", i, "total_words: ", len(self.pr), " pr total:", sum([v for k, v in self.pr.items()])


    def gen_key_words(self, thres=2.5, top_keywords=20):
        sorted_pr = sorted(self.pr.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        idx = 0;
        key_words_ret = OrderedDict()
        for item in sorted_pr:
            if item[1] <= thres or idx >= top_keywords:
                break;
            key_words_ret[item[0]] = item[1];
            idx = idx + 1
        return key_words_ret


class TfIdf(KeywordExtract):
    doc_total = 60496
    
    idf_dict = defaultdict(float)
    tfidf_dict = defaultdict(float)

    def __init__(self, idf_filename="", stopword_file=""):
        KeywordExtract.__init__(self, stopword_file)
        if idf_filename != "":
            for line in open(idf_filename):
                token_list = line.strip().split('\t')
                if len(token_list) == 2:
                    self.idf_dict[token_list[0]] = float(token_list[1])

    def tfidf(self, term_list):
        for i in term_list:
            if self.term_len(i) < self.min_term_len:
                continue;
            if i not in self.tfidf_dict:
                self.tfidf_dict[i] = 1
            else:
                self.tfidf_dict[i] = self.tfidf_dict[i] + 1
        total_tf = sum([v for k,v in self.tfidf_dict.items()])
        for k, v in self.tfidf_dict.items():
            self.tfidf_dict[k] = v * 1.0 / total_tf * math.log(self.doc_total / self.idf_dict.get(k, 1))

    def gen_key_words(self, thres=0.05, top_keywords=20):
        sorted_tfidf = sorted(self.tfidf_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        idx = 0;
        key_words_ret = OrderedDict()
        for item in sorted_tfidf:
            if item[1] <= thres or idx >= top_keywords:
                break;
            key_words_ret[item[0]] = item[1];
            idx = idx + 1
        return key_words_ret


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

