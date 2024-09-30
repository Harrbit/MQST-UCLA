import numpy as np

def Gaussian_Beams(R, WaveLength, waist):
    """Gaussian Beam discribed by 1/q, returns 1/q"""
    return 1/R - 1j*WaveLength/(np.pi*waist**2)

def Transformation(q_r, TransformMatrix):
    """How the reciprocal of q evolve along the way, returns 1/q' """
    return (TransformMatrix[1,0]+TransformMatrix[1,1]*q_r)/(TransformMatrix[0,0]+TransformMatrix[0,1]*q_r)

def Radius(q_r):
    """Calculate curvature radius, returns curvature radius"""
    return 1 / np.real(q_r)

def Waist(q_r, WaveLength):
    """Calculate waist, returns waist"""
    return np.sqrt(-1*WaveLength/(np.imag(q_r)*np.pi))

# set parameters
R_in = np.inf
waist_in = 1e-3
WaveLength = 633e-9
f_e = 1
f_o = 1
TransformMatrix = np.array([[-1*f_e/f_o, f_e + f_o],
                           [     0,    -1*f_o/f_e]])

# calculate initial q in reciprocal
q_r_in = Gaussian_Beams(R_in, WaveLength, waist_in)

# How the reciprocal of q evolve along the way
q_r_out = Transformation(q_r_in, TransformMatrix)

# result radius
R_out = Radius(q_r_out)

# result waist
waist_out = Waist(q_r_out, WaveLength)

print(" the curvature radius:", R_out,"m\n", "the waist:" , waist_out, "m")

