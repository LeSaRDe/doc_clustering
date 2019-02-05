import sqlite3
import string
import re
from nltk import word_tokenize


def count_abc_words(sss):
    cnt = 0
    pp = re.compile("^[A-Za-z-]*$")
    words = word_tokenize(sss)
    for w in words:
        if pp.match(w) is not None:
            cnt += 1
    return cnt


def main():
    DOCS_ROOT = "/home/fcmeng/PycharmProjects/doc_similarity/20news18828.db"
    conn = sqlite3.connect(DOCS_ROOT)
    cur = conn.cursor()
    cur.execute("SELECT doc_id, pre_ner FROM docs WHERE parse_trees='bad_parse' or parse_trees is null order by doc_id")
    # cur.execute("SELECT doc_id, pre_ner FROM docs WHERE doc_id like '%hockey/54169%'")
    docs = cur.fetchall()
    cnt = 0
    for doc in docs:
        sentences = doc[1].split('\n')
        for i, sent in enumerate(sentences):
            num_punc = len(sent) - len(str(sent).translate(None, string.punctuation))
            try:
                punc_ratio = float(num_punc)/len(sent)
            except:
                punc_ratio = 0
            num_punc_include_space = sent.count(' ') + num_punc
            try:
                punc_include_space_ratio = float(num_punc_include_space)/len(sent)
            except:
                punc_include_space_ratio = 0
            num_words = len(sent.split())
            num_abc_words = count_abc_words(sent)
            try:
                num_abc_words_ratio = float(num_punc_include_space)/num_abc_words
            except:
                num_abc_words_ratio = 0
            # if len(sent) > 1100 or (num_words >= 100 and punc_include_space_ratio >= 0.2):
            # if num_punc < 200 and len(sent) >= 2000:
            # if len(sent) >= 900 and punc_include_space_ratio >= 0.2:
            if len(sent) >= 1000:
                cnt+=1
                print "[%s - %s] Sent length:%s" \
                      "\n\tPunctuations:%s" \
                      "\n\tPunc ratio:%s" \
                      "\n\tPunc include space:%s" \
                      "\n\tPunc include space ratio:%s" \
                      "\n\tNumber of words:%s" \
                      "\n\tNumber of Eng words:%s" \
                      "\n\tNumber of punc with space/Number of Eng words ratio:%s" \
                      "\n\t%s\n" % \
                      (doc[0], i, len(sent), num_punc, punc_ratio, num_punc_include_space, punc_include_space_ratio,
                       num_words, num_abc_words, num_abc_words_ratio, sent)
    print "Total %s" % cnt


if __name__ == "__main__":
    main()

