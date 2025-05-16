# Quantum Circuit Simulation on AWS Trainium

## Overview

This project implements a quantum circuit simulator designed specifically for the AWS Trainium hardware accelerator. It demonstrates efficient matrix operations which form the foundation of quantum circuit simulation.

## AWS Trainium Architecture

* **Hardware Accelerator**: Custom-built by AWS for machine learning workloads
* **Memory Hierarchy**:
  * HBM (High Bandwidth Memory) - Device memory
  * SBUF (State Buffer) - On-chip memory for compute operations
  * PSUM (Partial Sum) - Specialized buffer for matrix operations
* **Programming Interface**: Neuron Kernel Interface (NKI)

## Core Components

### Quantum Circuit Classes

```python
class QuantumGate:
    def __init__(self, num_qubits, target_qubits):
        self.num_qubits = num_qubits
        self.target_qubits = target_qubits
        self.matrix = None
    
    def get_matrix(self):
        return self.matrix
```

```python
class QuantumCircuit:
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.dim = 2**num_qubits
        self.gates = []
        
        # Initialize state vector to |0...0⟩
        self.state = np.zeros(self.dim, dtype=np.complex64)
        self.state[0] = 1.0
    
    def add_gate(self, gate):
        self.gates.append(gate)
```

### Implemented Gates

* **Hadamard Gate**: Creates quantum superposition
* **CNOT Gate**: Entangles qubits

### Matrix Operations on Trainium

The project implements two critical matrix operations:

1. **Matrix-Vector Multiplication**:
   * Core operation for applying gates to the quantum state vector
   * Complexity: O(N²)

2. **Matrix-Matrix Multiplication**:
   * Used for combining quantum gates
   * Complexity: O(N³)

## Memory Flow Pattern

All matrix operations follow the same memory flow:

```
HBM → SBUF → Computation → PSUM → SBUF → HBM
```

## Matrix-Vector Multiplication Implementation

```python
@nki.jit
def manual_test_matrix_vector(size=64):
    TILE_K = 128
    
    # 1. Create tensors in HBM
    matrix_T_hbm = nl.ndarray((TILE_K, size), dtype=nl.bfloat16, buffer=nl.shared_hbm)
    vector_hbm = nl.ndarray((TILE_K, 1), dtype=nl.bfloat16, buffer=nl.shared_hbm)
    result_hbm = nl.ndarray((size, 1), dtype=nl.bfloat16, buffer=nl.shared_hbm)
    
    # 2. Initialize matrices
    # ... initialization code ...
    
    # 3. Create SBUF tensors
    matrix_sbuf = nl.ndarray((TILE_K, size), dtype=nl.bfloat16, buffer=nl.sbuf)
    vector_sbuf = nl.ndarray((TILE_K, 1), dtype=nl.bfloat16, buffer=nl.sbuf)
    
    # 4. Load from HBM to SBUF
    matrix_sbuf[i_mat_p, i_mat_f] = nl.load(
        matrix_T_hbm[i_mat_p, i_mat_f],
        mask=(i_mat_p < size) & (i_mat_f < size)
    )
    
    # 5. Perform computation in PSUM
    result_psum = nl.zeros((size, 1), nl.float32, buffer=nl.psum)
    result_psum[i_res_p, i_res_f] = nl.matmul(
        matrix_sbuf[i_mat_p, i_mat_f],
        vector_sbuf[i_vec_p, i_vec_f],
        transpose_x=True
    )
    
    # 6. Store back to HBM
    result_sbuf = nl.copy(result_psum, dtype=nl.bfloat16)
    nl.store(
        result_hbm[i_res_p, i_res_f],
        value=result_sbuf[i_res_p, i_res_f],
        mask=(i_res_p < size)
    )
    
    return result_hbm
```

## Key Optimizations

1. **Proper Memory Utilization**
   * All operations follow HBM → SBUF → compute → HBM flow
   * Respects Trainium's memory hierarchy

2. **Tile Size Management**
   * Uses hardware partition size limits (128)
   * Applies masks to prevent out-of-bounds access

3. **Computational Efficiency**
   * Direct use of Tensor Engine for matrix multiplication
   * Proper data type utilization (bf16)

## Performance Results

| Operation | Matrix Size | Time (s) | Performance |
|-----------|-------------|----------|------------|
| Matrix-Vector | 64×64 | ~11s | ~0.00 GFLOPS |
| Matrix-Vector | 128×128 | ~11s | ~0.00 GFLOPS |
| Matrix-Matrix | 64×64 | (varies) | (varies) |
| Matrix-Matrix | 128×128 | (varies) | (varies) |

*Note: The timing includes compilation overhead, which dominates for small matrices.*

## GHZ State Creation Example

```python
# Create a 3-qubit GHZ state
circuit = QuantumCircuit(3)
circuit.add_hadamard(0)  # Put qubit 0 in superposition
circuit.add_cnot(0, 1)   # Entangle qubits 0 and 1
circuit.add_cnot(1, 2)   # Entangle qubits 1 and 2

# Expected state: (|000⟩ + |111⟩)/√2
```

## Future Improvements

1. **Performance Optimization**
   * Implement tiling for larger matrices
   * Block computations for better memory efficiency
   * Use batched processing for multiple operations

2. **Additional Quantum Operations**
   * More quantum gates (Pauli-X, Y, Z, etc.)
   * Measurement operators
   * Circuit visualization

3. **Scaling to Larger Systems**
   * Multi-device distribution for large qubit counts
   * Sparse matrix techniques for specific quantum states

## Conclusion

This project demonstrates the feasibility of using AWS Trainium for quantum circuit simulation. While the current implementation serves as a proof of concept, there is significant potential for optimization to fully utilize Trainium's computational power for larger quantum systems.

## References

* AWS Neuron SDK Documentation
* AWS Trainium Architecture Guide
* NKI Programming Model