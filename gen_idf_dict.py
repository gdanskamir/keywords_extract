#!/usr/bin/env python
#-*- coding:UTF-8 -*-

import sys
import re
import json
from collections import defaultdict

idf_dict = {}
for line in sys.stdin:
    json_data = json.loads(line.strip());

    idx = 0;
    term_list_new = []
    while idx < len(json_data["regulationClause"]):
        term_list = json_data["regulationClause"][idx]["seg"];
        term_list_new.extend([i.encode('UTF-8', 'ignore') for i in term_list])
        idx = idx + 1
    for item in set(term_list_new):
        if item in idf_dict:
            idf_dict[item] = idf_dict[item] + 1
        else:
            idf_dict[item] = 1

for k,v in idf_dict.items():
    print k + "\t" + str(v)
