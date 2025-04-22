# Comprehensive Guide: Modeling and Simulating a Three‑Qubit Cross‑Resonance (CR) System

> Primary reference: M. Malekakhlagh *et al.*, "First‑principles Analysis of Cross‑Resonance Gate Operation," Phys. Rev. A 102, 042605 (2020)  (see Eq. 18).
> Spectator‑qubit extension: Section VI, Fig. 10/11, Eq. 41.
> Open‑system SWPT: Appendix C, Eqs. C13–C14.

---

## 1. Physical Layout

| Qubit | Role | Control Lines | Static Couplings |
|-------|------|---------------|------------------|
| Q0 | Control | CR drive at omega_d ~ omega_1 | Z exchange J_ct, J_cs |
| Q1 | Target  | none | Z exchange J_ct, J_ts |
| Q2 | Spectator | none | Z exchange J_cs, J_ts |

All three qubits are fixed‑frequency transmons. The CR tone is applied only to Q0 at the dressed target frequency omega_1.

---

## 2. Hamiltonian Construction

### 2.1 Bare Qubits

Each transmon is truncated to its two lowest levels. Higher states enter through renormalized matrix elements nu_mn (Table I of the paper).

### 2.2 Lab‑Frame Hamiltonian

```
H_lab = Sum_j (omega_j / 2) * Z_j
      + J      * Z_0 Z_1
      + J_cs   * Z_0 Z_2
      + J_ts   * Z_1 Z_2
      + (Omega / 2) * (Z_0 X_1) * sin(omega_d t)
```

### 2.3 Effective Frame (block‑diagonal)

After the Schrieffer‑Wolff expansion up to fourth order (Section III), the qubit pair is described by

```
H_eff = (w_ix/2) I X + (w_iz/2) I Z + (w_zi/2) Z I
       + (w_zx/2) Z X + (w_zz/2) Z Z
```

Spectator terms (Eq. 41) add

```
H_spec = J_cs * Z_0 Z_2 + J_ts * Z_1 Z_2
```

Leading scalings (lowest order)

| Term | Scaling |
|------|---------|
| w_zx | J * Omega / Delta_ct |
| w_iz, w_zi | Omega^2 / Delta, J^2 / Delta |
| w_zz | J^2 / Delta |
| IX error | same order as w_zx |

`Delta` denotes suitable detunings defined in the paper.

---

## 3. Open‑System Model

The Lindbladian is (Appendix C)

```
L rho = -i [H_eff + H_spec, rho]
        + Sum_k (L_k rho L_k^dagger - 0.5 {L_k^dagger L_k, rho})
```

Collapse operators per qubit

* Amplitude damping:  L_T1 = sqrt(1/T1) * sigma_minus
* Pure dephasing:     L_phi = sqrt(1/Tphi) * Z

---

## 4. NumPy Simulation Workflow

1. Choose parameters (omega, anharmonicity, J, Omega, T1, Tphi, spectator detuning).
2. Build the 8x8 matrix `H_tot = H_eff + H_spec`.
3. Assemble collapse list `[L_0_T1, L_0_phi, L_1_T1, ...]`.
4. Form 64x64 Liouvillian `L`.
5. Integrate `d rho / dt = L rho` (matrix exponential or ODE solver).
6. Diagnostics: level populations, expectation values `<Z X>`, `<Z Z>`, process fidelity.

A minimal reference code is given in `noisy_three_qubit_sim.py`.

---

## 5. Detuning Windows and Spectator Collisions

* The control‑target detuning `Delta_ct` is divided into five regions (Table II, Fig. 4). Region III (Delta_ct ~ -0.61 alpha_c) offers the best ZX/ZZ ratio.
* The spectator introduces additional collision lines (Table III). Avoid these by parking the spectator frequency inside the flat zones of Fig. 10.

---

## 6. Echo Pulse for Error Suppression

Sequence: half‑CR, X_pi on control, half‑CR with inverted Omega (paper Eq. 24).

* Cancels IZ, IX, and ZZ to first order.
* Residual IY, IZ, ZX rates are given by Eqs. 28 and 31.

---

## 7. Suggested Simulation Exercises

- Reproduce Fig. 4e: ZZ versus drive strength.
- Sweep spectator frequency and observe collision peaks.
- Compare gate fidelity before and after echo.
- Study infidelity scaling with T1 and Tphi.

---

## 8. Key Points

- Two‑level truncation plus renormalized matrix elements is accurate up to Omega ~ 50 MHz.
- Fourth‑order SWPT is needed to capture IX and ZZ correctly.
- Proper spectator detuning is essential; collisions can double coherent error.
- Echo sequences push CR gate error below 1e-3 in realistic parameters.

