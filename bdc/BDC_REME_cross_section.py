import numpy as np
import matplotlib.pyplot as plt
import reme
from scipy.interpolate import CubicSpline

# wavelength
wavelength = 1.55e-6
reme.set_wavelength(wavelength)
reme.set_max_waveguide_modes(5)

# layer thicknesses
t_substrate = 0.5e-6
t_core = 220e-9
t_clad = 0.5e-6

# widths
WG_width = 0.3e-6
WG_gap = 0.2e-6
Clad_width = 1e-6

# materials
m_si = reme.MaterialSi()
m_sio2 = reme.MaterialSiO2()


def taper_boundaries(w11, w12, w13, w31, w32, w33, l,
                     num):  # 2 additional variables need to be added: the lengths of input/output wgs
    z = np.linspace(0, l, 5)
    y1 = np.array(
        [WG_gap / 2. + WG_width, WG_gap / 2. + w11, WG_gap / 2. + w12, WG_gap / 2. + w13, WG_gap / 2. + WG_width])
    y3 = np.array(
        [-WG_gap / 2. - WG_width, -WG_gap / 2. - w31, -WG_gap / 2. - w32, -WG_gap / 2. - w33, -WG_gap / 2. - WG_width])

    z_new = np.linspace(z.min(), z.max(), num)
    y2 = np.full(num, WG_gap / 2.)
    y4 = np.full(num, -WG_gap / 2.)

    y1_cs = CubicSpline(z, y1, bc_type=((1, 0.0), (1, 0.0)))
    y3_cs = CubicSpline(z, y3, bc_type=((1, 0.0), (1, 0.0)))

    return z_new, y1_cs(z_new), y2, y3_cs(z_new), y4


# Slab layer stacks: all slabs should have the same thickness
s_core = reme.Slab(m_sio2(t_substrate) + m_si(t_core) + m_sio2(t_clad))
s_clad = reme.Slab(m_sio2(t_substrate) + m_sio2(t_core + t_clad))

w1 = Clad_width
w2 = WG_width
w3 = WG_gap
input_length = 5.7749
total_width = Clad_width * 2 + WG_width * 2 + WG_gap

input_rwg = reme.RWG(s_clad(w1) + s_core(w2) + s_clad(w3) + s_core(w2) + s_clad(w1))
input_guide = reme.FMMStraight(input_rwg)
input_guide.set_left_boundary(reme.PEC)
input_guide.set_right_boundary(reme.PEC)
input_guide.find_modes(nmax=m_si.n().real, nmin=m_sio2.n().real, scan_step=0.005)
n_eff_input_even = input_guide.get_mode_effective_index(0)
n_eff_input_odd = input_guide.get_mode_effective_index(1)
beta_input_even = 2 * np.pi * n_eff_input_even / wavelength
beta_input_odd = 2 * np.pi * n_eff_input_odd / wavelength
delta_beta_input_even_odd = beta_input_even - beta_input_odd

input_rwg_1 = reme.RWG(s_clad(w1) + s_core(w2) + s_clad(w1))
input_guide_1 = reme.FMMStraight(input_rwg_1)
input_guide_1.set_left_boundary(reme.PEC)
input_guide_1.set_right_boundary(reme.PEC)
input_guide_1.find_modes(nmax=m_si.n().real, nmin=m_sio2.n().real, scan_step=0.005)
n_eff_input_1 = input_guide_1.get_mode_effective_index(0)
beta_input_1 = 2 * np.pi * n_eff_input_1 / wavelength

kappa_input = delta_beta_input_even_odd / 2.
C_mat = np.exp(-1j * beta_input_1 * input_length) * np.matrix(
    [[np.cos(kappa_input * input_length), -1j * np.sin(kappa_input * input_length)],
     [-1j * np.sin(kappa_input * input_length), np.cos(kappa_input * input_length)]])
print 'kappa_input = ', kappa_input
print 'C_mat = ', C_mat

# Taper sections
taper_rwgs = []
taper_guides = []
Propagation_Matrix = []

T_length = 16.8367e-6
num_segments = 3

w11 = 0.2829e-6
w12 = 0.2829e-6
w13 = 0.2829e-6
w31 = 0.4365e-6
w32 = 0.4365e-6
w33 = 0.4365e-6
num = 50
step = T_length / num

z_new, y1, y2, y3, y4 = taper_boundaries(w11, w12, w13, w31, w32, w33, T_length, num)
plt.plot(z_new * 1e6, y1 * 1e6, label='y1')
plt.plot(z_new * 1e6, y2 * 1e6, label='y2')
plt.plot(z_new * 1e6, y3 * 1e6, label='y3')
plt.plot(z_new * 1e6, y4 * 1e6, label='y4')
plt.legend()
plt.show()

for i in range(num):
    w2 = y1[i] - y2[i]
    w4 = y4[i] - y3[i]
    w3 = WG_gap
    w1 = Clad_width + WG_width - w2
    w5 = Clad_width + WG_width - w4

    rwg = reme.RWG(s_clad(w1) + s_core(w2) + s_clad(w3) + s_core(w4) + s_clad(w5))
    taper_rwgs.append(rwg)
    guide = reme.FMMStraight(rwg)
    guide.find_modes(nmax=m_si.n().real, nmin=m_sio2.n().real, scan_step=0.005)
    n_eff_even = guide.get_mode_effective_index(0)
    beta_even = 2 * np.pi * n_eff_even / wavelength
    n_eff_odd = guide.get_mode_effective_index(1)
    beta_odd = 2 * np.pi * n_eff_odd / wavelength
    delta_beta_even_odd = (beta_even - beta_odd) / 2.

    rwg1 = reme.RWG(s_clad(w1) + s_core(w2) + s_clad(w1))
    guide1 = reme.FMMStraight(rwg1)
    guide1.set_left_boundary(reme.PEC)
    guide1.set_right_boundary(reme.PEC)
    guide1.find_modes(nmax=m_si.n().real, nmin=m_sio2.n().real, scan_step=0.005)
    n_eff1 = guide1.get_mode_effective_index(0)
    beta1 = 2 * np.pi * n_eff1 / wavelength

    rwg2 = reme.RWG(s_clad(w1) + s_core(w4) + s_clad(w1))
    guide2 = reme.FMMStraight(rwg2)
    guide2.set_left_boundary(reme.PEC)
    guide2.set_right_boundary(reme.PEC)
    guide2.find_modes(nmax=m_si.n().real, nmin=m_sio2.n().real, scan_step=0.005)
    n_eff2 = guide2.get_mode_effective_index(0)
    beta2 = 2 * np.pi * n_eff2 / wavelength
    delta_beta_1_2 = (beta1 - beta2) / 2.
    kappa_taper2 = delta_beta_even_odd ** 2 - delta_beta_1_2 ** 2
    if kappa_taper2.real > 0:
        kappa_taper = np.lib.scimath.sqrt(kappa_taper2)
        beta_avg = (beta1 + beta2) / 2.
        P_mat = np.exp(-1j * beta_avg * step) * np.matrix([[(np.cos(delta_beta_even_odd * step) - 1j * (
                    delta_beta_1_2 / delta_beta_even_odd) * np.sin(delta_beta_even_odd * step)),
                                                            -1j * kappa_taper / delta_beta_even_odd * np.sin(
                                                                delta_beta_even_odd * step)],
                                                           [-1j * kappa_taper / delta_beta_even_odd * np.sin(
                                                               delta_beta_even_odd * step), (
                                                                        np.cos(delta_beta_even_odd * step) + 1j * (
                                                                            delta_beta_1_2 / delta_beta_even_odd) * np.sin(
                                                                    delta_beta_even_odd * step))]])
        Propagation_Matrix.append(P_mat)
        print 'i =', i
        print 'P_mat =', P_mat

    else:
        P_mat = np.matrix([[np.exp(-1j * beta1 * step), 0],
                           [0, np.exp(-1j * beta2 * step)]])
        Propagation_Matrix.append(P_mat)
        print 'i =', i
        print 'P_mat =', P_mat

Taper_Transfer_Matrix = np.matrix([[1, 0], [0, 1]])

for x in Propagation_Matrix:
    Taper_Transfer_Matrix = x * Taper_Transfer_Matrix

print 'Taper_Transfer_Matrix = ', Taper_Transfer_Matrix
Input = np.matrix([[1], [0]])
Output = C_mat * Taper_Transfer_Matrix * C_mat * Input
print 'output_power = ', Output
