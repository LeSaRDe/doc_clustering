import socket
import sqlite3
import time
import multiprocessing
from multiprocessing import Manager

conn = sqlite3.connect("20news-18828.db")
cur = conn.cursor()
#inter_result = []

def get_words_from_db():
    cur.execute('SELECT word FROM all_words_count where in_nasari=1')
    rows = cur.fetchall()
    return rows


def insert_to_table():
    # try:
    #     cur.execute("INSERT INTO pairwise_sim(word_pair, sim) VALUES (?, ?)", (pair_str, sim))
    # except Exception as e:
    #     g_inter_results
    global g_inter_results, g_ll, g_man
    print "\nInserting %s res to table..." % len(g_inter_results)
    start = time.time()
    g_ll.acquire()
    cur.executemany("INSERT INTO pairwise_sim(word_pair, sim) VALUES (?, ?)", g_inter_results)
    print "\nInsert res takes %s..." % (time.time()-start)
    #conn.commit()
    print "\nCommit finish"
    g_inter_results = g_man.list([])
    g_ll.release()
    # if counter % 5000 == 0:
    #     connection.commit()
    #     print "%s percent has processed." % counter


def words_sim_by_nasari((w1, w2)):
    global g_inter_results, g_ll
    query = "%s#%s" % (w1, w2)
    serv_addr = ('localhost', 8306)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(query, serv_addr)
    msg, addr = sock.recvfrom(4096)
    pair_str = "%s#%s#%s#%s" % (w1, w2, w2, w1)

    g_ll.acquire()
    # insert_to_table(pair_str, float(msg))
    g_inter_results.append((pair_str, float(msg)))
    #print "append %s %s" % (pair_str, msg)
    g_ll.release()
    #print "lock released"
    # global counter
    # counter += 1
    # lock.release()
    # return float(msg)


# def sim_word_filter(full_word_list):
#     start = time.time()
#     cnt = 1
#     for i, word1 in enumerate(full_word_list):
#         for j, word2 in enumerate(full_word_list):
#             if i < j:
#                 sim = words_sim_by_nasari(str(word1[0]), str(word2[0]))
#                 pair_str = "%s#%s#%s#%s" % (str(word1[0]), str(word2[0]), str(word2[0]), str(word1[0]))
#                 cur.execute("INSERT INTO pairwise_sim(word_pair, sim) VALUES (?, ?)", (pair_str, float(sim)))
#                 if cnt % 5000 == 0:
#                     conn.commit()
#                     print "%s, %s percent has processed. Time takes: %s" % (cnt, (float(cnt)*100/TOTAL_NUM_PAIRS), (time.time() - start))
#                     start = time.time()
#                 cnt += 1
#     conn.commit()
#     cur.close()
#     conn.close()

#def init(l):
#    global lock
#    lock = l
    #inter_result = inter_res


# Use multi-processing
def sim_word_filter(full_word_list):
    #ll = multiprocessing.Lock()
    global g_inter_results, g_ll, g_man
    g_man = Manager()
    g_inter_results = g_man.list([])
    g_ll = g_man.Lock()

    #inter_res = []
    #pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count() - 1), initializer=init, initargs=(ll,))
    pool = multiprocessing.Pool(8)
    for i in range(len(full_word_list)):
        start = time.time()
        idx_map = []
        for x in full_word_list[i+1:]:
            idx_map.append(full_word_list[i] + x)
        pool.map(words_sim_by_nasari, idx_map)
        insert_to_table()
        # conn.commit()
        print "%s iteration is Done. Time:%s" % (i, (time.time() - start))
    pool.close()
    pool.join()

    # conn.commit()
    cur.close()
    conn.close()


def main():
    init_start = time.time()
    full_word_list = get_words_from_db()
    sim_word_filter(full_word_list)
    print "\n\nTotal time: %s sec" % (time.time() - init_start)


main()
