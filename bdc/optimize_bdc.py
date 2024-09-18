from bdc_utils_fd import simulate_bdc
from opt_utils import optimize_bdc

wg_gap = 0.2e-6
wg_width = 0.45e-6
wavelengths = [1.54e-6, 1.545e-6, 1.55e-6, 1.56e-6, 1.565e-6]
# wavelengths = [1.29556e-6, 1.30005e-6, 1.30458e-6, 1.30914e-6]
res = optimize_bdc(
    wg_gap,
    wg_width,
    wavelengths,
    initial_w3=5.5e-07,
    initial_t_length=15e-6,
    initial_w1=0.45e-6,
    max_iter=200,
    verbose=True,
)

print("OPTIMIZATION RESULTS")
print("Optimal w1 = {} m".format(res[0]))
print("Optimal w3 = {} m".format(res[1]))
print("Optimal taper length = {} m".format(res[2]))
print("wg width = {} m".format(wg_width))
print("wg_gap = {} m".format(wg_gap))
