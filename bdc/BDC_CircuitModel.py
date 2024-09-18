import ipkiss3.all as i3
import numpy as np
import matplotlib.pyplot as plt
import os
# smat = i3.device_sim.SMatrix1DSweep.from_touchstone('smatrix.s4p', term_mode_map = {('in1', 1): 0, ('in1', 2): 1, ('out1', 1): 2, ('out1', 2): 3,})
import joblib
project_folder = os.path.abspath("./test_BroadbandDC")
for cnt in np.linspace(5.0, 6.0, 3):
    smat = joblib.load(os.path.join(project_folder, "smatrix.s4p".format(0.1, 0.4, cnt)))
    # print smat[2, 0]
    # x = len(smat[2, 0])
    # print x
    # assert smat['in1:1', 'out1:1', 0] == smat[0, 0, 0]
    # assert smat['in1:2', 'out1:1', 0] == smat[1, 0, 0]
    # assert smat['out1:2', 'in1:1', 0] == smat[3, 0, 0]
    wavelengths = smat.sweep_parameter_values
    len(wavelengths)
    # if cnt == 0.4:
    # plt.plot(wavelengths, np.unwrap(np.angle(smat["in1_1", "out1_1"]))/np.pi, 'x-', markersize=7, linewidth=2, label='Odd Mode-{}'.format(cnt))
    plt.plot(wavelengths, np.abs(smat["in1:mode 0", "out1:mode 0"]), 'x-', markersize=7, linewidth=2, label='Odd Mode-{}'.format(cnt))
    # plt.plot(wavelengths, np.abs(smat["in1_1", "out1"]), 'x-', markersize=7, linewidth=2,
    #             label='Odd Mode-Even Mode{}'.format(cnt))
    # plt.plot(wavelengths, np.unwrap(np.angle(smat["in1", "out1"])), 'x-', markersize=7, linewidth=2, label='Even Mode')
    plt.xlabel("Wavelengths (\um)")
    plt.ylabel("S")
    # plt.ylabel("Phase [pi (rad)]")
    plt.legend()
plt.show()