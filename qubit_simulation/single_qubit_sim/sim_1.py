import numpy as np
import scipy.linalg as la
import scipy.integrate as integrate
import matplotlib.pyplot as plt

# Parameters for the transmon Hamiltonian
EC = 0.2  # GHz
EJ = 9.4  # GHz
n_max = 10  # Truncation for transmon states
num_levels = 4  # Truncated Hilbert space size (4-level transmon)

# Bath parameters (from the paper)
gx = 0.0057  # GHz
gz = 0.0044  # GHz
wx_c = 2 * np.pi * 1.948  # GHz
wz_c = 2 * np.pi * 0.00569  # GHz
b = 0.000598  # GHz
gamma_max = 2 * np.pi * 0.051  # GHz
gamma_min = 1e-4  # GHz
num_fluctuators = 10
temperature = 20e-3  # Kelvin
beta = 1 / (temperature * 0.02084)  # Convert to GHz^-1 (k_B/h = 0.02084 GHz/K)

# Physical constants
hbar = 1.0  # natural units where hbar = 1

# Helper: Transmon Hamiltonian
def transmon_hamiltonian(EC, EJ, n_max):
    n = np.arange(-n_max, n_max + 1)
    H = np.diag(4 * EC * n**2) - (EJ / 2) * (np.diag(np.ones(2*n_max), 1) + np.diag(np.ones(2*n_max), -1))
    eigvals, eigvecs = la.eigh(H)
    return eigvals[:num_levels], eigvecs[:, :num_levels]

# Noise operators (Charge and Phase operators)
def charge_operator(eigvecs, n_max):
    n = np.arange(-n_max, n_max + 1)
    charge_op = np.diag(n)
    return eigvecs.conj().T @ charge_op @ eigvecs

def cos_phi_operator(eigvecs, n_max):
    cos_phi_op = 0.5 * (np.diag(np.ones(2*n_max), 1) + np.diag(np.ones(2*n_max), -1))
    return eigvecs.conj().T @ cos_phi_op @ eigvecs

# Generate fluctuators for 1/f noise
def generate_fluctuators(t, num_fluctuators, gamma_min, gamma_max):
    gammas = np.exp(np.random.uniform(np.log(gamma_min), np.log(gamma_max), num_fluctuators))
    states = np.random.choice([-1, 1], size=num_fluctuators)
    fluctuators = np.zeros_like(t)
    for i, gamma in enumerate(gammas):
        switch_times = np.cumsum(np.random.exponential(1/gamma, int(t[-1]*gamma*10)))
        for time in switch_times:
            states[i] *= -1
            fluctuators[t >= time] += states[i]
    return fluctuators / np.sqrt(num_fluctuators)

# Ohmic bath correlation function
def ohmic_spectrum(omega, g, wc):
    return (2 * np.pi * g**2 * omega * np.exp(-np.abs(omega)/wc)) / (1 - np.exp(-beta * omega))

# Master equation dynamics
def master_equation(t, rho_flat, H_sys, Ax, Az, fluctuators, gx, gz, wx_c, wz_c, b):
    rho = rho_flat.reshape(H_sys.shape)
    commutator = -1j * (H_sys @ rho - rho @ H_sys)

    # Add fluctuators (classical noise on Az)
    H_fluctuator = Az * b * fluctuators[np.searchsorted(time_grid, t)]
    fluctuator_term = -1j * (H_fluctuator @ rho - rho @ H_fluctuator)

    # Simple Lindblad-type approximations for Ohmic baths
    Ax_dissipator = gx**2 * (Ax @ rho @ Ax - 0.5*(Ax @ Ax @ rho + rho @ Ax @ Ax))
    Az_dissipator = gz**2 * (Az @ rho @ Az - 0.5*(Az @ Az @ rho + rho @ Az @ Az))

    drho_dt = commutator + fluctuator_term + Ax_dissipator + Az_dissipator
    return drho_dt.flatten()

# Initialization
eigvals, eigvecs = transmon_hamiltonian(EC, EJ, n_max)
H_sys = np.diag(eigvals)
Ax = charge_operator(eigvecs, n_max)
Az = cos_phi_operator(eigvecs, n_max)

# Initial state: |1> state
rho0 = np.zeros((num_levels, num_levels), dtype=complex)
rho0[1, 1] = 1.0

# Time evolution setup
t_max = 2  # total simulation time (2 µs)
num_points = 500
time_grid = np.linspace(0, t_max, num_points)

# Generate fluctuators
fluctuators = generate_fluctuators(time_grid, num_fluctuators, gamma_min, gamma_max)

# Solve master equation
sol = integrate.solve_ivp(
    master_equation,
    [0, t_max],
    rho0.flatten(),
    args=(H_sys, Ax, Az, fluctuators, gx, gz, wx_c, wz_c, b),
    t_eval=time_grid,
    method='RK45'
)

# Extract populations
rho_t = sol.y.T.reshape(-1, num_levels, num_levels)  # shape: (num_points, num_levels, num_levels)
populations = np.real(np.diagonal(rho_t, axis1=1, axis2=2))  # shape: (num_points, num_levels)
populations = populations.T  # shape: (num_levels, num_points)

# Plot population dynamics
plt.figure(figsize=(8,5))
for i in range(num_levels):
    plt.plot(time_grid*1e6, populations[i], label=f'Level {i}')
plt.xlabel('Time (µs)')
plt.ylabel('Population')
plt.title('Transmon Qubit State Dynamics with Noise')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
