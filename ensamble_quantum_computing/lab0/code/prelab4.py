import numpy as np
import matplotlib.pyplot as plt

gamma_p = 42.6  

B = np.linspace(0, 3, 100)

E_up = -0.5 * gamma_p * B
E_down = +0.5 * gamma_p * B

plt.figure(figsize=(7,5))
plt.plot(B, E_up, label='Spin Up (m = +1/2)')
plt.plot(B, E_down, label='Spin Down (m = -1/2)')

plt.xlabel('Magnetic Field B [T]')
plt.ylabel('Energy [MHz]')
plt.title('Proton Spin Energy Levels vs. Magnetic Field')
plt.legend()
plt.grid(True)

plt.show()
