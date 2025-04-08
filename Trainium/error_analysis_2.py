import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import itertools

# Gate factories
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

def generate_random_circuit(qubits, depth):
    circuit = []
    for _ in range(depth):
        layer = []
        for _ in range(qubits):
            name = np.random.choice(GATE_NAMES)
            theta = np.random.uniform(0, 2*np.pi) if name.startswith("R") else None
            layer.append((name, theta))
        circuit.append(layer)
    return circuit

def kron_gates(gates):
    result = gates[0]
    for g in gates[1:]:
        result = np.kron(result, g)
    return result

def apply_circuit(circuit, precision="float64"):
    n = len(circuit[0])  # number of qubits
    dim = 2 ** n
    if precision == "float64":
        dtype = np.complex128
        state = np.zeros(dim, dtype=dtype)
        state[0] = 1.0
        for layer in circuit:
            gates = [gate_factory(name, theta)(dtype) for name, theta in layer]
            full_gate = kron_gates(gates)
            state = full_gate @ state
        return state

    elif precision == "float16":
        # simulate real/imag parts in float16
        real = np.zeros(dim, dtype=np.float16)
        imag = np.zeros(dim, dtype=np.float16)
        real[0] = 1.0
        for layer in circuit:
            gates = [gate_factory(name, theta)(np.complex128) for name, theta in layer]
            full_gate = kron_gates(gates)
            real_new = full_gate.real @ real - full_gate.imag @ imag
            imag_new = full_gate.real @ imag + full_gate.imag @ real
            real, imag = real_new.astype(np.float16), imag_new.astype(np.float16)
        return real.astype(np.float64) + 1j * imag.astype(np.float64)

# Experiment settings
qubit_counts = range(1, 12)
depth = 10
num_trials = 100

mean_fidelity_errors = []
std_fidelity_errors = []
mean_distance_errors = []
std_distance_errors = []

for q in tqdm(qubit_counts, desc="Simulating qubit counts"):
    fidelity_errors = []
    distance_errors = []

    for _ in tqdm(range(num_trials), desc=f"Qubits: {q}", leave=False):
        circuit = generate_random_circuit(q, depth)
        s_fp64 = apply_circuit(circuit, "float64")
        s_fp16 = apply_circuit(circuit, "float16")

        # Normalize
        s_fp64 /= np.linalg.norm(s_fp64)
        s_fp16 /= np.linalg.norm(s_fp16)

        fidelity = np.abs(np.vdot(s_fp64, s_fp16))**2
        fidelity_errors.append(1 - fidelity)

        distance = np.linalg.norm(s_fp64 - s_fp16)
        distance_errors.append(distance)

    mean_fidelity_errors.append(np.mean(fidelity_errors))
    std_fidelity_errors.append(np.std(fidelity_errors) / np.sqrt(num_trials))

    mean_distance_errors.append(np.mean(distance_errors))
    std_distance_errors.append(np.std(distance_errors) / np.sqrt(num_trials))

# Plotting
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.errorbar(qubit_counts, mean_distance_errors, yerr=1.96*np.array(std_distance_errors),
             fmt='o-', capsize=3)
plt.xlabel("Number of Qubits")
plt.ylabel("Mean L2 Distance")
plt.title("FP16 vs FP64: State Distance by Qubit Count")
plt.grid()

plt.subplot(1, 2, 2)
plt.errorbar(qubit_counts, mean_fidelity_errors, yerr=1.96*np.array(std_fidelity_errors),
             fmt='x-', capsize=3, color='orange')
plt.xlabel("Number of Qubits")
plt.ylabel("1 - Fidelity")
plt.title("FP16 vs FP64: Fidelity Error by Qubit Count")
plt.grid()

plt.tight_layout()
plt.show()
