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

from si_fab import all as pdk
import ipkiss3.all as i3
from bdc.cell import BroadbandDirectionalCoupler
from bdc.optimization.opt_utils import (
    # optimize_gc_pso,
    optimize_bdc_nsga2
    # optimize_gc_pso_in_and_sub
)

wavelength = 1.31


def main():
    best_solutions, best_bar_diff, best_cross_diff, best_trans_ratio, best_trans_bar, best_reflection = (
        optimize_bdc_nsga2(
            bdc_class=BroadbandDirectionalCoupler,
            max_gen=30,
            pop_size=20,
            wavelengths=(1.25, 1.35, 101),
            center_wavelength=1.31,
            verbose=True,
            plot=True,
            n_best_solutions=10
        ))

    print("OPTIMIZATION RESULTS")
    print("Top 10 solutions:")
    for i, (solution, bar_diff, cross_diff, trans_ratio, trans_bar, reflection) \
            in enumerate(
        zip(best_solutions, best_bar_diff, best_cross_diff, best_trans_ratio, best_trans_bar, best_reflection), 1):
        print(f"\nSolution {i}:")
        print(f"Wg length = {solution[0]:.3f} um")
        print(f"Taper length = {solution[1]:.3f} um")
        print(f"Taper width = 0.38, "
              f"{solution[2]:.3f},"
              f"{solution[3]:.3f},"
              f"{solution[4]:.3f},"
              f"{solution[5]:.3f},"
              f"{solution[6]:.3f},"
              f"{solution[7]:.3f},"
              f"{solution[8]:.3f},"
              f"{solution[9]:.3f},"
              f"{solution[10]:.3f},"
              f"0.38 um")
        print(f"coupling spacing = {solution[11]:.3f} um")
        print(f"Max-min bar diff: {bar_diff:.3f}")
        print(f"Max-min cross diff: {cross_diff:.3f}")
        print(f"Trans ratio (difference with 0.5): {trans_ratio:.3f}")
        print(f"Trans bar (difference with 0.5): {trans_bar:.3f}")
        print(f"Reflection: {reflection:.3f}")

    print("\nVisualization:")
    print("1. Objective function history has been saved as 'objective_history.png'")


if __name__ == "__main__":
    main()
