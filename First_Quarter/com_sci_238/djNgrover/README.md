# Instructions

## Deutsch-Jozsa:

use this function:

Apply_DJ(num_qubit, function_type, backend, Nshot):

    """
    Automatically generates a quantum circuit to solve the Deutsch-Jozsa problem for 
    a given function type. The circuit incorporates the oracle and implements the 
    Deutsch-Jozsa algorithm

    Parameters:
        num_qubit (int): The total number of qubits in the circuit. Note that the oracle 
        utilizes one less qubit than the entire circuit
        function_type(str): The type of the function to analyze—either 'constant' or 'balanced'  
        backend: The quantum backend on which the circuit will be executed
        Nshot(int): The number of times the quantum circuit is executed

    Returns:
        qc(QuantumCircuit): The generated quantum circuit that implements the Deutsch-Jozsa algorithm.  
        counts(dict): The measurement results from executing the circuit.
    """

## Grover:

use this function to generate circuit:

create_grovers_circuit(n_qubits, marked_states, num_iterations=None):

    """
    Creates a complete Grover's algorithm circuit
    
    Parameters:
        n_qubits (int): Number of qubits in the search space
        marked_states (list): List of binary strings representing marked states
        num_iterations (int): Optional number of Grover iterations

    Returns:
        qc:The circuit
    
    """

use this function to analys result:

analyze_results(counts, marked_states, shots):

    """
    Analyzes the results of Grover's algorithm, printed in terminal
    
    Parameters:
        counts: counts for each measure
        marked_states: marked states
        shots: shots

    Returns:
        None
    """
