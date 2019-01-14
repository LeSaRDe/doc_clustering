#!/usr/bin/python
# -*- coding: utf-8 -*-

from nltk.tokenize import RegexpTokenizer
import re
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
cur = conn.cursor()

word_tokenizer = RegexpTokenizer(r'\w+')


def rm_person_name(word_tokens):
    tags = list(ner_tagger.tag(word_tokens))
    new_words_tokens = []
    for tag in tags:
        if tag[1] != 'PERSON':
            new_words_tokens.append(tag[0])
    if DEBUG:
        print "\t\t[Cleaned sent]: %s" % new_words_tokens
    return new_words_tokens


def update_db(values):
    cur.execute("UPDATE docs SET word_list=? WHERE doc_id=?", values)
    conn.commit()


def rm_digs_and_person_name(word_tokens):
    new_words_tokens = []
    for w in word_tokens:
        if not w.isdigit():
            new_words_tokens = new_words_tokens + rm_person_name(w.replace('_', ' ').split())
    return new_words_tokens


def sent_clean(doc_words, ss, stop_words_list):
    pp = re.compile("^[A-Za-z-]*$")

    tokened_words = word_tokenizer.tokenize(ss)
    try:
        nered_words = rm_person_name(tokened_words)
    except:
        try:
            nered_words = rm_digs_and_person_name(tokened_words)
        except Exception as ee:
            print "\tSecond attempt fails."
            return "[NER server error]%s" % ee

    for word in nered_words:
        if word.lower() not in stop_words_list and not word.isdigit() and (pp.match(word) is not None):
            if DEBUG:
                print "\t\t%s" % word.lower(),
            if word.lower() not in doc_words.keys():
                doc_words[word.lower()] = 1
            else:
                doc_words[word.lower()] += 1
    return doc_words


def select_txt_to_process():
    # cur.execute("SELECT * FROM docs WHERE word_list is null limit 100")
    cur.execute("SELECT * FROM docs WHERE word_list like '%NER server error%'")
    # cur.execute("SELECT * FROM docs WHERE doc_id='rec.sport.hockey/53613'")
    return cur.fetchall()


def raw_txt_cleanup():
    stop_words = []
    for w in open('stopword.txt', 'r'):
        w = w.strip()
        if w:
            stop_words.append(w)

    txt_to_process = select_txt_to_process()

    for i, row in enumerate(txt_to_process):
        print "\n\n==[Doc %s]==\n" % row[0]
        final_words = dict()
        sents = row[1].split('\n')
        for j, sent in enumerate(sents):
            if DEBUG:
                print "\n\t[%s]Sent: %s" % (j, sent),
            final_words = sent_clean(final_words, str(sent), stop_words)
            if not isinstance(final_words, dict):
                break
        if DEBUG:
            print "\n\tFinal words: %s" % final_words
        else:
            update_db(values=(str(final_words), row[0]))
        print "\n%s processed." % row[0]

    cur.close()
    conn.close()


def main():
    start = time.time()
    raw_txt_cleanup()
    # with open("all_words_count_rm_person_name.json", 'w+') as outfile:
    #     json.dump(all_words, outfile)
    # outfile.close()
    print "Total time: %s sec" % (time.time() - start)


if __name__ == "__main__":
    main()
