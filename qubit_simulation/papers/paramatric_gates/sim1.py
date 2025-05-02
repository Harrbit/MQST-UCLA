# ---------------------------------------------------------------------
#  Parametric iSWAP / CZ gate simulator
#  Based on Caldwell et al., PRX Applied 10, 034050 (2018)
# ---------------------------------------------------------------------
import numpy as np
import qutip as qt

# -----------------------------
# Device & gate parameters
# -----------------------------
# Bare qubit properties (experiment of Ref. 1)
wF   = 2*np.pi*3.940e9          # fixed qubit ω_F          [rad/s]  :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}
wT   = 2*np.pi*4.582e9          # parked tunable qubit ω_T [rad/s]  :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}
etaF = 2*np.pi*180e6            # anharmonicities          [rad/s]  :contentReference[oaicite:4]{index=4}&#8203;:contentReference[oaicite:5]{index=5}
etaT = 2*np.pi*173e6

g     = 2*np.pi*6.3e6           # static capacitive coupling         :contentReference[oaicite:6]{index=6}&#8203;:contentReference[oaicite:7]{index=7}

# Effective interaction points (Table I)
gate_cfg = {
    "iswap": dict(geff=2*np.pi*3.9e6,  dur_ns=150),       # |10>↔|01| :contentReference[oaicite:8]{index=8}&#8203;:contentReference[oaicite:9]{index=9}
    "cz02" : dict(geff=2*np.pi*4.0e6,  dur_ns=210),       # |11>↔|02|
    "cz20" : dict(geff=2*np.pi*2.4e6,  dur_ns=290)        # |11>↔|20|
}

# Noise (drive-on values, Table I; we turn them into rates)
T1_F  = 25e-6   # choose upper end of reported range  :contentReference[oaicite:10]{index=10}&#8203;:contentReference[oaicite:11]{index=11}
T1_T  = 17e-6
Tphi_F= 20e-6
Tphi_T= 10e-6

# -----------------------------
# Hilbert space & operators
# -----------------------------
N = 3                              # keep |0>,|1>,|2>
aF  = qt.destroy(N)                # ladder operators
aT  = qt.destroy(N)

# Energy of each transmon (|n> ≈ √n oscillator with −η(n−1)/2 Kerr)
def H_transmon(w, eta):
    n = qt.num(N)
    return w*n - (eta/2.0)*n*(n-qt.qeye(N))

HF = qt.tensor(H_transmon(wF, etaF), qt.qeye(N))
HT = qt.tensor(qt.qeye(N),       H_transmon(wT, etaT))

# Static exchange (capacitive) g (XX+YY) in full space
sigma_x = lambda a: a + a.dag()
sigma_y = lambda a: -1j*a + 1j*a.dag()
Hint_static = g/4 * (qt.tensor(sigma_x(aF), sigma_x(aT)) +
                     qt.tensor(sigma_y(aF), sigma_y(aT)))

H0 = HF + HT + Hint_static            # “idle” Hamiltonian

# -----------------------------
# Effective parametric drives
# -----------------------------
# Projectors for relevant subspaces (computational+leakage)
P_10_01 = qt.tensor(qt.basis(N,1), qt.basis(N,0))*qt.tensor(qt.basis(N,0), qt.basis(N,1)).dag()
P_11_20 = qt.tensor(qt.basis(N,1), qt.basis(N,1))*qt.tensor(qt.basis(N,2), qt.basis(N,0)).dag()
P_11_02 = qt.tensor(qt.basis(N,1), qt.basis(N,1))*qt.tensor(qt.basis(N,0), qt.basis(N,2)).dag()

def drive(t, args):
    gate = args["gate"]
    geff = gate_cfg[gate]["geff"]
    if gate == "iswap":
        return geff
    elif gate == "cz02":
        return geff
    elif gate == "cz20":
        return geff
    return 0.0

H_drv = {
    "iswap": [ P_10_01 + P_10_01.dag(), drive ],
    "cz02" : [ np.sqrt(2)*(P_11_02 + P_11_02.dag()), drive ],
    "cz20" : [ np.sqrt(2)*(P_11_20 + P_11_20.dag()), drive ]
}

# -----------------------------
# Collapse operators (T₁, Tϕ)
# -----------------------------
def collapse_ops():
    c_ops=[]
    # amplitude damping
    gamma1_F = 1/T1_F
    gamma1_T = 1/T1_T
    for n in range(1,N):
        c_ops.append(np.sqrt(gamma1_F*n)*qt.tensor(qt.basis(N,n-1)*qt.basis(N,n).dag(), qt.qeye(N)))
        c_ops.append(np.sqrt(gamma1_T*n)*qt.tensor(qt.qeye(N), qt.basis(N,n-1)*qt.basis(N,n).dag()))
    # pure dephasing
    gamma_phi_F = 1/Tphi_F
    gamma_phi_T = 1/Tphi_T
    nF = qt.tensor(qt.num(N), qt.qeye(N))
    nT = qt.tensor(qt.qeye(N), qt.num(N))
    c_ops += [ np.sqrt(2*gamma_phi_F)*nF, np.sqrt(2*gamma_phi_T)*nT ]
    return c_ops

# -----------------------------
# Gate-level simulation helper
# -----------------------------
def simulate_gate(label, psi0=None, do_plot=False):
    dur = gate_cfg[label]["dur_ns"]*1e-9
    H = [H0, H_drv[label]]
    args = dict(gate=label)
    tlist = np.linspace(0, dur, 512)
    if psi0 is None:
        psi0 = qt.tensor(qt.basis(N,0), qt.basis(N,0))
    rho = qt.mesolve(H, psi0, tlist, collapse_ops(), [], args=args).states[-1]
    return rho

# Example: check population transfer for iSWAP starting in |10>
psi10 = qt.tensor(qt.basis(N,1), qt.basis(N,0))
rho_final = simulate_gate("iswap", psi10)
print("Population |01> =", qt.expect(qt.tensor(qt.basis(N,0), qt.basis(N,1))*qt.tensor(qt.basis(N,0), qt.basis(N,1)).dag(), rho_final))
