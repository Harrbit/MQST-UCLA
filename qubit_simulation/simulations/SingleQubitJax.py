import jax
import jax.numpy as jnp
from jax import jit, vmap
from jax.scipy.linalg import expm
from jax.experimental.ode import odeint
import matplotlib.pyplot as plt


SigX = jnp.array([[0, 1], [1, 0]], dtype=jnp.complex64)
SigY = jnp.array([[0, -1j], [1j, 0]], dtype=jnp.complex64)
SigZ = jnp.array([[1, 0], [0, -1]], dtype=jnp.complex64)
SigI = jnp.array([[1, 0], [0, 1]], dtype=jnp.complex64)
SigP = jnp.array([[0, 1], [0, 0]], dtype=jnp.complex64)
SigM = jnp.array([[0, 0], [1, 0]], dtype=jnp.complex64)

GammaAmp = 1/100e-6
p = 1.0
hbar = 1.0


GammaAmp = 1/100e-6
GammaPhase = 1/100e-6
p = 1.0
hbar = 1.0

L1Amp = (GammaAmp, SigM)
L1Phase = (GammaPhase, SigZ)


def vec(rho):
    return rho.flatten()

def unvec(rho_vec, dim):
    return rho_vec.reshape((dim, dim))

@jit
def commutator(A, B):
    return A @ B - B @ A

@jit
def lindblad_rhs(rho_vec, t, H, Ls):
    rho = unvec(rho_vec, 2)
    drho = -1j * commutator(H, rho)
    for L in Ls:
        Gamma = L[0]
        Lind = L[1]
        LdagL = Lind.conj().T @ Lind
        drho += (Lind @ rho @ Lind.conj().T - 0.5 * (LdagL @ rho + rho @ LdagL)) * Gamma
    return vec(drho)


class SingleQubitSim():
    def __init__(self, 
                 H, 
                 Ls, 
                 Rho0,
                 T,
                 TSteps,
                 ):
        self.TSteps = TSteps
        self.T = T
        self.TList = jnp.linspace(*self.T, self.TSteps)

        self.H = H
        self.Ls = Ls
        self.Rho0 = Rho0
        self.Sol = None
        self.PopExcited = None

    def run(self):
        self.Sol = odeint(lindblad_rhs, vec(self.Rho0), self.TList, self.H, self.Ls)
        self.PopExcited = jnp.real(jnp.array([unvec(rho, 2)[0, 0] for rho in self.Sol]))

T = (0.0, 100e-6)
TSteps = 1000
TList = jnp.linspace(*T, TSteps)

FreqQubit = 5.0e9
HamQubit = 2 * jnp.pi * FreqQubit * SigX

H = jnp.zeros((2, 2), dtype=jnp.complex64)
Ls = [L1Amp, L1Phase]
Rho0 = jnp.array([[1, 0], [0, 0]], dtype=jnp.complex64)
Sol = odeint(lindblad_rhs, vec(Rho0), TList, H, Ls)

PopExcited = jnp.real(jnp.array([unvec(rho, 2)[0, 0] for rho in Sol]))

plt.figure()
plt.ylim(-0.1, 1.1)
plt.plot(TList, PopExcited, label='Evolution of excited state population')
plt.xlabel('Time($\mu$s)')
plt.ylabel('Population')
plt.title('Single qubit dynamics with Dephasing and Amplitude Damping')
plt.legend()
plt.grid()
plt.show()