from bdc_utils_fmm import simulate_bdc
import numpy as np
from scipy.optimize import minimize


def optimize_bdc(
        wg_gap,
        wg_width,
        wavelengths,
        initial_w1,
        initial_w3,
        initial_t_length,
        max_iter=200,
        verbose=False,
):
    """Optimizes the length and waveguide spacing of a 1x2 MMI at fixed wavelength, taper_length and width.

    Parameters
    ----------
    mmi_class :
        PCell class of the MMI to optimize
    width : float
        Width of the mmi [um]
    initial_w1 : float
        Width of the taper in the mmi [um]
    taper_length : float
        Length of the taper [um]
    initial_w3 : float, optional, default=2.0
        Initial waveguide separation of the MMI at the first iteration [um]
    initial_t_length : float, optional, default=10.0
        Initial length of the MMI at the first iteration [um]
    max_iter : int, optional, default=50
        Max number of iterations for the optimization
    wavelengths : float list, optional, default=1.55
        Wavelength of the optimization [um]
    verbose : boolean, optional, default=False
        Print statements if True
    plot : boolean, optional, default=True
        Plot the optimized result

    Returns
    -------
    optimized_length, optimized_waveguide_spacing : float, float
        Optimized length and waveguide spacing for the MMI
    """

    def to_minimize(x):
        power_ratio, trans = simulate_bdc(
            wavelengths=wavelengths,
            wg_width=wg_width,
            wg_gap=wg_gap,
            w1=x[0],
            w3=x[1],
            t_length=x[2]
        )
        cost = max(np.abs([p - 0.5 for p in power_ratio]))

        if verbose is True:
            print("w1: {} - w3: {} - t_length: {} - max power_ratio: {}".format(x[0], x[1], x[2],  cost))

        return cost

    res = minimize(
        to_minimize,
        x0=np.array([initial_w1, initial_w3, initial_t_length]),
        method='Nelder-Mead',
        options={'xtol': 1e-2, 'disp': True, 'maxiter': max_iter},
    )

    return res.x
