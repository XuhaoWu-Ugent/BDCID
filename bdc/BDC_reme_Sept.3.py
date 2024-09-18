import numpy as np
import matplotlib.pyplot as plt
import reme
from scipy.interpolate import CubicSpline

# wavelength
wavelength = 1.55e-6
# If there is further wavelength sweeping, the for-loop should start here by adjusting the wavelengths.
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
b_separation = WG_gap + WG_width

# materials
m_si = reme.MaterialSi()
m_sio2 = reme.MaterialSiO2()
m_air = reme.MaterialAir()


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


# plot the taper shape
# Taper_section
# what we want to optimize: 50/50 and 100/0 coupler.

T_length = 16.8367e-6
num_segments = 3

w11 = 0.2829e-6
w12 = 0.2829e-6
w13 = 0.2829e-6
w31 = 0.4365e-6
w32 = 0.4365e-6
w33 = 0.4365e-6
num = 50

z_new, y1, y2, y3, y4 = taper_boundaries(w11, w12, w13, w31, w32, w33, T_length, num)
plt.plot(z_new * 1e6, y1 * 1e6, label='y1')
plt.plot(z_new * 1e6, y2 * 1e6, label='y2')
plt.plot(z_new * 1e6, y3 * 1e6, label='y3')
plt.plot(z_new * 1e6, y4 * 1e6, label='y4')
plt.legend()
plt.show()  # the derivatives of curves at start/end points are clamped to zero

# Slab layer stacks: all slabs should have the same thickness
s_core = reme.Slab(m_sio2(t_substrate) + m_si(t_core) + m_sio2(t_clad))
s_clad = reme.Slab(m_sio2(t_substrate) + m_sio2(t_core + t_clad))

taper_rwgs = []
taper_guides = []
taper_dict = {}
joint_dict = {}

# Input section
w1 = Clad_width
w2 = WG_width
w3 = WG_gap
total_width = Clad_width * 2 + WG_width * 2 + WG_gap
input_rwg = reme.RWG(s_clad(w1) + s_core(w2) + s_clad(w3) + s_core(w2) + s_clad(w1))
input_guide = reme.FMMStraight(input_rwg)
input_guide.set_left_boundary(reme.PEC)
input_guide.set_right_boundary(reme.PEC)
input_guide.find_modes(nmax=m_si.n().real, nmin=m_sio2.n().real, scan_step=0.01)

# Taper sections
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
    # Scan for modes instead of finding a certain number of modes directly.
    # In this way, degenerated modes won't be missed.
    taper_guides.append(guide)
    # print 'i =', i, 'w2 =', w2, 'w4 =', w4
    # print to check if the taper section is symmetric.

# Create the taper section device
# Create dictionaries of wgs/joints in order to generate dynamic variables
# Use add_element(element) to build up the loop with joint sections added inside taper.
taper = reme.Device()
step = T_length / num
for i in range(num - 1):
    taper_name = 'taper' + str(i)
    joint_name = 'joint' + str(i)
    taper_dict[taper_name] = reme.WaveguideSection(taper_guides[i], step)
    taper.add_element(taper_dict[taper_name])
    joint_dict[joint_name] = reme.Joint(taper_guides[i], taper_guides[i + 1])
    taper.add_element(joint_dict[joint_name])

last_taper_section = reme.WaveguideSection(taper_guides[num - 1], step)
taper.add_element(last_taper_section)

# Need a joint between input section and taper section
input_taper_joint = reme.Joint(input_guide, taper_guides[0])

# output_taper_joint = reme.Joint(input_taper_joint)
# output_taper_joint.mirror()
output_taper_joint = reme.Joint(taper_guides[num - 1], input_guide)

# Put everything together
input_section = reme.WaveguideSection(input_guide, 5.7749e-6)
output_section = reme.WaveguideSection(input_guide, 5.7749e-6)

coupler = reme.Device([input_section, input_taper_joint, taper, output_taper_joint, output_section])

# plotting the refractive index profile
coupler.plot_refractive_index_Xcut(0.6e-6, 0, total_width, 201, 0, coupler.get_length(), 401)

coupler.add_left_port(Clad_width + WG_width * 0.5, 0.2e-6 + WG_width,
                      5)  # port center position, port width, number of modes
coupler.add_left_port(Clad_width + WG_width * 1.5 + WG_gap, 0.2e-6 + WG_width,
                      5)
coupler.add_right_port(Clad_width + WG_width * 0.5, 0.2e-6 + WG_width, 5)
coupler.add_right_port(Clad_width + WG_width * 1.5 + WG_gap, 0.2e-6 + WG_width, 5)  # need to be changed to 1.5*wg_width

# coupler.clear_incident_left()
coupler.set_left_input_port(0, 0, 0.5)  # set the excitation (use the port mode) and run the simulation
coupler.set_left_input_port(1, 0, 0.5)

coupler.calculate()

# plot the field
print("Lower output power: {:.2f}".format(abs(coupler.get_right_output_port(0, 0)) ** 2))
print("Upper output power: {:.2f}".format(abs(coupler.get_right_output_port(1, 0)) ** 2))
coupler.plot_field_Xcut(x0=0.6e-6, y1=0, y2=total_width, ny=201,
                        z1=0, z2=coupler.get_length(), nz=201,
                        direction=0, field_component='Int', data_format='Abs')
