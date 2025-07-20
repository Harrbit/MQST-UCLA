import numpy as np
from product_operator import apply_operator_sequence

pi = np.pi

'''# sequence = [
# # x(1)
# # ((1,),'x',pi),
# # Ry before
#     # ((1,), '-y', pi/2),
#     # ((0,), 'y', pi/2),
# # H(0)
#     ((0,), 'y', pi/4),
#     ((0,), 'x', pi),
#     ((0,), '-y', pi/4),
# # H(1)
#     ((1,), 'y', pi/4),
#     ((1,), 'x', pi),
#     ((1,), '-y', pi/4),

# ## Oracle
# # x(1)
#     ((1,),'x',pi),
# # CNOT(0,1)
#     ((0,),'x',pi),
#     ((1,), 'y', pi/2),
#     ((0, 1), 'z', pi/2),
#     ((1,), '-x', pi/2),
#     ((0,),'x',pi),
# # CNOT(1,0)
#     # ((1,),'x',pi),
#     # ((0,), 'y', pi/2),
#     # ((0, 1), 'z', pi/2),
#     # ((0,), '-x', pi/2),
#     # ((1,),'x',pi)

# # H(0)
#     ((0,), 'y', pi/4),
#     ((0,), 'x', pi),
#     ((0,), '-y', pi/4),
# # H(1)
#     # ((1,), 'y', pi/4),
#     # ((1,), 'x', pi),
#     # ((1,), '-y', pi/4)
# # Ry after
#     # ((1,), 'y', pi/2),
#     # ((0,), '-y', pi/2)

# ]
# X
# ((0,),'x',pi)

# Hadamard
# ((0,), 'y', pi/4),
# ((0,), 'x', pi),
# ((0,), '-y', pi/4)

# Good CNOT(0,1)
# ((0,),'x',pi),
# ((1,), 'y', pi/2),
# ((0, 1), 'z', pi/2),
# ((1,), '-x', pi/2),
# ((0,),'x',pi)

# Good CNOT(1,0)
# ((1,),'x',pi),
# ((0,), 'y', pi/2),
# ((0, 1), 'z', pi/2),
# ((0,), '-x', pi/2),
# ((1,),'x',pi)

# # good but not practical CNOT
# ((1,), 'y', pi/2),
# ((0, 1), 'z', pi/2),
# ((0,), 'z', pi/2),
# ((1,), '-z', pi/2),
# ((1,), '-y', pi/2)

# good but not practical CZ
# ((0,), 'y', pi/4),
# ((0,), 'x', pi),
# ((0,), '-y', pi/4),

# ((0,), 'y', pi/2),
# ((0, 1), 'z', pi/2),
# ((1,), 'z', pi/2),
# ((0,), '-z', pi/2),
# ((0,), '-y', pi/2),

# ((0,), 'y', pi/4),
# ((0,), 'x', pi),
# ((0,), '-y', pi/4)

# bad CNOT
# ((1,), 'y', pi/2),
# ((0, 1), 'z', pi/2),
# ((0, 1), 'x', pi),
# ((0, 1), 'z', pi/2),
# ((0, 1), 'x', pi),
# ((0,), 'y', pi/2),
# ((0,), 'x', pi/2),
# ((0, 1), '-y', pi/2),
# ((1,), '-x', pi/2)
# '''

init_state = np.array([[5, 0, 0, 0],
                       [0, 3, 0, 0],
                       [0, 0, -3, 0],
                       [0, 0, 0, -5]], dtype=complex)

sequence = [
    # [
    # ((1,), 'y', pi/2),
    # ((0, 1), 'z', pi/4),
    # ((0, 1), 'x', pi),
    # ((0, 1), 'z', pi/4),
    # ((0, 1), 'x', pi),
    # ((0,), 'y', pi/2),
    # ((0,), 'x', pi/2),
    # ((0, 1), '-y', pi/2),
    # ((1,), '-x', pi/2)
    # ]
[
# P1
    # ((0,1),'x',pi),
# P1 end

# D.J.Pulse
#     ((1,), 'x', pi),
# # H(0)
    ((0,), 'y', pi/4),
    ((0,), 'x', pi),
    ((0,), '-y', pi/4),
# # H(1)
#     ((1,), 'y', pi/4),
#     ((1,), 'x', pi),
#     ((1,), '-y', pi/4),

# Oracle
# x(1) **apply this for f2 and f4 **
    # ((1,),'x',pi),
# # CNOT(0,1) **apply this for f3 and f4 **
    ((0,),'x',pi),
    ((1,), 'y', pi/2),
    ((0, 1), 'z', pi/2),
    ((1,), '-x', pi/2),
    ((0,),'x',pi),

# # H(0)
#     ((0,), 'y', pi/4),
#     ((0,), 'x', pi),
#     ((0,), '-y', pi/4)
# # D.J. Pulse end
]
,
[
## P2
# CNOT(0,1)
    ((0,),'x',pi),
    ((1,), 'y', pi/2),
    ((0, 1), 'z', pi/2),
    ((1,), '-x', pi/2),
    ((0,),'x',pi),
# CNOT(1,0)
    ((1,),'x',pi),
    ((0,), 'y', pi/2),
    ((0, 1), 'z', pi/2),
    ((0,), '-x', pi/2),
    ((1,),'x',pi),
# P2 end
    ((0,1),'x',pi),
# # D.J.Pulse
#     ((1,), 'x', pi),
# # H(0)
#     ((0,), 'y', pi/4),
#     ((0,), 'x', pi),
#     ((0,), '-y', pi/4),
# # H(1)
#     ((1,), 'y', pi/4),
#     ((1,), 'x', pi),
#     ((1,), '-y', pi/4),

# Oracle
# x(1)  **apply this for f2 and f4 **
    # ((1,),'x',pi),
# # CNOT(0,1)  **apply this for f3 and f4 **
    ((0,),'x',pi),
    ((1,), 'y', pi/2),
    ((0, 1), 'z', pi/2),
    ((1,), '-x', pi/2),
    ((0,),'x',pi),

# # H(0)
#     ((0,), 'y', pi/4),
#     ((0,), 'x', pi),
#     ((0,), '-y', pi/4)
# # D.J. Pulse end
]
,
[
# P3
# CNOT(1,0)
    ((1,),'x',pi),
    ((0,), 'y', pi/2),
    ((0, 1), 'z', pi/2),
    ((0,), '-x', pi/2),
    ((1,),'x',pi),
# CNOT(0,1)
    ((0,),'x',pi),
    ((1,), 'y', pi/2),
    ((0, 1), 'z', pi/2),
    ((1,), '-x', pi/2),
    ((0,),'x',pi),
# P3 end
    ((0,1),'x',pi),

# # D.J.Pulse
#     ((1,), 'x', pi),
# # H(0)
#     ((0,), 'y', pi/4),
#     ((0,), 'x', pi),
#     ((0,), '-y', pi/4),
# # H(1)
#     ((1,), 'y', pi/4),
#     ((1,), 'x', pi),
#     ((1,), '-y', pi/4),

# # Oracle
# # # x(1)  **apply this for f2 and f4 **
#     ((1,),'x',pi),
# # # CNOT(0,1)  **apply this for f3 and f4 **
    ((0,),'x',pi),
    ((1,), 'y', pi/2),
    ((0, 1), 'z', pi/2),
    ((1,), '-x', pi/2),
    ((0,),'x',pi),

# # H(0)
#     ((0,), 'y', pi/4),
#     ((0,), 'x', pi),
#     ((0,), '-y', pi/4)
# # D.J. Pulse end
]
]

# init_state = np.array([0,1,0,0],dtype=complex)
final_state_sum = np.zeros(4, dtype=complex)
def present_information(input_sequence, init_state):
    final_state, filtered_count = apply_operator_sequence(input_sequence, initial_state=init_state)
    # final_state = np.outer(final_state, np.conj(final_state.T))
    return final_state, filtered_count
for s in sequence:
    final_state, filtered_count = present_information(s, init_state)
    final_state_sum = final_state + final_state_sum
print("Final state matrix:")
print(final_state_sum/15)
print(f"\nNumber of values filtered (< 1e-15): {filtered_count}")
