import socket
import sqlite3
import time
import multiprocessing
from multiprocessing import Process, Lock

conn = sqlite3.connect("20news-18828.db")
cur = conn.cursor()


def get_words_from_db():
    cur.execute('SELECT word FROM all_words_count where in_nasari=1')
    rows = cur.fetchall()
    return rows


def insert_to_table(res):
    # try:
    #     cur.execute("INSERT INTO pairwise_sim(word_pair, sim) VALUES (?, ?)", (pair_str, sim))
    # except Exception as e:
    #     g_inter_results
    print "\nInserting %s res to table..." % len(res)
    start = time.time()
    cur.executemany("INSERT INTO pairwise_sim(word_pair, sim) VALUES (?, ?)", res)
    print "\nInsert res takes %s..." % (time.time()-start)
    conn.commit()
    print "\nCommit finish"
    # g_inter_results = g_man.list([])
    # if counter % 5000 == 0:
    #     connection.commit()
    #     print "%s percent has processed." % counter


def words_sim_by_nasari(lock, word_ids, full_list):
    start = time.time()
    for w_id in word_ids:
        w1 = full_list[w_id]
        res = []
        for w2 in full_list[w_id+1:]:
            query = "%s#%s" % (w1[0], w2[0])
            serv_addr = ('localhost', 8306)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.sendto(query, serv_addr)
                msg, addr = sock.recvfrom(4096)
            except Exception as e:
                print "%s: %s" % (query, e)
                raw_input("here is error")
            pair_str = "%s#%s#%s#%s" % (w1[0], w2[0], w2[0], w1[0])
            res.append((pair_str, float(msg)))

        lock.acquire()
        insert_to_table(res)
        # g_inter_results.append((pair_str, float(msg)))
        #print "append %s %s" % (pair_str, msg)
        lock.release()
        print "%s comparision with %s other words is Done. Time:%s" % (w1, len(word_ids), (time.time() - start))


# ===Single thread version===
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


# def init(l):
#     global lock
#     lock = l


# ===Use multi-processing===
def sim_word_filter(full_word_list):
    ll = Lock()
    num_proc = multiprocessing.cpu_count()
    # num_proc = 1
    # pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count() - 1), initializer=init, initargs=(ll,))
    # pool = multiprocessing.Pool(1)
    idx_map = []
    for i in range(num_proc):
        # ids = [i + num_proc*x for x in range(len(full_word_list)/num_proc+1)]
        ids = range(i, len(full_word_list), num_proc)
        # print ids
        Process(target=words_sim_by_nasari, args=(ll, ids, full_word_list)).start()
        # idx_map.append([full_word_list[i], full_word_list[i+1:]])
        # for x in full_word_list[i+1:]:
        #     idx_map.append(full_word_list[i] + x)
    # pool.map(words_sim_by_nasari, idx_map)
    # insert_to_table()

    # pool.close()
    # pool.join()

    # cur.close()
    # conn.close()


def main():
    init_start = time.time()
    full_word_list = get_words_from_db()
    sim_word_filter(full_word_list)
    print "\n\nTotal time: %s sec" % (time.time() - init_start)


main()
