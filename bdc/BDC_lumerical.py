from BroadbandDirectionalCoupler import DirectionalCoupler
from simulate_lum_BDC import simulate_bdc
import os
import joblib
from ipkiss3 import all as i3

dc = DirectionalCoupler()
lv = dc.Layout()
lv.visualize(annotate=True)
wavelengths = (1.5, 1.6, 100)
project_folder = os.path.abspath("./test_BroadbandDC")
smatrix = simulate_bdc(layout=lv, project_folder=project_folder, wavelengths=wavelengths)
# Save data
smatrix_path = os.path.join(project_folder, "dc_{}.z".format(dc.t_length))
joblib.dump(smatrix, smatrix_path)

# cm_BDC = joblib.load(smatrix)
