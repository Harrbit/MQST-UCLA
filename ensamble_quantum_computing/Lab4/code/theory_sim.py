import numpy as np

# Basic gates
I = np.eye(2)
X = np.array([[0, 1], [1, 0]])
H = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]])

def kron(*args):
    """Kronecker product of multiple matrices"""
    result = np.array([[1]])
    for matrix in args:
        result = np.kron(result, matrix)
    return result

def apply_gate(gate, qubit, num_qubits):
    """Apply a single-qubit gate to a multi-qubit system."""
    ops = []
    for i in range(num_qubits):
        if i == qubit:
            ops.append(gate)
        else:
            ops.append(I)
    return kron(*ops)

def deutsch_jozsa_oracle(case):
    """
    Oracle U_f for 1-bit inputs (2-qubit system)
    case: 'constant_0', 'constant_1', 'balanced_1', 'balanced_2'
    """
    # 2 qubits: qubit 0 (input), qubit 1 (output)
    U_f = np.eye(4)

    if case == 'constant_0':
        # f(x) = 0 → do nothing
        pass
    elif case == 'constant_1':
        # f(x) = 1 → flip output qubit always
        U_f = apply_gate(X, 1, 2)
    elif case == 'balanced_1':
        # f(x) = x → flip output qubit when input is 1
        U_f = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
    elif case == 'balanced_2':
        # f(x) = NOT x → flip output qubit when input is 0
        U_f = np.array([
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    else:
        raise ValueError("Unknown oracle case.")
    
    return U_f

def deutsch_jozsa_2qubit_unitary(oracle_case):
    """Full Deutsch-Jozsa algorithm unitary for 2 qubits"""
    # Initial X gate on the output qubit
    U = apply_gate(X, 1, 2)

    # Hadamard on both qubits
    U = apply_gate(H, 0, 2) @ U
    U = apply_gate(H, 1, 2) @ U

    # Oracle
    U_f = deutsch_jozsa_oracle(oracle_case)
    U = U_f @ U

    # Hadamard on input qubit only (qubit 0)
    U = apply_gate(H, 0, 2) @ U

    return U

# List of all possible oracles for 1 input qubit (2-qubit circuit)
oracle_cases = ['constant_0', 'constant_1', 'balanced_1', 'balanced_2']

# Compute and display unitaries
for case in oracle_cases:
    print(f"\nOracle case: {case}")
    U = deutsch_jozsa_2qubit_unitary(case)
    # print(np.round(U, 2))

thermal = np.array([[5, 0, 0, 0],
           [0, 3, 0, 0],
           [0, 0, -3, 0],
           [0, 0, 0, -5]])

CNOTH = np.array([[1, 0, 0, 0],
      [0, 0, 0, 1],
      [0, 0, 1, 0],
      [0, 1, 0, 0]])

CNOT = np.array([[1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]])
P1 = CNOT@CNOTH
P2 = CNOTH@CNOT

U1 = deutsch_jozsa_2qubit_unitary('constant_1')

output_themal = U1@P1@thermal@P1.conj().T@U1.conj().T
print(output_themal)