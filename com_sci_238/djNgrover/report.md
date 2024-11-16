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

the time my setup took to make simulation appears to increase exponentially. For 20 qubits, the simulation time for 1000 sampling is about 64s, for 14 qubits, around 1.4s

the notebook file contains a plot from 2 to 10 only, because all times are averaged by 10 runs, running 20 qubit simulation is too time consuming。

