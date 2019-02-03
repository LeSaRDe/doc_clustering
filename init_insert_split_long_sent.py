import sqlite3


def splite_sents(ss):
    new_list = []
    locs = []
    for i in range(1, len(ss)/2000+1,1):
        locs.append(i*2000)
    for cnt, loc in enumerate(locs):
        while ss[loc] != " ":
            loc = loc -1
        locs[cnt] = loc
    locs = [0] + locs + [len(ss)]
    for cnt, loc in enumerate(locs):
        if cnt < len(locs)-1:
            new_list.append(ss[loc:locs[cnt+1]])
    return new_list


def main():
    DOCS_ROOT = "/home/fcmeng/PycharmProjects/doc_similarity/20news18828.db"
    conn = sqlite3.connect(DOCS_ROOT)
    cur = conn.cursor()
    cur.execute("SELECT doc_id, pre_ner FROM docs order by doc_id")
    docs = cur.fetchall()
    for doc in docs:
        need_update = False
        sentences = doc[1].split('\n')
        new_sent_list = []
        for i, sent in enumerate(sentences):
            if len(sent) > 2000:
                need_update = True
                # print "%s [%s-%s] %s" % (doc[0], i, len(sent), sent)
                splitted_sents = splite_sents(sent)
                # for k, new_sent in enumerate(splitted_sents):
                #     print "Split sentences [%s] len [%s]" % (k, len(new_sent))
                new_sent_list = new_sent_list + splitted_sents
            else:
                new_sent_list.append(sent)
        if need_update:
            new_doc = '\n'.join(new_sent_list)
            cur.execute("UPDATE docs SET pre_ner=? WHERE doc_id=?", (doc[0], new_doc))
            print "Doc[%s] updated" % doc[0]
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()