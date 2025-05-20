# import numpy as np
# from scipy import integrate
# import matplotlib.pyplot as plt

# # Constants
# a_0 = 5.291772108e-11  # Bohr radius in meters
# ep_0 = 8.854187817e-12 # Vacuum permittivity in F/m
# e = 1.602176634e-19    # Elementary charge in coulombs
# eV_to_J = e            # Conversion factor from eV to joules
# J_to_eV = 1/e          # Conversion factor from joules to eV

# def R_1s(r):
#     Z = 2
#     return 2 * np.sqrt(Z**3/a_0**3) * np.exp(-1*Z*r/a_0)

# def R_3p(r):
#     Z = 1
#     return 2/81 * np.sqrt(2*Z**7/(3*a_0**7)) * r * (r - 6 * a_0/Z) * np.exp(-1*Z*r/(3*a_0))

# def Y00():
#     return 1/2 * np.sqrt(1/np.pi)

# def Y10(theta):
#     return 1/2 * np.sqrt(3/np.pi) * np.cos(theta)

# def r12(r1, r2, theta):
#     return np.sqrt(r1**2 + r2**2 - 2 * r1 * r2 * np.cos(theta))

# def integrand(r1, r2, theta):
#     R1s_1 = R_1s(r1)
#     R1s_2 = R_1s(r2)
#     R3p_1 = R_3p(r1)
#     R3p_2 = R_3p(r2)
    
#     denom = r12(r1, r2, theta)
    
#     if denom < 1e-20:
#         denom = 1e-20
        
#     coulomb = e**2 / (4 * np.pi * ep_0 * denom)
#     volume_element = r1**2 * r2**2 * np.sin(theta)

#     return (1 / (4*np.pi*ep_0)) * np.conj(R1s_1*Y00()) * np.conj(R3p_2*Y10(theta)) * coulomb * R3p_1*Y10(theta) * R1s_2*Y00() * volume_element
 
# def calculate_K():
#     r_max = 30 * a_0
    
#     def integrand_wrapper(theta, r2, r1):
#         return integrand(r1, r2, theta)
    
#     result, error = integrate.nquad(
#         integrand_wrapper,
#         [[0, np.pi],          # theta limits
#          [0, r_max],          # r2 limits
#          [0, r_max]]          # r1 limits
#     )
    
#     return result, error

# try:
#     print("Calculating using quadrature integration...")
#     K_quad, err_quad = calculate_K()
#     Delta_E_quad = 2 * K_quad
#     Delta_E_quad_eV = Delta_E_quad * J_to_eV
#     err_quad_eV = 2 * err_quad * J_to_eV
#     print(f"K = {K_quad:.6e} J")
#     print(f"Delta_E = 2*K = {Delta_E_quad:.6e} J = {Delta_E_quad_eV:.6f} eV ± {err_quad_eV:.6f} eV")
# except Exception as e:
#     print(f"Quadrature integration failed: {e}")
# import numpy as np
# from scipy import integrate

# # Constants
# a_0 = 5.291772108e-11  # Bohr radius (m)
# ep_0 = 8.854187817e-12  # Vacuum permittivity (F/m)
# e = 1.602176634e-19  # Elementary charge (C)
# J_to_eV = 1 / e

# # Hydrogen-like radial functions
# def R_1s(r, Z=2):
#     return 2 * np.sqrt(Z**3 / a_0**3) * np.exp(-Z * r / a_0)

# def R_3p(r, Z=1):
#     rho = Z * r / a_0
#     norm = 1 / (81 * np.sqrt(6)) * np.sqrt(Z**7 / a_0**7)
#     return norm * rho * (6 - rho) * np.exp(-rho / 3)

# # Spherical harmonics for m=0
# def Y00():
#     return 1 / np.sqrt(4 * np.pi)

# def Y10(theta):
#     return np.sqrt(3 / (4 * np.pi)) * np.cos(theta)

# # Distance r12 between r1 and r2
# def r12(r1, r2, theta1, phi1, theta2, phi2):
#     cos_gamma = (
#         np.sin(theta1) * np.sin(theta2) * np.cos(phi1 - phi2) +
#         np.cos(theta1) * np.cos(theta2)
#     )
#     return np.sqrt(r1**2 + r2**2 - 2 * r1 * r2 * cos_gamma)

# # Full 6D integrand
# def integrand(phi1, phi2, theta1, theta2, r1, r2):
#     R1s_r1 = R_1s(r1)
#     R1s_r2 = R_1s(r2)
#     R3p_r1 = R_3p(r1)
#     R3p_r2 = R_3p(r2)

#     Y00_val = Y00()
#     Y10_1 = Y10(theta1)
#     Y10_2 = Y10(theta2)

#     r12_val = r12(r1, r2, theta1, phi1, theta2, phi2)
#     if r12_val < 1e-10:
#         return 0.0

#     coulomb = e**2 / (4 * np.pi * ep_0 * r12_val)
#     psi_star = R1s_r1 * Y00_val * R3p_r2 * Y10_2
#     psi = R3p_r1 * Y10_1 * R1s_r2 * Y00_val
#     integrand_val = np.real(psi_star * coulomb * psi)

#     # Volume element in spherical coordinates
#     dV = r1**2 * np.sin(theta1) * r2**2 * np.sin(theta2)
#     return integrand_val * dV

# # Perform quadrature integration
# def compute_quadrature():
#     r_max = 30 * a_0
#     bounds = [
#         [0, 2 * np.pi],  # phi1
#         [0, 2 * np.pi],  # phi2
#         [0, np.pi],      # theta1
#         [0, np.pi],      # theta2
#         [0, r_max],      # r1
#         [0, r_max],      # r2
#     ]
#     opts = [{'limit': 200} for _ in range(6)]

#     print("Computing exchange integral using 6D quadrature...")
#     result, error = integrate.nquad(integrand, bounds, opts=opts)
#     return result, error

# # Optional: Monte Carlo estimator
# def monte_carlo_K(N=10**6):
#     r1 = np.random.exponential(scale=2*a_0, size=N)
#     r2 = np.random.exponential(scale=2*a_0, size=N)
#     theta1 = np.arccos(1 - 2*np.random.rand(N))
#     theta2 = np.arccos(1 - 2*np.random.rand(N))
#     phi1 = 2 * np.pi * np.random.rand(N)
#     phi2 = 2 * np.pi * np.random.rand(N)

#     R1s_r1 = R_1s(r1)
#     R1s_r2 = R_1s(r2)
#     R3p_r1 = R_3p(r1)
#     R3p_r2 = R_3p(r2)
#     Y00_val = Y00()
#     Y10_1 = Y10(theta1)
#     Y10_2 = Y10(theta2)

#     r12_val = r12(r1, r2, theta1, phi1, theta2, phi2)
#     r12_val = np.maximum(r12_val, 1e-10)

#     coulomb = e**2 / (4 * np.pi * ep_0 * r12_val)
#     psi_star = R1s_r1 * Y00_val * R3p_r2 * Y10_2
#     psi = R3p_r1 * Y10_1 * R1s_r2 * Y00_val
#     values = np.real(psi_star * coulomb * psi)
#     weights = r1**2 * np.sin(theta1) * r2**2 * np.sin(theta2)

#     estimate = (8 * np.pi**2 * (30*a_0)**2) * np.mean(values * weights)
#     return estimate

# # === Run Both ===
# if __name__ == "__main__":
#     # Method 1: Quadrature
#     try:
#         K, err = compute_quadrature()
#         Delta_E = 2 * K
#         Delta_E_eV = Delta_E * J_to_eV
#         err_eV = 2 * err * J_to_eV
#         print(f"\n[Quadrature]")
#         print(f"K = {K:.6e} J")
#         print(f"ΔE = 2K = {Delta_E:.6e} J = {Delta_E_eV:.6f} eV ± {err_eV:.6f} eV")
#     except Exception as e:
#         print("Quadrature method failed:", e)

#     # Method 2: Monte Carlo (optional)
#     try:
#         print("\nEstimating K with Monte Carlo (1 million samples)...")
#         K_monte = monte_carlo_K(N=10**6)
#         Delta_E_monte = 2 * K_monte
#         Delta_E_monte_eV = Delta_E_monte * J_to_eV
#         print(f"\n[Monte Carlo]")
#         print(f"K ≈ {K_monte:.6e} J")
#         print(f"ΔE = 2K ≈ {Delta_E_monte:.6e} J = {Delta_E_monte_eV:.6f} eV")
#     except Exception as e:
#         print("Monte Carlo method failed:", e)

import numpy as np
from scipy.integrate import nquad

ep_0 = 8.854187817e-12  # Vacuum permittivity in F/m
e = 1.602176634e-19    # Elementary charge in C
a_0 = 5.291772108e-11  # Bohr radius in m

def R_1s(r):
    Z = 2
    return 2 * Z**(3/2) * np.exp(-Z * r/a_0)

def R_3p(r):
    return (1 / (81 * np.sqrt(6))) * r * np.exp(-r / 3) * (1 - r / 6)

def Y10_squared(gamma):
    return (np.sqrt(3 / (4 * np.pi)) * np.cos(gamma))**2

def r12(r1, r2, gamma):
    return np.sqrt(r1**2 + r2**2 - 2 * r1 * r2 * np.cos(gamma))

def integrand(gamma, r2, r1):
    R1s_r1 = R_1s(r1)
    R1s_r2 = R_1s(r2)
    R3p_r1 = R_3p(r1)
    R3p_r2 = R_3p(r2)

    Y_part = Y10_squared(gamma)
    denom = r12(r1, r2, gamma)
    if denom < 1e-20:
        denom = 1e-20

    coulomb = 1 / denom * (e**2 / (4 * np.pi) * ep_0)
    volume_element = r1**2 * r2**2 * np.sin(gamma)

    return R1s_r1 * R3p_r2 * R3p_r1 * R1s_r2 * Y_part * coulomb * volume_element

# Set radial cutoff and integrate
r_max = 10  # atomic units

result, error = nquad(
    integrand,
    ranges=[
        [0, r_max],     # r1
        [0, r_max],     # r2
        [0, np.pi]      # gamma
    ],
    opts=[{"limit": 50}, {"limit": 50}, {"limit": 100}]
)

# Exchange energy K and splitting ΔE
K = result
Delta_E = 2 * K
hartree_to_ev = 27.2114

print(f"Exchange integral K       = {K:.6e} Hartree")
print(f"Singlet-triplet splitting = {Delta_E:.6e} Hartree")
print(f"                         = {Delta_E * hartree_to_ev:.4f} eV")

