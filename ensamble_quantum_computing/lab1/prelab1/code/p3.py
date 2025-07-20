import numpy as np
import matplotlib.pyplot as plt
from qutip import *

sx, sy, sz = sigmax(), sigmay(), sigmaz()
I = qeye(2)
rho0 = 0.5 * (I + sz)
# b = Bloch()
# b.add_states(rho0)
# b.show()

omega0 = 15.0
omega1 = 15.0
hbar   = 1.0

tmax = 3.15
nt = 500
times = np.linspace(0, tmax, nt)

def H1_coeff(t, args):
    return 0.5 * np.cos(omega1 * t)

def H1_coeffy(t, args):
    return 0.5 * np.sin(omega1 * t)

H0 = 0.5 * (omega0) * sz
H  = [H0, [sx, H1_coeff], [sy, H1_coeffy]]
# H  = [H0, [sx, H1_coeff]]

result = mesolve(H, rho0, times, c_ops=[], e_ops=[sx, sy, sx + 1j*sy, sz])

sx_vals = result.expect[0]
sy_vals = result.expect[1]
sp_vals = result.expect[2]
sz_vals = result.expect[3]


plt.figure()
# plt.plot(times, sx_vals, label="<sigma_x>")
# plt.plot(times, sy_vals, label="<sigma_y>")
plt.plot(times, sp_vals.real, label="Re<sigma_+>")
plt.plot(times, sp_vals.imag, label="Im<sigma_+>")
plt.legend()
plt.show()
plt.ion()
b = Bloch()

for i in range(nt):
    b.clear()
    b.add_vectors([sx_vals[i], sy_vals[i], sz_vals[i]])
    plt.draw()
    # plt.pause(0.005)
    plt.pause(0.005)
    b.add_points([sx_vals[:i+1], sy_vals[:i+1], sz_vals[:i+1]], meth='l')
    b.make_sphere()
    # plt.pause(0.005)
plt.pause(100)
b.save('/Users/runzhaoguo/Documents/MQST-UCLA/411/lab1/prelab1/code/bloch_sphere.png')