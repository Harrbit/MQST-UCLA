import numpy as np



wh = 401.28e6
wc = 100.923e6
beta = 1/(297*1.38064e-23)

E = -(0.5 * 1.0545e-34 * wh) - (0.5 * 1.0545e-34 * wc) + (0.5 * 1.0545e-34* np.pi * 1300)

print(np.exp(-1*beta*E))