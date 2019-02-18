import socket
import gensim
import os
from multiprocessing.dummy import Pool
import math

SERV_PORT = 8306
WV_MODEL_BIN = "/home/{0}/workspace/lib/NASARIembed+UMBC_w2v.bin".format(os.environ['USER'])
WV_MODEL = "/home/{0}/workspace/lib/NASARIembed+UMBC_w2v_model".format(os.environ['USER'])

g_wv_model = None
g_serv_sock = None

g_sim_mode = 'wo'
#g_sim_mode = 'cosine'


def load_nasari_w2v():
    global g_wv_model
    if not os.path.isfile(WV_MODEL):
        g_wv_model = gensim.models.KeyedVectors.load_word2vec_format(WV_MODEL_BIN, binary=True) 
        g_wv_model.save(WV_MODEL)
    g_wv_model = gensim.models.KeyedVectors.load(WV_MODEL)
    return g_wv_model

def get_val(ele):
    return ele[0]

def weighted_overlap(v1, v2):
    dim = len(v1)
    v_idx = [x for x in range(1, dim+1)]
    v1_z = list(zip(v1, v_idx))
    v2_z = list(zip(v2, v_idx))
    v1_z.sort(key=get_val)
    v2_z.sort(key=get_val)
    v1_r = []
    v2_r = []
    for dim_i in range(1, dim+1):
        v1_r_i = [id_v1_x for id_v1_x, v1_x in enumerate(v1_z) if v1_x[1] == dim_i]
        v1_r.append(v1_r_i[0]+1)
        v2_r_i = [id_v2_x for id_v2_x, v2_x in enumerate(v2_z) if v2_x[1] == dim_i]
        v2_r.append(v2_r_i[0]+1)
    wo_pairs = []
    for i in range(dim):
        wo_pairs.append((v1_r[i], v2_r[i]))
    #print wo_pairs
    l_n = []
    for i in range(dim):
        l_n.append(math.pow(wo_pairs[i][0] + wo_pairs[i][1], -1))
    n = sum(l_n)
    l_d = []
    for i in range(dim):
        l_d.append(math.pow(2*(i+1), -1))
    d = sum(l_d)
    wo = math.sqrt(n / d)
    return wo

def compute_ws(param):
    global g_wv_model
    global g_serv_sock
    msg = param[0]
    addr = param[1]
    demsg = msg.split("#")
    word_1 = str(demsg[0].lower()).strip()
    word_2 = str(demsg[1].lower()).strip()
    if (word_1 in g_wv_model) and (word_2 in g_wv_model):
        if g_sim_mode == 'wo':
            ws = weighted_overlap(g_wv_model.wv[word_1], g_wv_model.wv[word_2])
        elif g_sim_mode == 'cosine':
            ws = g_wv_model.similarity(word_1, word_2)
        else:
            ws = 0
            print "[ERR]: Unsupported similarity mode!"
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

