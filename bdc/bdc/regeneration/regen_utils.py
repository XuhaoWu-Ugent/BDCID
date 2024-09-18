# Copyright (C) 2020 Luceda Photonics
# This version of Luceda Academy and related packages
# (hereafter referred to as Luceda Academy) is distributed under a proprietary License by Luceda
# It does allow you to develop and distribute add-ons or plug-ins, but does
# not allow redistribution of Luceda Academy  itself (in original or modified form).
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# For the details of the licensing contract and the conditions under which
# you may use this software, we refer to the
# EULA which was distributed along with this program.
# It is located in the root of the distribution folder.

from si_fab import technology  # noqa: F401
from bdc.simulation.simulate_bdc_lum import simulate_bdc_fdtd
from ipkiss3 import all as i3
from ipkiss3.simulation.circuit.utils import convert_smatrix_units
import numpy as np
import pylab as plt
import os
import json


def regenerate_bdc(bdc_class, wavelengths, center_wavelength, resimulate=True, plot=True):
    """It regenerates the simulation fitting data and/or the plots of the optimized bdc.

    Parameters
    ----------
    bdc_class :
        PCell class of the bdc to resimulate or replot
    wavelengths : tuple
        Tuple representing the wavelength range for the simulation and for the plots. The tuple must be in the format
        (min, max, number of points).
    center_wavelength: float
        The center wavelength around which to have polynomial fitting
    resimulate : boolean, optional, default=True
        If True, it runs the Lumerical FDTD simulation of gc_class, fits the transmission and reflection as a
        function of wavelength and stores the fitting coefficients in data/component_name.json
    plot : boolean, optional, default=True
        If True, it plots the transmission and reflection as a function of wavelength.
    """

    bdc = bdc_class()
    # Paths
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "data")
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    base_directory = os.path.join(data_dir, bdc.data_tag)
    if not os.path.exists(base_directory):
        os.mkdir(base_directory)
    base_directory_lum = os.path.join(base_directory, "lum")
    if not os.path.exists(base_directory_lum):
        os.mkdir(base_directory_lum)
    base_directory_model = os.path.join(base_directory, "model")
    if not os.path.exists(base_directory_model):
        os.mkdir(base_directory_model)

    project_folder = base_directory_lum
    smatrix_path = os.path.join(base_directory_lum, "smatrix.s3p")
    params_path = os.path.join(base_directory_model, "params.json")

    wavelengths_array = np.linspace(wavelengths[0], wavelengths[1], wavelengths[2])

    if resimulate:
        # Instantiate
        bdc_lo = bdc.Layout()
        if plot:
            bdc_lo.visualize(annotate=True)
            bdc_lo.visualize_2d()
        # Simulate
        smatrix = simulate_bdc_fdtd(
            layout=bdc_lo,
            project_folder=project_folder,
            wavelengths=wavelengths,
            # inspect=True
        )

        smatrix.to_touchstone(smatrix_path)

        print("Done")

    # Fitting
    smatrix = convert_smatrix_units(
        i3.device_sim.SMatrix1DSweep.from_touchstone(smatrix_path),
        to_unit="um",
    )
    transmission_bar = np.abs(smatrix["in1", "out1"])
    transmission_cross = np.abs(smatrix["in1", "out2"])
    reflection = np.abs(smatrix["in1", "in1"])
    pol_trans_bar = np.polyfit(wavelengths_array - center_wavelength, transmission_bar, 7)
    pol_trans_cross = np.polyfit(wavelengths_array - center_wavelength, transmission_cross, 7)
    pol_refl = np.polyfit(wavelengths_array - center_wavelength, reflection, 7)
    # Save
    results_np = {
        "center_wavelength": center_wavelength,
        "pol_trans_bar": pol_trans_bar,
        "pol_trans_cross": pol_trans_cross,
        "pol_refl": pol_refl,
    }

    def serialize_ndarray(obj):
        return obj.tolist() if isinstance(obj, np.ndarray) else obj

    with open(params_path, "w") as f:
        json.dump(results_np, f, sort_keys=True, default=serialize_ndarray, indent=2)

    if plot:
        with open(params_path, "r") as f:
            coefficients = json.load(f)

        center_wavelength = coefficients["center_wavelength"]
        transmission_bar_fit = np.polyval(coefficients["pol_trans_bar"], wavelengths_array - center_wavelength)
        transmission_cross_fit = np.polyval(coefficients["pol_trans_cross"], wavelengths_array - center_wavelength)
        reflection_fit = np.polyval(coefficients["pol_refl"], wavelengths_array - center_wavelength)
        transmission_up_error = (transmission_bar_fit - transmission_bar) / max(transmission_bar)
        transmission_down_error = (transmission_cross_fit - transmission_cross) / max(transmission_cross)
        reflection_error = (reflection_fit - reflection) / max(reflection)

        print(
            f"The maximum fitting relative error is {max(transmission_up_error)}  in transmission up, "
            f"{max(transmission_down_error)} in transmission down"
            f" and {max(reflection_error)} in reflection"
        )

        print("Plotting...")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

        # 原始数据
        ax1.plot(wavelengths_array, i3.signal_power_dB(transmission_bar), label="Transmission Up")
        ax1.plot(wavelengths_array, i3.signal_power_dB(transmission_bar_fit), label="Transmission Up Fitted")
        ax1.plot(wavelengths_array, i3.signal_power_dB(reflection), label="Reflection")
        ax1.set_title("Original Data")
        ax1.legend()

        # 拟合数据
        ax2.plot(wavelengths_array, i3.signal_power_dB(transmission_cross), label="Transmission Down")
        ax2.plot(wavelengths_array, i3.signal_power_dB(transmission_cross_fit), label="Transmission Down Fitted")
        ax2.plot(wavelengths_array, i3.signal_power_dB(reflection_fit), label="Reflection Fitted")
        ax2.set_title("Fitted Data")
        ax2.legend()

        plt.tight_layout()
        plt.show()
    print("Done")
