from BroadbandDirectionalCoupler import DirectionalCoupler
from simulate_lum_BDC import simulate_bdc
import os
import joblib
import numpy as np

wg_length = 25
t_width_u = 0.6
t_length = 6.5
num = 16

for i in np.linspace(0.1, 0.5, 5):
# sweep for the length of waveguide
    wgl = i
    for k in np.linspace(5, t_length, num):
    # sweep for the length of taper
        tl = k
        for j in np.linspace(0.45, t_width_u, num):
        # sweep for the width of the upper taper section
            twu = j
            dc = DirectionalCoupler(wg_length=wgl, t_width_u=twu, t_length=tl, t_width_l=0.45)
            lv = dc.Layout()
            # lv.visualize(annotate=True)
            wavelengths = (1.5, 1.6, 100)
            project_folder = os.path.abspath("./test_database_BroadbandDC")
            smatrix = simulate_bdc(layout=lv, project_folder=project_folder, wavelengths=wavelengths)
            smatrix_path = os.path.join(project_folder, "dc_{}_{}_{}.z".format(dc.wg_length, dc.t_width_u, dc.t_length))
            joblib.dump(smatrix, smatrix_path)