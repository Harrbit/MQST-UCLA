import numpy as np
from scipy.linalg import expm
import matplotlib.pyplot as plt
import os
import csv

# Create output directory
os.makedirs('nmr_simulations', exist_ok=True)

# Fundamental NMR parameters
gamma_H = 267.522e6  # ^1H gyromagnetic ratio (rad/(s·T))
gamma_C = 67.282e6   # ^13C gyromagnetic ratio (rad/(s·T))
B0 = 11.74           # Magnetic field strength (Tesla)

# Derived Larmor frequencies
omega0_H = gamma_H * B0  # ^1H Larmor frequency (rad/s)
omega0_C = gamma_C * B0  # ^13C Larmor frequency (rad/s)

# Chemical shifts (ppm) and conversion to frequencies
delta_H_ppm = 7.3       # Chloroform proton chemical shift
delta_C_ppm = 77.0      # Chloroform carbon chemical shift
delta_H = omega0_H * delta_H_ppm * 1e-6  # Actual frequency offset
delta_C = omega0_C * delta_C_ppm * 1e-6

# Scalar coupling
J = 215.0  # Hz (CHCl3 J-coupling)
T1 = 1.0    # Longitudinal relaxation (s)
T2 = 0.1    # Transverse relaxation (s)

# Pauli matrices
sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
I = np.eye(2, dtype=complex)

# Hamiltonian (lab frame)
H = (
    0.5 * (omega0_H + delta_H) * np.kron(sigma_z, I) + 
    0.5 * (omega0_C + delta_C) * np.kron(I, sigma_z) + 
    (np.pi * J) * np.kron(sigma_z, sigma_z)
)

# Initial density matrix (deviation matrix)
rho_initial = np.diag([5, 3, -3, -5]).astype(complex)

def rotation_matrix(axis, angle):
    """Generate single-qubit rotation matrix."""
    if axis == 'x':
        return np.cos(angle/2)*I - 1j*np.sin(angle/2)*sigma_x
    elif axis == 'y':
        return np.cos(angle/2)*I - 1j*np.sin(angle/2)*sigma_y
    elif axis == 'z':
        return np.cos(angle/2)*I - 1j*np.sin(angle/2)*sigma_z
    raise ValueError("Invalid axis")

def apply_pulse(rho, qubit, axis, angle):
    """Apply pulse to specified qubit."""
    R = rotation_matrix(axis, angle)
    U = np.kron(R, I) if qubit == 0 else np.kron(I, R)
    return U @ rho @ U.conj().T

def simulate_sequence(pulses, seq_idx, T=2e-3, N=4000):
    """Simulate a single pulse sequence with full frequency treatment."""
    rho = rho_initial.copy()
    for pulse in pulses:
        rho = apply_pulse(rho, *pulse)
    
    dt = T/N
    times = np.linspace(0, T, N)
    
    # Quantum observables
    Mx = np.kron(sigma_x, I) + np.kron(I, sigma_x)
    My = np.kron(sigma_y, I) + np.kron(I, sigma_y)
    
    signal = np.zeros(N, dtype=complex)
    rho_ev = rho.copy()
    
    for i in range(N):
        # Time evolution
        U = expm(-1j*H*dt)
        rho_ev = U @ rho_ev @ U.conj().T
        
        # Relaxation effects
        diag = np.diag(rho_ev)
        off_diag = rho_ev - np.diag(diag)
        rho_ev = np.diag(diag * np.exp(-dt/T1)) + off_diag * np.exp(-dt/T2)
        
        # Quadrature detection
        signal[i] = np.trace(Mx @ rho_ev) + 1j*np.trace(My @ rho_ev)
    
    # Add noise and save raw signal
    noise = 0.05*(np.random.normal(0,1,N) + 1j*np.random.normal(0,1,N))
    signal += noise
    
    # Frequency analysis
    spectrum = np.fft.fftshift(np.fft.fft(signal))
    freqs = np.fft.fftshift(np.fft.fftfreq(N, dt))/(2*np.pi)
    
    # Save data
    prefix = f'nmr_simulations/seq_{seq_idx}'
    with open(f'{prefix}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time (s)', 'Real', 'Imag', 'Frequency (Hz)', 'Magnitude'])
        for t, s, f, m in zip(times, signal, freqs, np.abs(spectrum)):
            writer.writerow([t, s.real, s.imag, f, m])
    
    # Plotting
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(times*1e3, signal.real, label='Real')
    plt.plot(times*1e3, signal.imag, label='Imag')
    plt.title(f'FID - Sequence {seq_idx}')
    plt.xlabel('Time (ms)')
    plt.ylabel('Signal')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(freqs/1e6, np.abs(spectrum))
    plt.title(f'Spectrum - Sequence {seq_idx}')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Magnitude')
    plt.xlim([omega0_H/(2*np.pi*1e6)-0.1, omega0_H/(2*np.pi*1e6)+0.1])  # Zoom to proton
    plt.tight_layout()
    plt.savefig(f'{prefix}.png')
    plt.close()
    
    return freqs, np.abs(spectrum)

def simulate_all_sequences(pulse_sequences):
    """Process multiple sequences and combine results."""
    summed_spectrum = None
    all_freqs = []
    
    for idx, seq in enumerate(pulse_sequences):
        freqs, spectrum = simulate_sequence(seq, idx)
        all_freqs.append(freqs)
        
        if summed_spectrum is None:
            summed_spectrum = spectrum
        else:
            summed_spectrum += spectrum
    
    # Plot combined spectrum
    plt.figure()
    plt.plot(all_freqs[0]/1e6, summed_spectrum)
    plt.title('Combined NMR Spectrum')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Magnitude')
    plt.xlim([omega0_H/(2*np.pi*1e6)-0.1, omega0_H/(2*np.pi*1e6)+0.1])
    plt.grid(True)
    plt.savefig('nmr_simulations/combined_spectrum.png')
    plt.show()

# Example pulse sequences
if __name__ == "__main__":
    sequences = [
        [(0, 'x', np.pi/2), (1, 'y', np.pi/2)],  # COSY-like
    ]
    
    simulate_all_sequences(sequences)