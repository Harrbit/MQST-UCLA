// Sample quantum circuit
qreg q[3];
h q[0];     // Hadamard on first qubit
cx q[0], q[1];  // CNOT with control on qubit 0, target on qubit 1
cz q[1], q[2];  // CZ with control on qubit 1, target on qubit 2
x q[2];     // X gate on third qubit