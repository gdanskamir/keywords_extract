#!/usr/bin/env python
#-*- coding:UTF-8 -*-

import sys
import re
import json
from collections import defaultdict
from collections import OrderedDict
from keywords_extract_base import KeywordExtract
from keywords_extract_base import _get_module_path
import math

class TextRank(KeywordExtract):
    ''' 
    实现textrank算法
    '''
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


