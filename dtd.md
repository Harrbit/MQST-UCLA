## COBYLA Algorithm (Pseudocode)

**Input:**  
- Objective function: *f(x)*  
- Constraints: *c₁(x), ..., cₘ(x) ≥ 0*  
- Initial point: *x₀*  
- Initial trust region radius: *ρ₀*

```text
1. Initialize x ← x₀, ρ ← ρ₀
2. While ρ > ρ_min:
    a. Approximate f and c_i with linear models
    b. Solve LP: minimize approx f(x) 
       s.t. approx c_i(x) ≥ 0 and ||x - x_k|| ≤ ρ
    c. Evaluate f(x_trial), c_i(x_trial)
    d. If constraints satisfied and improvement:
         Accept x_trial
       Else:
         Reduce ρ
3. Return best x found
