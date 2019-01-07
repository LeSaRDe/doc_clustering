import os, fnmatch
import re
import json
import contractions
import time
import sqlite3
from nltk.tokenize import sent_tokenize, RegexpTokenizer

DEBUG = False
DOCS_ROOT = "/home/fcmeng/PycharmProjects/20news-18828/"
conn = sqlite3.connect("20news-18828.db")

pattern1 = re.compile("^[A-Za-z0-9]*$")
pattern2 = re.compile(r'([\W0-9]+[\w]*|[\w]*[\W0-9]+)')
# pattern3 = re.compile(r'[\W0-9]+([\w]*[\W0-9]+')
pattern3 = re.compile(r'[\W0-9]*([\W0-9]+[\w]+|[\w]+[\W0-9]+)+[\W0-9]*')

def insert_pre_ner_to_db(values):
    cur = conn.cursor()
    cur.execute("INSERT INTO docs(doc_id, pre_ner) VALUES (?, ?)", values)


def cleanup_invalid_lines(lines):
    cleaned_txt = ''
    for i, line in enumerate(lines):
        # The first line is "From:", remove this line
        if i < 2 and 'From:' in line:
            pass
        elif 'Subject:' in line:
            line = line.replace('Subject:', '').replace('Re:', '')
            line = re.sub("^[>]+", "", line)
            cleaned_txt = cleaned_txt + line.replace('\n', ' ')
        # ignore the lines without any [a-zA-Z] characters
        elif re.search("[a-zA-Z]", line) is not None:
            line = re.sub("^[>]+", "", line)
            cleaned_txt = cleaned_txt + line.replace('\n', ' ')
    return cleaned_txt


def rm_emails(txt):
    return re.sub(r'[\w\.+-]+@[\w\.-]+\.\w+', '', txt)


def rm_noise(di, txt):
    raw_words = re.split("[ \t]+", txt)
    for rw in raw_words:
        # if (len(rw) > 20 and re.search("[a-zA-Z0-9]", rw) is None) or \
        if (len(rw) >= 16 and re.search("[@%#&*=+><~]", rw) is not None):
            print di, rw
        # if len(rw) > 15 and (pattern2.match(rw) or pattern3.match(rw)):
        #     print di, rw


def txt_clean(doc_id, res_txt, txt, stop_words_list):
    pp = re.compile("^[A-Za-z-]*$")
    try:
        txt_ = txt.decode("ascii", errors="ignore").encode()
    except Exception as e:
        print "[ERROR] %s" % e
        # insert_pre_ner_to_db(values=(doc_id, e))
        return
    txt_ = contractions.fix(txt_)
    sents = sent_tokenize(txt_)
    # word_tokenizer = RegexpTokenizer(r'\w+')
    for i, raw_sent in enumerate(sents):
        raw_sent = rm_emails(raw_sent)
        sent = rm_noise(doc_id, raw_sent)
    #
    #     words = word_tokenizer.tokenize(sent)
    #     # insert_to_db(values=("docs", doc_id, '#'.join(words)))
    #     # words = rm_person_name(words)
    #     if DEBUG:
    #         print "\n\t[Cleaned sent %s] %s\n\t[Words]%s" % (i, sent, words)
    #     for word in words:
    #         if word.lower() not in stop_words_list and not word.isdigit() and (pp.match(word) is not None):
    #             if DEBUG:
    #                 print word.lower(),
    #             if word.lower() not in res_txt.keys():
    #                 res_txt[word.lower()] = 1
    #             else:
    #                 res_txt[word.lower()] += 1
    # return res_txt


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
        txt_clean(filename.replace(DOCS_ROOT, ''), res, txt, stop_words)


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def main():
    raw_txt_cleanup(DOCS_ROOT)


if __name__=="__main__":
    main()