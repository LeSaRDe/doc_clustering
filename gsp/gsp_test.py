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

def heat_kernel_func(G, eig_val, tau):
    return np.exp(-tau * eig_val / G.lmax)

def heat_kernel(G, tau):
    h_g = []
    normalize = False
    #norm = np.linalg.norm(kernel(G.e, tau)) if normalize else 1
    norm = 1
    for i in range(len(G.e)):
        h_eig_val = heat_kernel_func(G, G.e[i], tau) / norm
        h_g.append(h_eig_val)
    print h_g
    return h_g

def main():
    plotting.BACKEND = 'matplotlib'
    plt.rcParams['figure.figsize'] = (10, 200)
    G = gen_graph()
    G.compute_laplacian('normalized')
    G.compute_fourier_basis(recompute=True)
    G.compute_differential_operator()
    print "Laplacian = "
    print G.L
    print "Fourier Basis  = "
    print G.U
    print "Eigenvals = "
    print G.e
    G.set_coordinates('ring2D')
    signal = np.array([10,10,10,10,1])
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
    filter_g = filters.Heat(G, tau=3, normalize=True)
    print "heat kernel = "
    print filter_g
    filtered_signal = filter_g.filter(signal, method='exact')
    print "Filter Results = "
    print filtered_signal
    fig, axes = plt.subplots(2, 1, figsize=(10,20))
    G.set_coordinates('ring2D')
    G.plot_signal(filtered_signal, ax=axes[0])
    G.set_coordinates('line1D')
    G.plot_signal(filtered_signal, ax=axes[1])
    fig.tight_layout()
    plt.title('Filtered Signal')

    print "filter freq resp = "
    y = filter_g.evaluate(G.e)
    print y

    fled_freq = np.array([15.1304, -0.2792, 0.0578, -0.2836, -0.1779])
    fled_sig = G.igft(fled_freq)
    print fled_sig
    #fig, ax_f = plt.subplots()
    #filter_g.plot(plot_eigenvalues=True, ax=ax_f)

    h_g = heat_kernel(G, 10)


    plotting.show()
    #print G

main()
