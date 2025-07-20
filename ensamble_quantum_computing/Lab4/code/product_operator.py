import numpy as np
from scipy.linalg import expm

def product_operator(target, axis, angle):
    """
    Calculate the product operator on a two-qubit system.
    
    Parameters:
    target(tuple): Tuple containing the indices of target qubits (0, 1, or both). Length must be 1 or 2.
    axis(str): Axis of rotation ('x', 'y', or 'z').
    angle(float): Rotation angle in radians.
    
    Returns:
        (numpy.ndarray): 4x4 matrix representing the product operator.
    """
    # Define Pauli matrices
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    # Map axis string to Pauli matrix
    axis_to_pauli = {
        'x': X, 'y': Y, 'z': Z,
        '-x': -X, '-y': -Y, '-z': -Z
    }
    
    if axis.lower() not in axis_to_pauli:
        raise ValueError("Axis must be one of: 'x', 'y', 'z', '-x', '-y', '-z'")
    
    if not isinstance(target, tuple) or len(target) < 1 or len(target) > 2:
        raise ValueError("Target must be a tuple of length 1 or 2")
    
    for t in target:
        if t not in [0, 1]:
            raise ValueError("Target qubits must be 0 or 1")
    
    pauli = axis_to_pauli[axis.lower()]
    
    # Single qubit operation
    if len(target) == 1:
        q = target[0]
        if q == 0:
            generator = np.kron(pauli, I)
        else:  # q == 1
            generator = np.kron(I, pauli)
    
    # Two-qubit operation
    else:  # len(target) == 2
        if target == (0, 1) or target == (1, 0):
            generator = np.kron(pauli, pauli)
        else:
            raise ValueError("For two-qubit operation, target must be (0,1) or (1,0)")
    # generator = generator
    # Calculate the unitary operation using the matrix exponential
    operator = expm(-1j * angle/2 * generator)
    # operator = np.cos(angle/2) * np.kron(I, I) - 1j*np.sin(angle/2) * (generator)
    
    return operator

def apply_operator_sequence(sequence, initial_state=None, threshold=1e-15):
    """
    Apply a sequence of product operators to a two-qubit system.
    
    Parameters:
        sequence: (list of tuples): List of operations in the form [(target, axis, angle), ...] where target is a tuple of qubit indices, axis is 'x', 'y', or 'z', and angle is the rotation angle in radians.

        initial_state(numpy.ndarray, optional): Initial state vector (4x1) or density matrix (4x4). If None, starts with |00⟩ state.
        threshold(float, optional): Values with absolute magnitude smaller than this threshold will be set to zero. Default is 1e-15.
    Returns:
        final_state(numpy.ndarray): Final state after applying all operations
        filtered_count(int): Number of values that were set to zero
    """
    # Define standard basis states
    ket_00 = np.array([1, 0, 0, 0], dtype=complex)
    
    # Set initial state
    if initial_state is None:
        state = ket_00
    else:
        state = initial_state
        
    # Check if state is a vector or density matrix
    is_density_matrix = False
    # if isinstance(state, np.ndarray):
    if state.shape == (4, 4):
        is_density_matrix = True
    elif state.shape != (4,):
        raise ValueError("Initial state must be a 4x1 vector or 4x4 density matrix")
    
    # Apply each operation in sequence
    unitary_net = np.eye(4, dtype=complex)  # Identity operator
    
    for op in sequence:
        if len(op) != 3:
            raise ValueError("Each operation must be a tuple of (target, axis, angle)")
        
        target, axis, angle = op
        operator = product_operator(target, axis, angle)
        
        # Accumulate the unitary operations
        unitary_net = operator @ unitary_net
    np.set_printoptions(precision=2)
    print(unitary_net)
    # Apply the net unitary to the initial state
    if is_density_matrix:
        print(unitary_net.shape)
        final_state = unitary_net @ state @ unitary_net.conj().T
    else:
        final_state = unitary_net @ state
    
    # Filter small values
    filtered_count = 0
    if is_density_matrix:
        for i in range(4):
            for j in range(4):
                if abs(final_state[i, j]) < threshold:
                    filtered_count += 1
                    final_state[i, j] = 0
    else:
        for i in range(4):
            if abs(final_state[i]) < threshold:
                filtered_count += 1
                final_state[i] = 0
    
    return final_state, filtered_count

