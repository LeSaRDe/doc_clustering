import networkx as nx
import matplotlib.pyplot as plt
from networkx.linalg.laplacianmatrix import directed_laplacian_matrix
from numpy import linalg as LA
import numpy as np

def construct_dgraph():
    G = nx.DiGraph()
    G.add_nodes_from([1, 2, 3, 4])
    G.add_edge(1, 2, weight=1.0)
    G.add_edge(1, 3, weight=1.0)
    G.add_edge(1, 4, weight=1.0)
    G.add_edge(2, 3, weight=1.0)
    G.add_edge(3, 2, weight=1.0)
    G.add_edge(2, 4, weight=1.0)
    G.add_edge(3, 4, weight=1.0)
    return G

def spectrum(G):
    DL = directed_laplacian_matrix(G)
    eig_vals, eig_vects = LA.eig(DL)
    print "eig_vals = "
    print eig_vals
    print "eig_vects = "
    print np.asmatrix(eig_vects)
    return eig_vals, np.asmatrix(eig_vects)

def fourier_transform(v_sig, basis):
    f_sig = v_sig.dot(basis)
    print f_sig

def main():
    G = construct_dgraph()
    eig_vale, eig_vects = spectrum(G)
    sig = np.array([[10, 1, 1, 1]])
    fourier_transform(sig, eig_vects)
    test_mat = np.array([[1.0, 1.0, 1.0, 1.0],
                         [2.0, 2.0, 2.0, 2.0],
                         [3.0, 3.0, 3.0, 3.0],
                         [4.0, 4.0, 4.0, 4.0]])
    print sig.dot(test_mat)
    #nx.draw(G, with_labels=True)
    #plt.show()

main()
