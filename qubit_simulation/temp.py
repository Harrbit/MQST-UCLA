"""
noisy_three_qubit_sim.py
Minimal three-qubit crossresonance demo with noise and plots
=======================================================================

* Q0: control    * Q1: target    * Q2: spectator (idle here)

Hamiltonian (effective, computational subspace, hbar = 1)::

    H = (w_zx/2) Z0 X1                 # desired CR term
      + (w_ix/2)  X1                   # residual IX
      + (w_zz/2) Z0 Z1                 # residual ZZ
      + (w_zi/2) Z0 + (w_iz/2) Z1      # Stark shifts (optional)

Noise: amplitude-damping (T1) and pure dephasing (Tphi) on all qubits.

The script:
    1. Builds H and collapse operators.
    2. Computes Liouvillian L.
    3. Evolves the density matrix for a list of times.
    4. Plots |1> population of each qubit in three figures.

Dependencies: numpy, scipy, matplotlib (CPU only, no torch required)
"""

import numpy as np
import matplotlib.pyplot as plt
from functools import reduce
from scipy.linalg import expm

# ----------------------------------------------------------------------
# Basic 2x2 operators
I2 = np.eye(2, dtype=np.complex128)
X  = np.array([[0, 1], [1, 0]],             dtype=np.complex128)
Y  = np.array([[0, -1j], [1j, 0]],          dtype=np.complex128)
Z  = np.array([[1, 0], [0, -1]],            dtype=np.complex128)
SIGMA_M = np.array([[0, 1], [0, 0]],        dtype=np.complex128)  # lowering

# ----------------------------------------------------------------------
# Helpers
def kron(*ops):
    "Kronecker product of many matrices."
    return reduce(np.kron, ops)

def embed(op, which):
    "Promote a single-qubit operator to 3-qubit space."
    return kron(*(op if k == which else I2 for k in range(3)))

# Tensor operators
Z0, Z1, Z2 = (embed(Z, k) for k in range(3))
X1 = embed(X, 1)
SIGMA_M0, SIGMA_M1, SIGMA_M2 = (embed(SIGMA_M, k) for k in range(3))

# ----------------------------------------------------------------------
# Effective Hamiltonian builder
def h_eff(w_zx, w_ix=0.0, w_zz=0.0, w_zi=0.0, w_iz=0.0):
    return (w_zx/2) * Z0 @ X1 + (w_ix/2) * X1 + (w_zz/2) * Z0 @ Z1 \
         + (w_zi/2) * Z0 + (w_iz/2) * Z1

# ----------------------------------------------------------------------
# Collapse operators
def collapse_ops(t1, tphi, which):
    """Return list of sqrt(gamma)*L for one qubit."""
    out = []
    if t1 is not None and t1 > 0.0:
        out.append(np.sqrt(1.0/t1) * embed(SIGMA_M, which))
    if tphi is not None and tphi > 0.0:
        out.append(np.sqrt(1.0/tphi) * embed(Z, which))
    return out

# ----------------------------------------------------------------------
# Liouvillian: L vec(rho) = -i[H,rho] + sum(L rho L^† - 1/2 {L^†L,rho})
def liouvillian(H, collapses):
    dim = H.shape[0]
    eye = np.eye(dim, dtype=np.complex128)
    # Commutator part
    L = -1j * (np.kron(eye, H) - np.kron(H.conj().T, eye))
    # Dissipators
    for Lk in collapses:
        LdgL = Lk.conj().T @ Lk
        L += np.kron(Lk, Lk.conj()) \
           - 0.5 * np.kron(eye, LdgL) \
           - 0.5 * np.kron(LdgL.T, eye)
    return L

# ----------------------------------------------------------------------
# Evolution
def evolve_density(rho0, L, times):
    dim = rho0.shape[0]
    rho_vec0 = rho0.reshape(dim*dim, 1)
    trajectories = []
    for t in times:
        U = expm(L * t)
        rho_t = (U @ rho_vec0).reshape(dim, dim)
        trajectories.append(rho_t)
    return trajectories

# ----------------------------------------------------------------------
# Plot helper
def plot_evolution(times_ns, p0, p1, p2):
    for idx, probs in enumerate([p0, p1, p2]):
        plt.figure()
        plt.plot(times_ns, probs)
        plt.grid(True)
        plt.ylim(-0.1, 1.1)
        plt.xlabel("Time (ns)")
        plt.ylabel(f"P(qubit {idx} = |1>)")
        plt.title(f"Qubit {idx} excited-state population")
        plt.tight_layout()
        plt.show()

# ----------------------------------------------------------------------
if __name__ == "__main__":

    # ----- Parameters -----
    MHz = 2.0 * np.pi * 1.0e6         # convert MHz to angular frequency
    w_zx = 0.40 * MHz                 # dominant ZX coupling
    H = h_eff(w_zx)

    T1 = 100e-6 * 2.0 * np.pi         # rad^-1 units
    Tphi = 120e-6 * 2.0 * np.pi

    COPS = []
    for q in range(3):
        COPS += collapse_ops(T1, Tphi, q)

    # Liouvillian
    L = liouvillian(H, COPS)

    # Initial state |000>  (control excited)
    psi = kron(np.array([0,1], dtype=np.complex128),
               np.array([1,0], dtype=np.complex128),
               np.array([1,0], dtype=np.complex128))
    rho0 = np.outer(psi, psi.conj())

    # Time grid (0 .. 150 mus)
    times = np.linspace(0.0, 150e-6 * 2.0 * np.pi, 400)  # angular seconds
    rho_t_list = evolve_density(rho0, L, times)

    # Measure P(|1>) on each qubit
    P1_single = 0.5 * (I2 - Z)
    P0 = embed(P1_single, 0)
    P1 = embed(P1_single, 1)
    P2 = embed(P1_single, 2)

    p0, p1, p2 = [], [], []
    for rho in rho_t_list:
        p0.append(np.real(np.trace(rho @ P0)))
        p1.append(np.real(np.trace(rho @ P1)))
        p2.append(np.real(np.trace(rho @ P2)))

    # Plot
    times_ns = times / (2.0 * np.pi * 1.0e-9)
    plot_evolution(times_ns, np.array(p0), np.array(p1), np.array(p2))
