import socket
import sqlite3
import numpy as np
from sklearn.cluster import SpectralClustering


SIM_THRESHOLD = 0.4


def get_words_from_db(db_file, table_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''SELECT key FROM %s limit 300''' % table_name)
    rows = cursor.fetchall()
    return rows


def words_sim_by_nasari(w1, w2):
    query = "%s#%s" % (w1, w2)
    serv_addr = ('localhost', 8306)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(query, serv_addr)
    msg, addr = sock.recvfrom(4096)
    return float(msg)


def sim_word_filter(full_word_list):
    full_words_sim_dict = dict()
    word_idx_list = []
    for i, word1 in enumerate(full_word_list):
        single_word_sim_dict = dict()
        for j, word2 in enumerate(full_word_list):
            if i < j:
                sim = words_sim_by_nasari(str(word1[0]), str(word2[0]))
                if sim >= SIM_THRESHOLD:
                    single_word_sim_dict[j] = sim
                    print "%s - %s: %s" % (word1, word2, sim)
                    if i not in word_idx_list:
                        word_idx_list.append(i)
                    if j not in word_idx_list:
                        word_idx_list.append(j)
        if len(single_word_sim_dict) > 0:
            full_words_sim_dict[i] = single_word_sim_dict
    return full_words_sim_dict, len(word_idx_list)


def build_aff_matrix(full_dicts, size):
    aff_mat = np.zeros([size, size], dtype=float)
    idx_mapping = dict()
    idx_backwards_mapping = dict()
    for org_idx, sim_dict in full_dicts.items():
        if org_idx not in idx_mapping.keys():
            xidx = len(idx_mapping)
            idx_mapping[org_idx] = xidx
            idx_backwards_mapping[xidx] = org_idx
            aff_mat[xidx][xidx] = 1
        else:
            xidx = idx_mapping[org_idx]
        for sim_word_idx, sim in sim_dict.items():
            if sim_word_idx not in idx_mapping.keys():
                yidx = len(idx_mapping)
                idx_mapping[sim_word_idx] = yidx
                idx_backwards_mapping[yidx] = sim_word_idx
                aff_mat[yidx][yidx] = 1
            else:
                yidx = idx_mapping[sim_word_idx]
            aff_mat[xidx][yidx] = sim
            aff_mat[yidx][xidx] = sim
    return aff_mat, idx_backwards_mapping


def spectral_clustering(mat):
    sc = SpectralClustering(n_clusters=4, eigen_solver=None, random_state=None, n_init=10,affinity='precomputed', assign_labels='kmeans', n_jobs=-1).fit_predict(mat)
    return sc


def main(db_file, table_name):
    full_word_list = get_words_from_db(db_file, table_name)
    full_words_sim_dict, total_cnt = sim_word_filter(full_word_list)
    aff_matrix, idx_map = build_aff_matrix(full_words_sim_dict, total_cnt)
    cluster_labels = spectral_clustering(aff_matrix)
    for i, label in enumerate(cluster_labels):
        print "%s - %s" % (label, full_word_list[idx_map[i]])


main('all_words.db', 'all_words_count_010119')
