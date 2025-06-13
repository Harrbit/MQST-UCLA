"""
QAOA for MAX2SAT: A Complete Qiskit Implementation
==================================================

This implementation demonstrates how to translate the theoretical QAOA framework
for MAX2SAT into executable quantum circuits using Qiskit. We'll build everything
from scratch to see how each mathematical concept becomes actual quantum gates.

The example problem: Find variable assignments that satisfy the maximum number
of clauses in: (¬x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₃) ∧ (x₂ ∨ x₃)
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator
from qiskit.primitives import Estimator
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis import SuzukiTrotter
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class MAX2SAT_QAOA:
    """
    A complete implementation of QAOA for MAX2SAT problems.
    
    This class encapsulates all the steps: problem encoding, circuit construction,
    parameter optimization, and result analysis. Each method corresponds to a
    specific part of the theoretical framework we discussed.
    """
    
    def __init__(self, clauses, num_variables):
        """
        Initialize the MAX2SAT problem.
        
        Args:
            clauses: List of clauses, where each clause is a tuple of (var1, var2, negation_flags)
                    Example: (1, 2, (True, False)) represents (¬x₁ ∨ x₂)
            num_variables: Number of boolean variables
        """
        self.clauses = clauses
        self.num_variables = num_variables
        self.cost_hamiltonian = None
        self.mixing_hamiltonian = None
        
        # Build the Hamiltonians immediately - this translates our mathematical
        # formulation into the Pauli operator representation that Qiskit uses
        self._build_hamiltonians()
        
    def _build_hamiltonians(self):
        """
        Construct the cost and mixing Hamiltonians.
        
        This is where we implement the mathematical translation from boolean
        clauses to quantum operators. Each clause (¬xᵢ ∨ xⱼ) becomes the
        operator ¼(I - Zᵢ)(I + Zⱼ) that we derived in the theory section.
        """
        print("Building Hamiltonians from boolean clauses...")
        
        # The cost Hamiltonian will accumulate terms from each clause
        cost_terms = []
        
        for i, (var1, var2, (neg1, neg2)) in enumerate(self.clauses):
            print(f"Processing clause {i+1}: {'¬' if neg1 else ''}x{var1} ∨ {'¬' if neg2 else ''}x{var2}")
            
            # Convert to 0-based indexing for Qiskit
            qubit1, qubit2 = var1 - 1, var2 - 1
            
            # Build the Pauli string for this clause
            # We need to construct ¼(I - Z₁)(I + Z₂) for clause (¬x₁ ∨ x₂)
            # Expanding: ¼(I + Z₂ - Z₁ - Z₁Z₂)
            
            pauli_string = ['I'] * self.num_variables
            
            # The constant term ¼ contributes to the energy offset
            cost_terms.append(('I' * self.num_variables, 0.25))
            
            # Single Z terms: +¼Z₂ for positive literal, -¼Z₁ for negative literal
            if not neg1:  # x₁ appears positively in clause
                pauli_string[qubit1] = 'Z'
                cost_terms.append((''.join(pauli_string), 0.25))
                pauli_string[qubit1] = 'I'  # Reset for next term
            else:  # ¬x₁ appears (negative literal)
                pauli_string[qubit1] = 'Z'
                cost_terms.append((''.join(pauli_string), -0.25))
                pauli_string[qubit1] = 'I'
                
            if not neg2:  # x₂ appears positively
                pauli_string[qubit2] = 'Z'
                cost_terms.append((''.join(pauli_string), 0.25))
                pauli_string[qubit2] = 'I'
            else:  # ¬x₂ appears (negative literal)
                pauli_string[qubit2] = 'Z'
                cost_terms.append((''.join(pauli_string), -0.25))
                pauli_string[qubit2] = 'I'
            
            # Two-qubit ZZ term: this captures the interaction between variables
            pauli_string[qubit1] = 'Z'
            pauli_string[qubit2] = 'Z'
            zz_coeff = 0.25 if (neg1 == neg2) else -0.25
            cost_terms.append((''.join(pauli_string), zz_coeff))
        
        # Convert to Qiskit's SparsePauliOp format
        self.cost_hamiltonian = SparsePauliOp.from_list(cost_terms)
        
        # The mixing Hamiltonian is simpler: Σᵢ Xᵢ (sum of X operators)
        # This enables transitions between computational basis states
        mixing_terms = []
        for i in range(self.num_variables):
            pauli_string = ['I'] * self.num_variables
            pauli_string[i] = 'X'
            mixing_terms.append((''.join(pauli_string), 1.0))
        
        self.mixing_hamiltonian = SparsePauliOp.from_list(mixing_terms)
        
        print(f"Cost Hamiltonian constructed with {len(cost_terms)} terms")
        print(f"Mixing Hamiltonian: {self.mixing_hamiltonian}")
    
    def build_qaoa_circuit(self, gamma_params, beta_params):
        """
        Construct the QAOA circuit for given parameters.
        
        This implements the alternating sequence of cost and mixing unitaries:
        UM(βp)UC(γp)...UM(β1)UC(γ1)|+⟩^n
        
        We use PauliEvolutionGate for robust Hamiltonian time evolution
        that works across different Qiskit versions.
        
        Args:
            gamma_params: Parameters for cost unitaries [γ₁, γ₂, ..., γₚ]
            beta_params: Parameters for mixing unitaries [β₁, β₂, ..., βₚ]
        """
        p = len(gamma_params)  # Number of QAOA layers
        qc = QuantumCircuit(self.num_variables)
        
        # Initialize in uniform superposition |+⟩^n using Hadamard gates
        # This gives equal amplitude to all computational basis states
        qc.h(range(self.num_variables))
        qc.barrier()  # Visual separator in circuit diagrams
        
        # Apply p alternating layers of cost and mixing unitaries
        for layer in range(p):
            # Cost unitary UC(γ) = exp(-iγHC)
            # Use PauliEvolutionGate for robust implementation across Qiskit versions
            cost_gate = PauliEvolutionGate(self.cost_hamiltonian, time=gamma_params[layer])
            qc.append(cost_gate, range(self.num_variables))
            qc.barrier()
            
            # Mixing unitary UM(β) = exp(-iβHM) 
            # Since HM = ΣXᵢ, this becomes individual RX rotations
            mixing_gate = PauliEvolutionGate(self.mixing_hamiltonian, time=beta_params[layer])
            qc.append(mixing_gate, range(self.num_variables))
            qc.barrier()
        
        return qc
    
    def evaluate_circuit(self, gamma_params, beta_params, shots=1024):
        """
        Evaluate the expectation value ⟨ψ(γ,β)|HC|ψ(γ,β)⟩.
        
        This is the objective function we're trying to maximize in QAOA.
        Higher values mean our quantum state has higher overlap with
        good solutions to the MAX2SAT problem.
        """
        qc = self.build_qaoa_circuit(gamma_params, beta_params)
        
        # Use Qiskit's Estimator primitive for expectation value calculation
        # This handles the sampling and statistical estimation automatically
        estimator = Estimator()
        job = estimator.run(qc, self.cost_hamiltonian, shots=shots)
        expectation_value = job.result().values[0]
        
        return expectation_value
    
    def optimize_parameters(self, p=1, max_iterations=100):
        """
        Find optimal QAOA parameters using classical optimization.
        
        This is the "hybrid" part of the quantum-classical algorithm.
        We use scipy's minimize function to find the best γ and β values.
        
        Args:
            p: Number of QAOA layers (circuit depth)
            max_iterations: Maximum optimization iterations
        """
        print(f"\nOptimizing QAOA parameters for p={p} layers...")
        
        # Objective function for classical optimizer (note the negative sign)
        # We minimize the negative expectation value to maximize the original
        def objective(params):
            gamma_params = params[:p]
            beta_params = params[p:]
            return -self.evaluate_circuit(gamma_params, beta_params)
        
        # Random initialization of parameters
        # This choice can affect convergence, so in practice you might
        # want to try multiple random starting points
        initial_params = np.random.uniform(0, 2*np.pi, 2*p)
        
        # Format arrays properly for printing
        gamma_init = initial_params[:p]
        beta_init = initial_params[p:]
        print(f"Initial parameters: γ={[f'{x:.3f}' for x in gamma_init]}, β={[f'{x:.3f}' for x in beta_init]}")
        
        # Classical optimization using COBYLA (derivative-free method)
        # Good choice for noisy quantum objective functions
        result = minimize(objective, initial_params, method='COBYLA', 
                         options={'maxiter': max_iterations})
        
        optimal_gamma = result.x[:p]
        optimal_beta = result.x[p:]
        optimal_value = -result.fun  # Convert back to maximization
        
        print(f"Optimization converged: {result.success}")
        print(f"Optimal parameters: γ={[f'{x:.3f}' for x in optimal_gamma]}, β={[f'{x:.3f}' for x in optimal_beta]}")
        print(f"Optimal expectation value: {optimal_value:.4f}")
        
        return optimal_gamma, optimal_beta, optimal_value
    
    def sample_solutions(self, gamma_params, beta_params, shots=1024):
        """
        Sample measurement outcomes from the optimized QAOA circuit.
        
        This gives us the probability distribution over computational basis
        states, which correspond to candidate solutions for our MAX2SAT problem.
        """
        qc = self.build_qaoa_circuit(gamma_params, beta_params)
        
        # Add measurement operations
        qc.measure_all()
        
        # Execute on simulator
        simulator = AerSimulator()
        compiled_circuit = transpile(qc, simulator)
        job = simulator.run(compiled_circuit, shots=shots)
        counts = job.result().get_counts()
        
        return counts
    
    def evaluate_classical_solution(self, bitstring):
        """
        Evaluate how many clauses a classical assignment satisfies.
        
        This lets us check the quality of solutions found by QAOA.
        
        Args:
            bitstring: String like '101' representing variable assignment
        """
        # Convert bitstring to variable assignment (Qiskit uses reversed order)
        assignment = [int(bit) for bit in reversed(bitstring)]
        
        satisfied_clauses = 0
        for var1, var2, (neg1, neg2) in self.clauses:
            # Evaluate the clause with current assignment
            val1 = assignment[var1-1] if not neg1 else 1 - assignment[var1-1]
            val2 = assignment[var2-1] if not neg2 else 1 - assignment[var2-1]
            
            # Clause is satisfied if at least one literal is true
            if val1 or val2:
                satisfied_clauses += 1
                
        return satisfied_clauses
    
    def analyze_results(self, counts):
        """
        Analyze the measurement results to find the best solutions.
        
        This connects our quantum results back to the original boolean
        satisfiability problem.
        """
        print("\nAnalyzing QAOA results...")
        print("Top measurement outcomes:")
        
        # Sort by probability (count frequency)
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        max_satisfied = 0
        best_solutions = []
        
        for bitstring, count in sorted_counts[:10]:  # Show top 10
            probability = count / sum(counts.values())
            satisfied = self.evaluate_classical_solution(bitstring)
            
            print(f"  {bitstring}: {probability:.3f} probability, "
                  f"satisfies {satisfied}/{len(self.clauses)} clauses")
            
            if satisfied > max_satisfied:
                max_satisfied = satisfied
                best_solutions = [bitstring]
            elif satisfied == max_satisfied:
                best_solutions.append(bitstring)
        
        print(f"\nBest classical solutions found:")
        print(f"Maximum clauses satisfied: {max_satisfied}/{len(self.clauses)}")
        for solution in best_solutions:
            assignment = [int(bit) for bit in reversed(solution)]
            print(f"  Assignment: {assignment} (bitstring: {solution})")
        
        return max_satisfied, best_solutions

def main():
    """
    Demonstrate QAOA on a concrete MAX2SAT example.
    
    We'll use the same example from our theoretical section:
    C₁ = (¬x₁ ∨ x₂), C₂ = (x₁ ∨ ¬x₃), C₃ = (x₂ ∨ x₃)
    """
    print("QAOA for MAX2SAT: Proof of Principle Implementation")
    print("=" * 55)
    
    # Define our MAX2SAT instance
    # Each tuple: (var1, var2, (is_var1_negated, is_var2_negated))
    clauses = [
        (1, 2, (True, False)),   # (¬x₁ ∨ x₂)
        (1, 3, (False, True)),   # (x₁ ∨ ¬x₃)  
        (2, 3, (False, False))   # (x₂ ∨ x₃)
    ]
    
    num_variables = 3
    
    print(f"Problem: 3 variables, {len(clauses)} clauses")
    for i, (var1, var2, (neg1, neg2)) in enumerate(clauses):
        clause_str = f"({'¬' if neg1 else ''}x{var1} ∨ {'¬' if neg2 else ''}x{var2})"
        print(f"  C{i+1}: {clause_str}")
    
    # Initialize QAOA solver
    qaoa = MAX2SAT_QAOA(clauses, num_variables)
    
    # Find classical optimal solution for comparison
    print("\nFinding classical optimal solution...")
    best_classical = 0
    optimal_assignments = []
    
    # Brute force search over all 2³ = 8 possible assignments
    for assignment in range(2**num_variables):
        bitstring = format(assignment, f'0{num_variables}b')
        satisfied = qaoa.evaluate_classical_solution(bitstring)
        if satisfied > best_classical:
            best_classical = satisfied
            optimal_assignments = [bitstring]
        elif satisfied == best_classical:
            optimal_assignments.append(bitstring)
    
    print(f"Classical optimum: {best_classical}/{len(clauses)} clauses")
    print(f"Optimal assignments: {optimal_assignments}")
    
    # Run QAOA optimization
    print("\n" + "="*50)
    print("RUNNING QAOA OPTIMIZATION")
    print("="*50)
    
    # Try different circuit depths to see the effect
    for p in [1, 2]:
        print(f"\n--- QAOA with p={p} layers ---")
        
        optimal_gamma, optimal_beta, optimal_value = qaoa.optimize_parameters(p=p)
        
        # Sample solutions with optimized parameters
        print(f"\nSampling solutions with optimized parameters...")
        counts = qaoa.sample_solutions(optimal_gamma, optimal_beta, shots=2048)
        
        # Analyze the results
        max_satisfied, best_solutions = qaoa.analyze_results(counts)
        
        # Compare with classical optimum
        success_ratio = max_satisfied / best_classical
        print(f"\nQAOA Performance:")
        print(f"  Found solutions satisfying {max_satisfied}/{len(clauses)} clauses")
        print(f"  Success ratio: {success_ratio:.1%}")
        
        if max_satisfied == best_classical:
            print("  ✓ QAOA found optimal solution!")
        else:
            print(f"  ⚠ QAOA missed optimum by {best_classical - max_satisfied} clauses")
    
    # Demonstrate circuit structure for publication
    print(f"\n" + "="*50)
    print("PUBLICATION-READY CIRCUIT ANALYSIS")
    print("="*50)
    
    # Build a sample circuit to show structure
    # Use specific parameter values that demonstrate the algorithm clearly
    sample_gamma = [np.pi/4]  # Choose meaningful parameter values
    sample_beta = [np.pi/8]
    sample_circuit = qaoa.build_qaoa_circuit(sample_gamma, sample_beta)
    
    print(f"\nQAOA circuit structure (p=1):")
    print(f"  Qubits: {sample_circuit.num_qubits}")
    print(f"  Gates: {sample_circuit.size()}")
    print(f"  Depth: {sample_circuit.depth()}")
    
    # Create publication-ready circuit diagrams
    create_publication_circuit_diagrams(qaoa, sample_gamma, sample_beta)

def create_publication_circuit_diagrams(qaoa, gamma_params, beta_params):
    """
    Generate publication-quality circuit diagrams for academic papers.
    
    This function demonstrates how to create clean, professional-looking
    quantum circuit diagrams suitable for inclusion in research papers.
    The key principles are clarity, consistency, and information density.
    """
    import matplotlib.pyplot as plt
    from qiskit.visualization import circuit_drawer
    
    print(f"\nGenerating publication-ready circuit diagrams...")
    
    # Build the circuit we want to visualize
    circuit = qaoa.build_qaoa_circuit(gamma_params, beta_params)
    
    # Method 1: Text-based diagram (good for code documentation)
    print(f"\n--- Text Circuit Diagram (for code/documentation) ---")
    text_diagram = circuit.draw(output='text', fold=-1)
    print(text_diagram)
    
    # Method 2: Clean matplotlib figure (best for papers)
    print(f"\n--- Generating matplotlib figure for paper inclusion ---")
    
    # Create a figure with specific styling for academic publications
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    # Draw circuit with publication-ready styling
    circuit_img = circuit.draw(
        output='mpl',                    # Use matplotlib backend
        style={'backgroundcolor': 'white',  # Clean white background
               'linecolor': 'black',         # Black lines for clarity
               'textcolor': 'black',         # Black text
               'gatefacecolor': 'lightblue', # Subtle gate coloring
               'barrierfacecolor': 'gray',   # Clear barrier visibility
               'fontsize': 14,               # Readable font size
               'subfontsize': 12},           # Slightly smaller for subscripts
        fold=-1,                         # Don't fold the circuit
        ax=ax,                          # Use our custom axes
        vertical_compression='high'      # Compact vertical spacing
    )
    
    # Customize the plot for publication standards
    ax.set_title(r'1', 
                 fontsize=16, pad=20)
    
    # Remove axes ticks and labels (not needed for circuit diagrams)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Tight layout to minimize white space
    plt.tight_layout()
    
    # Save in multiple formats for different use cases
    plt.savefig('qaoa_circuit_publication.pdf', 
                dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('qaoa_circuit_publication.png', 
                dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"  ✓ Saved high-resolution PDF: qaoa_circuit_publication.pdf")
    print(f"  ✓ Saved high-resolution PNG: qaoa_circuit_publication.png")
    
    plt.show()
    
    # Method 3: Simplified schematic diagram (for conceptual explanation)
    print(f"\n--- Creating conceptual schematic ---")
    
    # Create a simplified version that emphasizes the algorithmic structure
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    
    # Build a minimal circuit showing just the key structure
    conceptual_circuit = QuantumCircuit(3)
    conceptual_circuit.h(range(3))  # Initial state preparation
    conceptual_circuit.barrier()
    
    # Add a single cost layer (we'll represent the complex evolution symbolically)
    conceptual_circuit.rz(gamma_params[0], 0)  # Simplified representation
    conceptual_circuit.rz(gamma_params[0], 1)
    conceptual_circuit.rz(gamma_params[0], 2)
    conceptual_circuit.barrier()
    
    # Add mixing layer
    conceptual_circuit.rx(beta_params[0], 0)
    conceptual_circuit.rx(beta_params[0], 1)
    conceptual_circuit.rx(beta_params[0], 2)
    conceptual_circuit.barrier()
    
    # Measurement
    conceptual_circuit.measure_all()
    
    # Draw with emphasis on the algorithmic flow
    conceptual_circuit.draw(
        output='mpl',
        style={'backgroundcolor': 'white',
               'linecolor': 'black',
               'textcolor': 'black',
               'gatefacecolor': 'lightgreen',  # Different color scheme
               'fontsize': 8},
        fold=-1,
        ax=ax
    )
    
    ax.set_title(r'Circuit Diagram',fontsize=14, pad=20)
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.tight_layout()
    plt.savefig('qaoa_schematic_publication.pdf', 
                dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"  ✓ Saved conceptual schematic: qaoa_schematic_publication.pdf")
    plt.show()
    
    # Method 4: Component breakdown (for detailed technical explanation)
    print(f"\n--- Creating component breakdown diagrams ---")
    
    # Show individual pieces of the algorithm
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))
    
    # Initialization circuit
    init_circuit = QuantumCircuit(3)
    init_circuit.h(range(3))
    init_circuit.draw(output='mpl', ax=axes[0], 
                     style={'backgroundcolor': 'white', 'fontsize': 6})
    axes[0].set_title('(a) Initial State Preparation: $|+\\rangle^{\\otimes 3}$', fontsize=12)
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    
    # Cost evolution (simplified representation)
    cost_circuit = QuantumCircuit(3)
    cost_circuit.rz(gamma_params[0], 0)
    cost_circuit.cx(0, 1)
    cost_circuit.rz(gamma_params[0], 1)
    cost_circuit.cx(0, 1)
    cost_circuit.draw(output='mpl', ax=axes[1], 
                     style={'backgroundcolor': 'white', 'fontsize': 6})
    axes[1].set_title('(b) Cost Evolution: $U_C(\\gamma)$ (simplified)', fontsize=12)
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    
    # Mixing evolution
    mix_circuit = QuantumCircuit(3)
    mix_circuit.rx(beta_params[0], 0)
    mix_circuit.rx(beta_params[0], 1)
    mix_circuit.rx(beta_params[0], 2)
    mix_circuit.draw(output='mpl', ax=axes[2], 
                    style={'backgroundcolor': 'white', 'fontsize': 4})
    axes[2].set_title('(c) Mixing Evolution: $U_M(\\beta)$', fontsize=12)
    axes[2].set_xticks([])
    axes[2].set_yticks([])
    
    plt.tight_layout()
    plt.savefig('qaoa_components_publication.pdf', 
                dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"  ✓ Saved component breakdown: qaoa_components_publication.pdf")
    plt.show()
    
    print(f"\nPublication diagram guidelines:")
    print(f"  • Use PDF format for vector graphics in LaTeX documents")
    print(f"  • PNG format provides good quality for presentations")
    print(f"  • Choose diagram complexity based on paper's focus")
    print(f"  • Include parameter values in captions when relevant")
    print(f"  • Consider colorblind-friendly color schemes")
    print(f"  • Ensure text is readable at publication scale")

if __name__ == "__main__":
    main()