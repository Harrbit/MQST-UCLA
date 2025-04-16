import numpy as np
import matplotlib.pyplot as plt
from qutip import *

# Parameters
omega_q = 5.0 * 2 * np.pi * 1e9  # Qubit frequency (5 GHz)
eta_q = -200 * 2 * np.pi * 1e6    # Anharmonicity (-200 MHz)
num_levels = 4                     # 4-level system
t_gate = 70e-9                     # Gate time (70 ns)
sigma = t_gate / 6                 # Gaussian width
T1 = 100e-6                        # Relaxation time (100 μs)
T2 = 150e-6                        # Dephasing time (150 μs)

# Transmon Hamiltonian (diagonal in eigenbasis)
H0 = Qobj(np.diag([0, 
                   omega_q, 
                   2*omega_q + eta_q, 
                   3*omega_q + 3*eta_q]))

# Charge operator (connect neighboring levels)
n_operator = create(num_levels) + destroy(num_levels)  # σ_x like
n_operator_y = 1j*(destroy(num_levels) - create(num_levels))  # σ_y like

# Time-dependent coefficients
def envelope(t, args):
    return args['amp'] * np.exp(-(t - args['t_mid'])**2/(2*args['sigma']**2))

def drag(t, args):
    return args['alpha'] * (t - args['t_mid']) / args['sigma']**2 * envelope(t, args) / args['eta']

# Parameters dictionary
args = {
    'amp': np.pi/(np.sqrt(2*np.pi)*sigma),  # Pulse amplitude
    'alpha': 0.5,        # DRAG parameter
    'eta': abs(eta_q),   # Anharmonicity
    't_mid': t_gate/2,
    'sigma': sigma,
    't_gate': t_gate
}

# Combine Hamiltonian terms
H = [
    H0,
    [n_operator, envelope],
    [n_operator_y, drag]
]

# Noise operators
gamma1 = 1/T1
gamma_phi = 1/T2 - 1/(2*T1)
c_ops = [
    np.sqrt(gamma1) * destroy(num_levels),     # Relaxation
    np.sqrt(gamma_phi) * num(num_levels)/2    # Dephasing
]

# Initial state (|+> in qubit subspace)
psi0 = (basis(num_levels,0) + basis(num_levels,1)).unit()
# psi0 = basis(num_levels, 0).unit()  # Start in ground state

# Time points
times = np.linspace(0, t_gate, 1000)

# Run simulation
result = mesolve(H, psi0, times, c_ops, [], args=args)

# Calculate fidelity with target |+>
target = (basis(num_levels,0) + basis(num_levels,1)).unit()
fidelity = [fidelity(state, target) for state in result.states]

# Plot results
plt.figure(figsize=(10,6))
plt.plot(times * 1e9, fidelity, label='With Noise')
plt.xlabel('Time (ns)')
plt.ylabel('Fidelity')
plt.title('Transmon Qubit Gate Fidelity with DRAG Correction')
plt.legend()
plt.grid(True)
plt.show()