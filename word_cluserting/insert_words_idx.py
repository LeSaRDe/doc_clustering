

def insert_words_idx(db_conn, file_path):

    # dataset = file_path[:file_path.find('_')]
    # conn = sqlite3.connect("/home/fcmeng/workspace/data/%s.db" % dataset)
    cur = db_conn.cursor()

    infile = open(file_path, 'r').read()
    full_word_list = infile.split(",")

    db_exist_words_cnt = cur.execute("SELECT count(*) FROM words_idx").fetchone()[0]

    if 0 < db_exist_words_cnt != len(full_word_list):
        cur.close()
        raise Exception("[Err]Number of words count (%s) in the txt file doesn't match exist words_idx entries (%s), "
                        "need manual check!" % (len(full_word_list), db_exist_words_cnt))
    elif db_exist_words_cnt == len(full_word_list):
        print "Total %s words are already saved in words_idx, no need to insert." % db_exist_words_cnt
        return db_exist_words_cnt

    for i, word in enumerate(full_word_list):
        cur.execute('INSERT INTO words_idx (word, idx) VALUES (?, ?)', (word, i))
        if i % 500 == 0:
            db_conn.commit()

    db_conn.commit()
    cur.close()

    print "Total %s words insert into table words_idx." % len(full_word_list)
    return len(full_word_list)


def insert_word_pair_idx(db_conn, total):
    cur = db_conn.cursor()

    exist_rows = cur.execute('SELECT count(word_pair_idx) FROM words_sim').fetchone()[0]
    if 0 < exist_rows != total * (total-1) /2:
        cur.close()
        raise Exception(
            "[Err]Word pair idx already exist in table, but number of idx (%s) doesn't match total combination of "
            "words (%s)! Need manual check!" % (exist_rows, total * (total-1) /2))
    elif exist_rows == total * (total-1) /2:
        print "Total %s word pair index are already saved in words_idx, no need to insert." % exist_rows
        return

    import idx_bit_translate
    cnt = 0
    for i in range(total):
        for j in range(i+1, total):
            word_pair_idx = idx_bit_translate.keys_to_key(i, j)
            cur.execute('INSERT INTO words_sim (word_pair_idx) VALUES (?)', (word_pair_idx, ))
            cnt += 1
            if cnt % 500 == 0:
                db_conn.commit()
    db_conn.commit()
    cur.close()

    if cnt != total * (total-1) /2:
        raise Exception(
            "[Err]Insert %s Word pair idx into table, but doesn't match total combination of "
            "words (%s)! Need manual check!" % (cnt, total * (total - 1) / 2))

    print "Total %s word pair idx insert into table words_sim." % cnt


