# Deutsch_Jozsa

## how the U_f is designed

A very very simple choice of functions: if constant, output 0 only, if balanced, output the first qubit.

In terms of circuit, the U_f do absolutly nothing for constant and put a cx on the first qubit and the helper qubit

## how this design change number of qubit easily

there's no complex rules in U_f's design, ergo the manipulation of qubit number is suprisingly easy.

## how this design is tested

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

## impact of noise

noise added by applying a noise model onto a aersimulator, noised simulation conducted, result in file Deutsch.ipynb

## time - qubit_number

the time my setup took to make simulation appears to increase exponentially.

| No Noise Constant| No Noise Balanced | Noised Constant | Noised Balanced |
|----------|----------|----------|----------|
| 20 qubits, 51.8s | 20 qubits, 1 min 44.2s | 20 qubits, 54.7s | 18 qubits, 1 min 04s |


# Grover

## how the Z_f is designed:

add x on 0s, then add multi control cz, then undo x

## how this design change number of qubit easily

the design is suitable for all input, therefore no matter what n is, the design works correctly

## how is this design tested

test with this function:

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

## impact of noise

noise added by applying a noise model onto a aersimulator, noised simulation conducted, result in file Grove.ipynb

## time - qubit_number

the time my setup took to make simulation appears to increase exponentially. 

| No Noise | Noised |
|----------|----------|
| 18 qubits, 2 min 37.7s | 9 qubits, 37.4s |