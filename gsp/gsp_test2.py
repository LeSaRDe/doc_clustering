from numpy import linalg as LA
from scipy.sparse import csgraph
import numpy as np

def spectrum(L):
    w, v = LA.eigh(L)
    return w, v

def laplacian():
    A = np.array([[0, 1, 1, 1, 1],
               [1, 0, 1, 1, 1],
               [1, 1, 0, 1, 1],
               [1, 1, 1, 0, 1],
               [1, 1, 1, 1, 0]])
    L = csgraph.laplacian(A, normed=True)
    return L

def main():
    L_norm = laplacian()
    print "normalized laplacian = "
    print L_norm
    eig_vals, eig_vects = spectrum(L_norm)
    eig_idx_sorted = np.flip(eig_vals.argsort()[::-1])
    eig_vals = eig_vals[eig_idx_sorted]
    eig_vects = eig_vects[:, eig_idx_sorted]
    print "eigen values = "
    print eig_vals
    print "eigen vectors = "
    print eig_vects
    print "verify:"
    print np.diag(eig_vals)
    print np.matmul(np.matmul(eig_vects, np.diag(eig_vals)), LA.inv(eig_vects))

main()
