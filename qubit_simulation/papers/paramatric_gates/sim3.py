import numpy as np
import matplotlib.pyplot as plt

I = np.array([[1, 0],
              [0, 1]], dtype=complex)
X = np.array([[0, 1],
              [1, 0]], dtype=complex)
Y = np.array([[0, -1j],
              [1j, 0]], dtype=complex)
Z = np.array([[1, 0],
              [0, -1]], dtype=complex)
pauli1 = [I, X, Y, Z]

def kron(*ops):
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out

pauli2 = [kron(p, q) for p in pauli1 for q in pauli1]

U_iSWAP = np.array([[1, 0,   0,   0],
                    [0, 0, 1j,   0],
                    [0, 1j, 0,   0],
                    [0, 0,   0,   1]], dtype=complex)

U_CZ    = np.diag([1, 1, 1, -1]).astype(complex)

def amplitude_damping(p):
    E0 = np.array([[1, 0],
                   [0, np.sqrt(1-p)]], complex)
    E1 = np.array([[0, np.sqrt(p)],
                   [0, 0]], complex)
    return [E0, E1]

def phase_damping(p):
    E0 = np.array([[1, 0],
                   [0, np.sqrt(1-p)]], complex)
    E1 = np.array([[0, 0],
                   [0, np.sqrt(p)]], complex)
    return [E0, E1]

def two_qubit_noise(T1, T2, t_gate):
    p_AD = 1 - np.exp(-t_gate/T1)
    p_deph_total = 1 - np.exp(-t_gate/T2)
    p_PD = max(p_deph_total - 0.5*p_AD, 0)

    kraus_single = [Ka @ Kp
                    for Ka in amplitude_damping(p_AD)
                    for Kp in phase_damping(p_PD)]
    kraus_two = [kron(K1, K2) for K1 in kraus_single for K2 in kraus_single]

    dim = 4
    S = np.zeros((dim*dim, dim*dim), complex)
    for K in kraus_two:
        S += np.kron(K, K.conj())
    return S

def unitary_super(U):
    return np.kron(U, U.conj())

def ptm(superop):
    R = np.zeros((16, 16))
    for i, Pi in enumerate(pauli2):
        vi = Pi.flatten()
        for j, Pj in enumerate(pauli2):
            vj = Pj.flatten()
            R[i, j] = np.real(np.vdot(vi, superop @ vj)) / 2
    return R

specs = {
    "iSWAP": dict(U=U_iSWAP, t=150e-9, T1=15e-6, T2=4.6e-6),
    "CZ"   : dict(U=U_CZ,     t=210e-9, T1=12e-6, T2=10.2e-6),
}

fig, axs = plt.subplots(1, 2, figsize=(10, 4))
for ax, (name, s) in zip(axs, specs.items()):
    S = two_qubit_noise(s["T1"], s["T2"], s["t"]) @ unitary_super(s["U"])
    R = ptm(S)
    im = ax.imshow(R, vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_title(f"{name} gate")
    ax.set_xlabel("Input Pauli index")
    ax.set_ylabel("Output Pauli index")

fig.colorbar(im, ax=axs, shrink=0.8, location='right')
fig.tight_layout()
plt.show()
