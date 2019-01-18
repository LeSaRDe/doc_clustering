import socket
import sqlite3

conn = sqlite3.connect("20news-18828.db")
cur = conn.cursor()


def get_words_from_db():
    cur.execute('SELECT word FROM all_words_count')
    rows = cur.fetchall()
    return rows


def words_sim_by_nasari((w)):
    query = "%s#%s" % (w, w)
    serv_addr = ('localhost', 8306)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(query, serv_addr)
    msg, addr = sock.recvfrom(4096)
    return float(msg)


def main():
    full_word_list = get_words_from_db()
    cnt = 1
    for i, word in enumerate(full_word_list):
        sim = words_sim_by_nasari(str(word[0]))
        if sim == 0:
            cur.execute("UPDATE all_words_count SET in_nasari=? WHERE word=?", (0, str(word[0])))
            cnt += 1
        else:
            cur.execute("UPDATE all_words_count SET in_nasari=? WHERE word=?", (1, str(word[0])))
        if (i+1) % 1000 == 0:
            conn.commit()
            print "%s processed" % (i+1)
    print "Total: %s" % cnt
    conn.commit()
    cur.close()
    conn.close()


main()