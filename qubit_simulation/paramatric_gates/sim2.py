import numpy as np
from qutip import basis,qeye,tensor,Qobj,mesolve,destroy

dim=3
ket0,ket1,ket2=basis(dim,0),basis(dim,1),basis(dim,2)
sigma_y=1j*(ket1*ket0.dag()-ket0*ket1.dag())
s_y=1j*(ket2*ket1.dag()-ket1*ket2.dag())
S_y=1j*(ket2*ket0.dag()-ket0*ket2.dag())
I3=qeye(dim)
Id=tensor(I3,I3)
sigma_y_F=tensor(sigma_y,I3)
s_y_F=tensor(s_y,I3)
sigma_y_T=tensor(I3,sigma_y)
s_y_T=tensor(I3,s_y)
S_y_T=tensor(I3,S_y)
PiF0,PiF1,PiF2=[tensor(p,I3) for p in [ket0*ket0.dag(),ket1*ket1.dag(),ket2*ket2.dag()]]
PiT0,PiT1,PiT2=[tensor(I3,p) for p in [ket0*ket0.dag(),ket1*ket1.dag(),ket2*ket2.dag()]]

E_F=[0,5.0,5.0-0.25]
E_T=[0,4.8,4.8-0.24]
gC=0.02
xi_F=0.18
xi_T0=0.18
lambda_F=0.9
phi_F=0.8
lambda_T0=0.9
phi_T0=0.8
v=0.3
phi_p=0.0
phi_amp=0.4
omega_p=0.05

def coeff_lambda_T(t,args):
    return lambda_T0+0.0*np.cos(omega_p*t)
def coeff_phi_T(t,args):
    return phi_T0+0.0*np.cos(omega_p*t)
def xi_T(t):
    return xi_T0
def phi_eff_dot(t):
    return -phi_amp*omega_p*np.sin(omega_p*t)
def g_t(t):
    return gC/(4*np.sqrt(xi_F*xi_T(t)))

H0=E_F[1]*PiF1+E_F[2]*PiF2+E_T[1]*PiT1+E_T[2]*PiT2
H1=lambda_F*sigma_y_F*lambda_T0*sigma_y_T*1.0
H2=np.sqrt(2)*phi_F*s_y_F*lambda_T0*sigma_y_T*1.0
H3=lambda_F*sigma_y_F*np.sqrt(2)*phi_T0*s_y_T*1.0

def H_time(t,args):
    term_couple=g_t(t)*(lambda_F*sigma_y_F*coeff_lambda_T(t,args)*sigma_y_T+np.sqrt(2)*phi_F*s_y_F*coeff_lambda_T(t,args)*sigma_y_T+np.sqrt(2)*lambda_F*sigma_y_F*coeff_phi_T(t,args)*s_y_T)
    term_na=-(phi_eff_dot(t)/(2*np.sqrt(xi_T(t))))*(lambda_T0*sigma_y_T+np.sqrt(2)*phi_T0*s_y_T)
    return H0+term_couple+term_na

H=[H0,[sigma_y_T,lambda t, args: -(phi_eff_dot(t)/(2*np.sqrt(xi_T(t))))*lambda_T0],[s_y_T,lambda t,args:-(phi_eff_dot(t)/(np.sqrt(2)*np.sqrt(xi_T(t))))*phi_T0],[sigma_y_F*sigma_y_T,lambda t,args:g_t(t)*lambda_F*coeff_lambda_T(t,args)],[s_y_F*sigma_y_T,lambda t,args:g_t(t)*np.sqrt(2)*phi_F*coeff_lambda_T(t,args)],[sigma_y_F*s_y_T,lambda t,args:g_t(t)*np.sqrt(2)*lambda_F*coeff_phi_T(t,args)]]

gamma_relax=0.001
gamma_deph=0.0005
C_ops=[]
C_ops.append(np.sqrt(gamma_relax)*tensor(destroy(dim),I3))
C_ops.append(np.sqrt(gamma_relax)*tensor(I3,destroy(dim)))
C_ops.append(np.sqrt(gamma_deph)*(PiF1-PiF0))
C_ops.append(np.sqrt(gamma_deph)*(PiT1-PiT0))

psi0=tensor(ket0,ket0)
tlist=np.linspace(0,400,1001)
result=mesolve(H,psi0,tlist,C_ops,[])
