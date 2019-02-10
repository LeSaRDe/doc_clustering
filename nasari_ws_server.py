import socket
import gensim
import os
from multiprocessing.dummy import Pool

SERV_PORT = 8306
WV_MODEL_BIN = "/home/fcmeng/workspace/lib/NASARIembed+UMBC_w2v.bin"
WV_MODEL = "/home/fcmeng/workspace/lib/NASARIembed+UMBC_w2v_model"

g_wv_model = None
g_serv_sock = None


def load_nasari_w2v():
    global g_wv_model
    if not os.path.isfile(WV_MODEL):
        g_wv_model = gensim.models.KeyedVectors.load_word2vec_format(WV_MODEL_BIN, binary=True) 
        g_wv_model.save(WV_MODEL)
    g_wv_model = gensim.models.KeyedVectors.load(WV_MODEL)
    return g_wv_model


def compute_ws(param):
    global g_wv_model
    global g_serv_sock
    msg = param[0]
    addr = param[1]
    demsg = msg.split("#")
    word_1 = str(demsg[0].lower()).strip()
    word_2 = str(demsg[1].lower()).strip()
    if (word_1 in g_wv_model) and (word_2 in g_wv_model):
        ws = g_wv_model.similarity(word_1, word_2)
    else:
        ws = 0
        print "[ERR]: at least one of the words does not exist: " + word_1 + ", " + word_2
    print "[DBG]: " + word_1 + ":" + word_2 + ":" + str(ws)
    g_serv_sock.sendto(str(ws), addr)


def main():
    global g_wv_model
    global g_serv_sock
    g_serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    g_serv_sock.bind(("", SERV_PORT))
    t_pool = Pool(500)
    load_nasari_w2v()
    print "[DBG]: NASARI model loaded in."
    #print g_wv_model['customer']
    #print g_wv_model['notice']
    while True:
       msg, addr = g_serv_sock.recvfrom(4096)
       param = (msg, addr)
       l_param = list()
       l_param.append(param)
       print l_param
       t_pool.map(compute_ws, l_param)

main()
#load_nasari_w2v()

