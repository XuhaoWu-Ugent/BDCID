from bdc_utils_fd import simulate_bdc
import numpy as np
import pylab as plt


w3 = np.arange(0.38, 0.6, 0.01)*1e-6  # width doesn't really change the power ratio
# lengths = np.arange(14, 16, 0.1)*1e-6
power_ratio_w_sweep = []

for w in w3:
    power_ratio, trans = simulate_bdc(
        wavelengths=[1.31e-6],
        wg_width=0.38e-6,
        wg_gap=0.2e-6,
        w1=0.38e-6,
        w3=w,
        t_length=16e-6
    )
    print 'power_ratio', power_ratio[0]
    power_ratio_w_sweep.append(power_ratio[0])

plt.plot(w3, power_ratio_w_sweep, "bo-")
plt.xlabel("width [m]")
plt.ylabel("power_ratio")
plt.show()
