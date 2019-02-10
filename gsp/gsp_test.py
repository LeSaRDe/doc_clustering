import numpy as np
import matplotlib.pyplot as plt
from pygsp import graphs, filters, plotting
import time

def gen_graph():
    adj_mat = np.array([[0,1,1,1,1],[1,0,1,1,1],[1,1,0,1,1],[1,1,1,0,1],[1,1,1,1,0]])
    G = graphs.Graph(adj_mat)
    return G

def filter_func(x):
    tau = 1
    return 1. / (1. + tau*x)

def main():
    plotting.BACKEND = 'matplotlib'
    plt.rcParams['figure.figsize'] = (10, 200)
    G = gen_graph()
    G.compute_laplacian('normalized')
    G.compute_fourier_basis(recompute=True)
    G.compute_differential_operator()
    print "Fourier Basis  = "
    print G.U
    print "Eigenvals = "
    print G.e
    G.set_coordinates('ring2D')
    signal = np.array([10,10,10,3,1])
    #fig, axes = plt.subplots(2, 1, figsize=(10,20))
    #G.plot_signal(signal, ax=axes[0])
    G.plot_signal(signal)
    plt.title('Signal')
    
    G.set_coordinates('line1D')
    #G.plot_signal(G.U[:, 0:4], ax=axes[1])
    G.plot_signal(G.U[:, 0:4])
    plt.title('Eigenvectors')
    #for i in range(0, 5):
    #    G.plot_signal(G.U[:, i], ax=axes[i+1])
    #fig.tight_layout()

    freq_response = G.gft(signal)
    print "Frequence Response = "
    print freq_response
    fig, axes = plt.subplots(2, 1, figsize=(10,20))
    G.set_coordinates('ring2D')
    G.plot_signal(freq_response, ax=axes[0])
    G.set_coordinates('line1D')
    G.plot_signal(freq_response, ax=axes[1])
    fig.tight_layout()
    plt.title('Frequence Response')

    #filter_g = filters.Filter(G, filter_func)
    filter_g = filters.Heat(G, tau=10)
    filtered_signal = filter_g.filter(signal)
    print "Filter Results = "
    print filtered_signal
    fig, axes = plt.subplots(2, 1, figsize=(10,20))
    G.set_coordinates('ring2D')
    G.plot_signal(filtered_signal, ax=axes[0])
    G.set_coordinates('line1D')
    G.plot_signal(filtered_signal, ax=axes[1])
    fig.tight_layout()
    plt.title('Filtered Signal')
    #fig, ax_f = plt.subplots()
    #filter_g.plot(plot_eigenvalues=True, ax=ax_f)


    plotting.show()
    #print G

main()
