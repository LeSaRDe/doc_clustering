#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, fnmatch
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
import re
import json
import contractions
import time
import sqlite3
# from nltk.tag.stanford import StanfordNERTagger
# ST = StanfordNERTagger('/home/fcmeng/PycharmProjects/stanford/stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz',
# '/home/fcmeng/PycharmProjects/stanford/stanford-ner-2018-10-16/stanford-ner.jar')
from nltk.parse import CoreNLPParser
import multiprocessing

DEBUG = False
DOCS_ROOT = "/home/fcmeng/PycharmProjects/20news-18828/"

ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
conn = sqlite3.connect("20news-18828.db")


def rm_emails(txt):
    return re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', txt)


def rm_person_name(word_tokens):
    tags = list(ner_tagger.tag(word_tokens))
    new_words_tokens = []
    for tag in tags:
        if tag[1] != 'PERSON':
            new_words_tokens.append(tag[0])
    if DEBUG:
        print "\n\tcleaned sent: %s" % new_words_tokens
    return new_words_tokens


def insert_to_db(values):
    cur = conn.cursor()
    cur = cur.execute("INSERT INTO ? VALUES (?, ?)", values)


def update_db(tablename, col, value):
    query_data = (tablename, col, value)



def txt_clean(doc_id, res_txt, txt, stop_words_list):
    pp = re.compile("^[A-Za-z-]*$")
    try:
        #printable = set(string.printable)
        # myprintable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
        # txt_ = filter(lambda x: x in myprintable, txt)
        # print txt_
        txt_ = txt.decode("ascii", errors="ignore").encode()
    except Exception as e:
        return e
    sents = sent_tokenize(txt_)
    word_tokenizer = RegexpTokenizer(r'\w+')
    for i, sent in enumerate(sents):
        sent = rm_emails(sent)
        sent = contractions.fix(sent)
        words = word_tokenizer.tokenize(sent)
        insert_to_db(values=("docs", doc_id, '#'.join(words)))
        # words = rm_person_name(words)
        if DEBUG:
            print "\n\t[Cleaned sent %s] %s\n\t[Words]%s\n\t[Counted words]" % (i, sent, words),
        for word in words:
            if word.lower() not in stop_words_list and not word.isdigit() and (pp.match(word) is not None):
                if DEBUG:
                    print word.lower(),
                if word.lower() not in res_txt.keys():
                    res_txt[word.lower()] = 1
                else:
                    res_txt[word.lower()] += 1
    return res_txt


def cleanup_invalid_lines(lines):
    cleaned_txt = ''
    for i, line in enumerate(lines):
        # The first line is "From:", remove this line
        if i < 2 and 'From:' in line:
            pass
        elif 'Subject:' in line:
            line = line.replace('Subject:', '').replace('Re:', '')
            cleaned_txt = cleaned_txt + line.replace('\n', ' ')
        # ignore the lines without any [a-zA-Z] characters
        elif re.search("[a-zA-Z]", line) is not None:
            cleaned_txt = cleaned_txt + line.replace('\n', ' ')
    return cleaned_txt


def raw_txt_cleanup(path_to_txt_files):
    stop_words = []
    for w in open('stopword.txt', 'r'):
        w = w.strip()
        if w:
            stop_words.append(w)
    res = dict()
    for i, filename in enumerate(find_files(path_to_txt_files, "*")):
        if DEBUG:
            print "\n\n==[Doc %s]==\n" % filename
        lines = open(filename, 'r').readlines()
        txt = cleanup_invalid_lines(lines)
        if DEBUG:
            print "\tCleaned txt:%s" % txt
        tmp_res = txt_clean(filename.replace(DOCS_ROOT, ''), res, txt, stop_words)
        if isinstance(tmp_res, dict) is False:
            print "[Unicode Error]Doc:%s, err=%s" % (filename, tmp_res)
        else:
            res = tmp_res
    return res


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def main():
    start = time.time()
    all_words = raw_txt_cleanup(DOCS_ROOT)
    with open("all_words_count_rm_person_name.json", 'w+') as outfile:
        json.dump(all_words, outfile)
    outfile.close()

    print "Total time: %s sec" % (time.time() - start)


if __name__=="__main__":
    main()
