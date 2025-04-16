import torch
from torchdiffeq import odeint
import matplotlib.pyplot as plt
import time

# Basic 1-qubit operators in PyTorch
SIGMA_X = torch.tensor([[0, 1], [1, 0]], dtype=torch.cfloat)
SIGMA_Y = torch.tensor([[0, -1j], [1j, 0]], dtype=torch.cfloat)
SIGMA_Z = torch.tensor([[1, 0], [0, -1]], dtype=torch.cfloat)
SIGMA_M = torch.tensor([[0, 1], [0, 0]], dtype=torch.cfloat)
IDENTITY = torch.eye(2, dtype=torch.cfloat)

def commutator(A, B):
    return A @ B - B @ A

def anticommutator(A, B):
    return A @ B + B @ A

def flatten_complex_matrix(matrix):
    matrix = matrix.flatten()
    return torch.cat([matrix.real, matrix.imag])

def reconstruct_matrix_from_array(array, shape):
    half_len = array.numel() // 2
    real = array[:half_len].reshape(*shape)
    imag = array[half_len:].reshape(*shape)
    return real + 1j * imag

class LindbladSimulator:
    def __init__(self, hamiltonian_func, lindblad_operators, device='cpu'):
        self.H = hamiltonian_func
        self.L_ops = lindblad_operators
        self.device = device

    def evolve(self, rho0, times):
        rho0 = rho0.to(self.device)
        rho0_vec = flatten_complex_matrix(rho0)

        def master_eq(t, rho_vec):
            rho = reconstruct_matrix_from_array(rho_vec, rho0.shape)
            Ht = self.H(t)
            L_ops_t = [L(t) for L in self.L_ops]
            L_dags = [L.conj().T for L in L_ops_t]

            dissipator = sum(L @ rho @ L_dag for L, L_dag in zip(L_ops_t, L_dags))
            anti = sum(L_dag @ L for L, L_dag in zip(L_ops_t, L_dags))
            drho = -1j * commutator(Ht, rho) + dissipator - 0.5 * anticommutator(anti, rho)
            return flatten_complex_matrix(drho)

        result = odeint(master_eq, rho0_vec, times.to(self.device))
        return [reconstruct_matrix_from_array(r, rho0.shape).cpu() for r in result]

if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # Initial state |+⟩⟨+|
    psi0 = (1 / torch.sqrt(torch.tensor(2.))) * (
    torch.tensor([[1.0], [0.0]], dtype=torch.cfloat) +
    torch.tensor([[0.0], [1.0]], dtype=torch.cfloat)
)

    rho0 = psi0 @ psi0.T.conj()

    # Time-independent operators
    H = lambda t: 0.5 * SIGMA_Z.to(device)
    L1 = lambda t: torch.sqrt(torch.tensor(0.5)) * SIGMA_M.to(device)
    L2 = lambda t: torch.sqrt(torch.tensor(0.3)) * SIGMA_Z.to(device)

    sim = LindbladSimulator(H, [L1, L2], device)

    t0 = 0.0
    tf = 10.0
    steps = 1000
    times = torch.linspace(t0, tf, steps)

    start = time.time()
    evolution = sim.evolve(rho0, times)
    end = time.time()
    print(f"Simulation time: {end - start:.2f} seconds")

    # Plot populations and coherences
    rho_00 = [r[0, 0].real for r in evolution]
    rho_11 = [r[1, 1].real for r in evolution]
    rho_01_re = [r[0, 1].real for r in evolution]
    rho_01_im = [r[0, 1].imag for r in evolution]

    times_np = times.numpy()

    plt.figure()
    plt.plot(times_np, rho_00, label='ρ₀₀')
    plt.plot(times_np, rho_11, label='ρ₁₁')
    plt.plot(times_np, rho_01_re, label='Re(ρ₀₁)')
    plt.plot(times_np, rho_01_im, label='Im(ρ₀₁)')
    plt.xlabel("Time")
    plt.ylabel("Matrix elements")
    plt.title("Density Matrix Evolution (Custom Solver)")
    plt.grid(True)
    plt.legend()
    plt.show()
