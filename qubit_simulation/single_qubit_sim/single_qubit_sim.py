import numpy as np
from scipy.integrate import solve_ivp
import torch
import time
import matplotlib.pyplot as plt

SIG_X = torch.tensor([[0,1],[1,0]], dtype=torch.cfloat)
SIG_Y = torch.tensor([[0, -1j], [1j, 0]], dtype=torch.cfloat)
SIG_Z = torch.tensor([[1, 0], [0, -1]], dtype=torch.cfloat)
SIG_M = torch.tensor([[0, 1], [0, 0]], dtype=torch.cfloat)
SIG_P = torch.tensor([[0, 0], [1, 0]], dtype=torch.cfloat)
IDEN = torch.eye(2, dtype=torch.cfloat)

def commute(A, B):
    return A @ B - B @ A

def anticommute(A, B):
    return A @ B + B @ A

class OpenQuantumSolver:
    def __init__ (self, Hamiltonian, Lindbladians, device='cpu'):
        self.H = Hamiltonian
        self.L = Lindbladians
        self.device = device

    def MatToVec(self, vec, shape):
        l=vec.numel() // 2
        RealPart=vec[:l].reshape(*shape)
        ImagPart=vec[l:].reshape(*shape)
        return RealPart + 1j * ImagPart
    
    def MatFlat(self, matrix):
        matrix = matrix.flatten()
        return torch.cat([matrix.real, matrix.imag])
    
    def LindbladRHS(self, t, rho_vec):
        rho = self.MatToVec(rho_vec, self.rho0.shape)
        Ht = self.H(t)
        L_ops_t = [L(t) for L in self.L]
        L_dags = [L.conj().T for L in L_ops_t]

        dissipator = sum(L @ rho @ L_dag for L, L_dag in zip(L_ops_t, L_dags))
        anti = sum(L_dag @ L for L, L_dag in zip(L_ops_t, L_dags))
        drho = -1j * commute(Ht, rho) + dissipator - 0.5 * anticommute(anti, rho)
        return self.MatFlat(drho)
    
    def EvoRho(self, rho0, times):
        self.rho0 = rho0.to(self.device)
        rho0_vec = self.MatFlat(rho0)
        rho_t = [rho0_vec]
        dt = times[1] - times[0]
        for t in times[:-1]:
            drho = torch.tensor(self.LindbladRHS(t, rho_t[-1]), device=self.device)
            rho_t.append(rho_t[-1] + drho * dt)
        return [self.MatToVec(rho, rho0.shape).cpu() for rho in rho_t]
    
    def plot_rho(self, rho_t, times):
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        for i in range(2):
            for j in range(2):
                axes[i, j].plot(times, [rho[i, j].item() for rho in rho_t], label=f'rho[{i},{j}]')
                axes[i, j].set_xlabel('Time')
                axes[i, j].set_ylabel(f'rho[{i},{j}]')
                axes[i, j].legend()
        plt.tight_layout()
        plt.show()
        return fig, axes
    
def main():
    # Define Hamiltonian and Lindbladians
    H = lambda t: -0.5 * SIG_Z
    L1 = lambda t: np.sqrt(0.5) * SIG_M
    L2 = lambda t: np.sqrt(0.3) * SIG_P
    L = [L1, L2]

    # Initial state
    rho0 = torch.tensor([[0.5, 0.5], [0.5, 0.5]], dtype=torch.cfloat)

    # Time points
    times = np.linspace(0, 10, 1000)

    # Create solver and compute evolution
    solver = OpenQuantumSolver(H, L)
    start_time = time.time()
    rho_t = solver.EvoRho(rho0, times)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")

    # Plot results
    fig, axes = solver.plot_rho(rho_t, times)
    plt.show()
    return fig, axes
if __name__ == "__main__":
    main()
