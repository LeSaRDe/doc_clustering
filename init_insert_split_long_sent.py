import sqlite3
import string
import re
from nltk import word_tokenize

SPLIT_LEN = 1000
SPLIT_WORDS_LEN = 100
commit = True


def split_sents(ss):
    new_list = []
    locs = []
    for i in range(1, len(ss)/SPLIT_LEN+1, 1):
        locs.append(i*SPLIT_LEN)
    for cnt, loc in enumerate(locs):
        while ss[loc] != " ":
            loc = loc -1
        locs[cnt] = loc
    locs = [0] + locs + [len(ss)]
    for cnt, loc in enumerate(locs):
        if cnt < len(locs)-1:
            new_list.append(ss[loc:locs[cnt+1]])
    return new_list


def split_sents_by_words(word_list):
    new_list = []
    locs = []
    for i in range(1, len(word_list) / SPLIT_WORDS_LEN + 1, 1):
        locs.append(i * SPLIT_WORDS_LEN)
    locs = [0] + locs + [len(word_list)]
    for cnt, loc in enumerate(locs):
        if cnt < len(locs) - 1:
            new_list.append(' '.join(word_list[loc:locs[cnt+1]]))
    return new_list


def count_abc_words(sss):
    cnt = 0
    pp = re.compile("^[A-Za-z-]*$")
    words = word_tokenize(sss)
    for w in words:
        if pp.match(w) is not None:
            cnt += 1
    return cnt


def rm_punc(ss):
    punc_translator = string.maketrans(string.punctuation, ' '*len(string.punctuation))
    return ss.translate(punc_translator)


def main():
    DOCS_ROOT = "/home/fcmeng/workspace/data/20news18828.db"
    conn = sqlite3.connect(DOCS_ROOT)
    cur = conn.cursor()
    cur.execute("SELECT doc_id, pre_ner FROM docs WHERE parse_trees='bad_parse' or parse_trees is null order by doc_id")
    docs = cur.fetchall()
    # step1: split long sent that length >= 2000
    print "\n\nProcessing long sent to 1000 each\n\n"
    for doc in docs:
        need_update = False
        sentences = doc[1].split('\n')
        new_sent_list = []
        for i, sent in enumerate(sentences):
            if len(sent) >= 2010:
                need_update = True
                print "%s [%s-%s] %s" % (doc[0], i, len(sent), sent)
                splitted_sents = split_sents(sent)
                for k, new_sent in enumerate(splitted_sents):
                    # splitted_sents[k] = new_sent + "."
                    print "Split sentences [%s] len [%s]" % (k, len(new_sent))
                new_sent_list = new_sent_list + splitted_sents
            else:
                new_sent_list.append(sent)
        if need_update:
            new_doc = '\n'.join(new_sent_list)
            if commit:
                cur.execute("UPDATE docs SET pre_ner=? WHERE doc_id=?", (new_doc, doc[0]))
            else:
                print new_doc
            print "Doc[%s] updated" % doc[0]
    conn.commit()

    # step2: find table and split into 100words/sentence
    print "\n\nProcessing long sent to 100 each\n\n"
    for doc in docs:
        need_update = False
        sentences = doc[1].split('\n')
        new_sent_list = []
        for i, sent in enumerate(sentences):
            num_punc = len(sent) - len(str(sent).translate(None, string.punctuation))
            try:
                punc_ratio = float(num_punc) / len(sent)
            except:
                punc_ratio = 0
            num_punc_include_space = sent.count(' ') + num_punc
            try:
                punc_include_space_ratio = float(num_punc_include_space) / len(sent)
            except:
                punc_include_space_ratio = 0
            num_words = len(sent.split())
            num_abc_words = count_abc_words(sent)
            try:
                num_abc_words_ratio = float(num_punc_include_space)/num_abc_words
            except:
                num_abc_words_ratio = 0
            if len(sent) >= 900 and punc_include_space_ratio >= 0.2 and num_abc_words_ratio >= 1.5: # must be table
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
                need_update = True
                rm_punc_sent = rm_punc(str(sent))
                rm_punc_words = word_tokenize(rm_punc_sent)
                if len(rm_punc_words) > SPLIT_WORDS_LEN:
                    print "%s [%s-%s] %s" % (doc[0], i, len(rm_punc_sent), rm_punc_sent)
                    splitted_sents = split_sents_by_words(rm_punc_words)
                    for k, new_sent in enumerate(splitted_sents):
                        # splitted_sents[k] = new_sent+"."
                        print "Split sentences [%s] len [%s]" % (k, len(new_sent))
                    new_sent_list = new_sent_list + splitted_sents
                else:
                    new_sent_list.append(rm_punc_sent)
            else:
                new_sent_list.append(sent)
        if need_update:
            new_doc = '\n'.join(new_sent_list)
            if commit:
                cur.execute("UPDATE docs SET pre_ner=? WHERE doc_id=?", (new_doc, doc[0]))
            else:
                print new_doc
            print "Doc[%s] updated" % doc[0]
    conn.commit()
    cur.close()
    conn.close()


# def main1():
#     DOCS_ROOT = "/home/fcmeng/PycharmProjects/doc_similarity/20news18828.db"
#     conn = sqlite3.connect(DOCS_ROOT)
#     cur = conn.cursor()
#     cur.execute("SELECT doc_id, pre_ner FROM docs order by doc_id")
#     docs = cur.fetchall()
#     for doc in docs:
#         sentences = doc[1].split('\n')
#         for i, sent in enumerate(sentences):
#             if 500 < len(sent) < 1000:
#                 print "%s [%s-%s] %s" % (doc[0], i, len(sent), sent)


if __name__ == "__main__":
    main()
