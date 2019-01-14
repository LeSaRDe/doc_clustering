import sqlite3
import time

conn = sqlite3.connect("20news-18828.db")
cur = conn.cursor()


def count_words():
    final_list = dict()
    cur.execute("SELECT word_list FROM docs")
    all_words = cur.fetchall()
    for i, each in enumerate(all_words):
        word_list = eval(each[0])
        for each_word in word_list:
            if each_word not in final_list.keys():
                final_list[each_word] = 1
            else:
                final_list[each_word] += 1
        if i % 1000 == 0:
            print "%s doc words counted." % i
    return final_list


def save_words(all):
    cnt = 1
    for key, value in all.items():
        cur.execute("INSERT INTO all_words_count(word, count) VALUES (?, ?)", (str(key), int(value)))
        if cnt % 5000 == 0:
            conn.commit()
            print "%s words inserted" % cnt
        cnt += 1
    conn.commit()
    cur.close()
    conn.close()


def main():
    start = time.time()
    all_words = count_words()
    print "Total time: %s sec, Total words: %s" % ((time.time() - start), len(all_words))
    start = time.time()
    save_words(all_words)
    print "Total time: %s sec" % (time.time() - start)


if __name__ == "__main__":
    main()