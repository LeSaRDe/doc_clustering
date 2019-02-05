import sqlite3
import numpy as np
import networkx as nx
from numpy import linalg as LA


SIM_THRESHOLD = 0.4


def get_words_from_db():
    conn = sqlite3.connect('20news-18828.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM all_words_count limit 300 where in_nasari=1')
    rows = cursor.fetchall()
    return rows


def build_graph(full_dicts):



def find_eig_gap(eig_values, num):
    diffs = []
    pos = []
    for i, eig in enumerate(eig_values):
        if i+1 < len(eig_values):
            diff = eig_values[i+1] - eig
            if len(diffs)<num:
                diffs.append(diff)
                pos.append(i+1)
            elif diff > min(diffs):
                to_rm = diffs.index(min(diffs))
                diffs.pop(to_rm)
                pos.pop(to_rm)
                diffs.append(diff)
                pos.append(i + 1)
        else:
            return dict(zip(pos, diffs))


def main():
    full_word_list = get_words_from_db()
    G = build_graph(full_word_list)
    eig_values, eig_vectors = LA.eigh(nx.normalized_laplacian_matrix(G).todense())
    num_of_top_eig_values = 5
    eig_gaps = find_eig_gap(eig_values, num_of_top_eig_values)
    print eig_gaps

main()
