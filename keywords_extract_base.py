#!/usr/bin/env python
#-*- coding:UTF-8 -*-

import sys
import re
import json
from collections import defaultdict
from collections import OrderedDict
import math
import os

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
    os.path.dirname(__file__), path))

class KeywordExtract(object):
    stop_words = {}
    min_term_len = 2
    def term_len(self, term):
        return len(term.decode('UTF-8', 'ignore'))

    def __init__(self, stop_words_dict=""):
        if stop_words_dict != "":
            for i in open(_get_module_path(stop_words_dict)):
                self.stop_words[i.strip().split('\t')[0]] = 0

