# keywords_extract
实现tfidf和textrank来提取关键词

# 文件说明
* filekeywords_extract_base.py
    * gen_idf_dict.py
    * get_text_rank.py
    * get_tfidf.py
* data or dict
    * idf_dict: 默认idf文件
    * idf_dict.big: 停留词
    * sample_data.seg：测试数据文件



# tests
cat ../sample_data.seg | python ./test_textrank_tfidf.py
output_format:
* tab分割
* 第三列为textrank输出，第四列为tfidf输出
* 关键词以及权重

# todo
可以尝试其他关键词提取算法

