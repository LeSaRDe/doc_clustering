import socket
import sqlite3
import time

TOTAL_NUM_PAIRS = 76124 * 76124/2
conn = sqlite3.connect("20news-18828.db")
cur = conn.cursor()


def get_words_from_db():
    cur.execute('SELECT word FROM all_words_count')
    rows = cur.fetchall()
    return rows


def words_sim_by_nasari(w1, w2):
    query = "%s#%s" % (w1, w2)
    serv_addr = ('localhost', 8306)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(query, serv_addr)
    msg, addr = sock.recvfrom(4096)
    return float(msg)


def sim_word_filter(full_word_list):
    start = time.time()
    cnt = 1
    for i, word1 in enumerate(full_word_list):
        for j, word2 in enumerate(full_word_list):
            if i < j:
                sim = words_sim_by_nasari(str(word1[0]), str(word2[0]))
                pair_str = "%s#%s#%s#%s" % (str(word1[0]), str(word2[0]), str(word2[0]), str(word1[0]))
                cur.execute("INSERT INTO pairwise_sim(word_pair, sim) VALUES (?, ?)", (pair_str, float(sim)))
                if cnt % 5000 == 0:
                    conn.commit()
                    print "%s, %s percent has processed. Time takes: %s" % (cnt, (float(cnt)*100/TOTAL_NUM_PAIRS), (time.time() - start))
                    start = time.time()
                cnt += 1
    conn.commit()
    cur.close()
    conn.close()


def main():
    init_start = time.time()
    full_word_list = get_words_from_db()
    sim_word_filter(full_word_list)
    print "\n\nTotal time: %s sec" % (time.time() - init_start)


main()
