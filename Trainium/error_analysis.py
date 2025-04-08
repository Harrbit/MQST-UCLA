import numpy as np
import matplotlib.pyplot as plt

# Gate factories with parameterization
def gate_factory(name, theta=None):
    if name == "H":
        return lambda dtype: (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=dtype)
    elif name == "X":
        return lambda dtype: np.array([[0, 1], [1, 0]], dtype=dtype)
    elif name == "Y":
        return lambda dtype: np.array([[0, -1j], [1j, 0]], dtype=dtype)
    elif name == "Z":
        return lambda dtype: np.array([[1, 0], [0, -1]], dtype=dtype)
    elif name == "Rx":
        return lambda dtype: np.array([
            [np.cos(theta/2), -1j*np.sin(theta/2)],
            [-1j*np.sin(theta/2), np.cos(theta/2)]
        ], dtype=dtype)
    elif name == "Ry":
        return lambda dtype: np.array([
            [np.cos(theta/2), -np.sin(theta/2)],
            [np.sin(theta/2), np.cos(theta/2)]
        ], dtype=dtype)
    elif name == "Rz":
        return lambda dtype: np.array([
            [np.exp(-1j*theta/2), 0],
            [0, np.exp(1j*theta/2)]
        ], dtype=dtype)

GATE_NAMES = ["H", "X", "Y", "Z", "Rx", "Ry", "Rz"]

def generate_random_circuit(depth):
    circuit = []
    for _ in range(depth):
        name = np.random.choice(GATE_NAMES)
        theta = np.random.uniform(0, 2*np.pi) if name.startswith("R") else None
        circuit.append((name, theta))
    return circuit

def apply_circuit(circuit, precision="float64"):
    if precision == "float64":
        dtype = np.complex128
        state = np.array([1.0 + 0j, 0.0 + 0j], dtype=dtype)
        for name, theta in circuit:
            gate = gate_factory(name, theta)(dtype)
            state = gate @ state
        return state

    elif precision == "float16":
        real = np.array([1.0, 0.0], dtype=np.float16)
        imag = np.array([0.0, 0.0], dtype=np.float16)
        for name, theta in circuit:
            gate = gate_factory(name, theta)(np.complex128)
            real_new = gate.real @ real - gate.imag @ imag
            imag_new = gate.real @ imag + gate.imag @ real
            real, imag = real_new.astype(np.float16), imag_new.astype(np.float16)
        return real.astype(np.float64) + 1j * imag.astype(np.float64)


depths = range(1, 500)
num_trials = 100

mean_fidelity_errors = []
std_fidelity_errors = []
mean_norm_errors = []
std_norm_errors = []

for d in depths:
    fidelity_errors = []
    norm_errors = []

    for _ in range(num_trials):
        circuit = generate_random_circuit(d)

        s_fp64 = apply_circuit(circuit, "float64")
        s_fp16 = apply_circuit(circuit, "float16")

        # Normalize
        s_fp64 /= np.linalg.norm(s_fp64)
        s_fp16 /= np.linalg.norm(s_fp16)

        fidelity = np.abs(np.vdot(s_fp64, s_fp16))**2
        fidelity_errors.append(1 - fidelity)
        norm_errors.append(np.linalg.norm(s_fp64 - s_fp16))  # direct L2 distance between final states


    mean_fidelity_errors.append(np.mean(fidelity_errors))
    std_fidelity_errors.append(np.std(fidelity_errors) / np.sqrt(num_trials))  # SEM

    mean_norm_errors.append(np.mean(norm_errors))
    std_norm_errors.append(np.std(norm_errors) / np.sqrt(num_trials))  # SEM

# Plot with error bars (95% confidence interval)
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.errorbar(depths, mean_norm_errors, yerr=1.96*np.array(std_norm_errors), fmt='o-', capsize=3)
plt.xlabel("Circuit Depth")
plt.ylabel("Mean Distance (L2)")
plt.title("L2 Distance Between FP16 and FP64 States")
plt.grid()


plt.subplot(1, 2, 2)
plt.errorbar(depths, mean_fidelity_errors, yerr=1.96*np.array(std_fidelity_errors), fmt='x-', color='orange', capsize=3)
plt.xlabel("Circuit Depth")
plt.ylabel("1 - Fidelity")
plt.title("Mean Fidelity Error (FP16 vs FP64, 95% CI)")
plt.grid()

plt.tight_layout()
plt.show()

