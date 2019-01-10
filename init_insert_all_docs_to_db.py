import os, fnmatch
import re
import contractions
import time
import sqlite3
from nltk.tokenize import sent_tokenize

DEBUG = False
DOCS_ROOT = "/home/fcmeng/PycharmProjects/20news-18828/"
conn = sqlite3.connect("20news-18828.db")
cur = conn.cursor()

# pattern1 = re.compile("^[A-Za-z0-9]*$")
# pattern2 = re.compile(r'([\W0-9]+[\w]*|[\w]*[\W0-9]+)')
# pattern3 = re.compile(r'[\W0-9]+([\w]*[\W0-9]+')
# pattern3 = re.compile(r'[\W0-9]*([\W0-9]+[\w]+|[\w]+[\W0-9]+)+[\W0-9]*')


def insert_pre_ner_to_db(values, cnt):
    cur.execute("INSERT INTO docs(doc_id, pre_ner) VALUES (?, ?)", values)
    if cnt % 1000 == 0:
        conn.commit()
        print "%s docs is processed." % cnt


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


def rm_noise(ss):
    # remove the words either without any characters/numbers or long messy words
    raw_words = re.split("[ \t]+", ss)
    cleaned_txt = []
    for rw in raw_words:
        if re.search("[a-zA-Z0-9]", rw) is None or (len(rw) >= 16 and re.search("[@%#&*=+><~]", rw) is not None):
            pass
        else:
            cleaned_txt.append(rw)
    return ' '.join(cleaned_txt)


def txt_clean(txt):
    # pp = re.compile("^[A-Za-z-]*$")
    try:
        encoded_txt = txt.decode("ascii", errors="ignore").encode()
    except Exception as e:
        print "[ERROR] %s" % e
        # insert_pre_ner_to_db(values=(doc_id, e))
        return
    contracted_txt = contractions.fix(encoded_txt)
    sents = sent_tokenize(contracted_txt)
    denoised_txt = []
    # word_tokenizer = RegexpTokenizer(r'\w+')
    for i, raw_sent in enumerate(sents):
        raw_sent = rm_emails(raw_sent)
        sent = rm_noise(raw_sent)
        if sent:
            denoised_txt.append(sent)
        # print "\t[Cleaned sent %s] %s" % (i, sent)
    return '\n'.join(denoised_txt)


def raw_txt_cleanup(path_to_txt_files):
    for i, filename in enumerate(find_files(path_to_txt_files, "*")):
        if DEBUG:
            print "\n\n==[Doc %s]==\n" % filename
        lines = open(filename, 'r').readlines()
        txt = cleanup_invalid_lines(lines)
        pre_ner_txt = txt_clean(txt)
        if DEBUG:
            print "PRE NER txt:\n%s" % pre_ner_txt
        if not DEBUG:
            insert_pre_ner_to_db((filename.replace(DOCS_ROOT, ''), pre_ner_txt), i)
    if not DEBUG:
        conn.commit()
        cur.close()
        conn.close()


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def main():
    start = time.time()
    raw_txt_cleanup(DOCS_ROOT)
    print "\n\nTotal time: %s sec" % (time.time() - start)


if __name__ == "__main__":
    main()