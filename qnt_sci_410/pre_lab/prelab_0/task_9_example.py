import numpy as np

def gaussian_beam_q(waist, R, wavelength):
    """Calculate the complex beam parameter q(z) from waist and curvature."""
    return 1 / (1 / R - 1j * wavelength / (np.pi * waist**2))

def abcd_matrix(A, B, C, D, q_in):
    """Apply the ABCD matrix to the input q parameter."""
    return (A * q_in + B) / (C * q_in + D)

def calculate_waist_curvature(q_out, wavelength):
    """Extract the waist and curvature from the complex beam parameter q."""
    R_out = 1 / np.real(1 / q_out)  # Extract curvature
    waist_out = np.sqrt(-wavelength / (np.pi * np.imag(1 / q_out)))  # Extract waist
    return waist_out, R_out

# Example parameters
wavelength = 633e-9  # Wavelength in meters (red laser, for example)
w_in = 0.01  # Initial beam waist in meters
R_in = np.inf  # Plane wave entering (flat wavefront, curvature = infinity)

# Initial beam parameter
q_in = gaussian_beam_q(w_in, R_in, wavelength)

# ABCD matrix for the telescope (example telescope setup)
A, B, C, D = 1, 50, 0, 1  # Simplified ABCD matrix for propagation and lenses

# Calculate the output beam parameter
q_out = abcd_matrix(A, B, C, D, q_in)

# Calculate output beam waist and curvature
w_out, R_out = calculate_waist_curvature(q_out, wavelength)

print(f"Output Waist: {w_out} meters")
print(f"Output Curvature: {R_out} meters")
