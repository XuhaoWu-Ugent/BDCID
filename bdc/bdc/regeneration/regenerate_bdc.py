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

"""This script regenerates the data used for the circuit model of the optimized Y-branch.
It does this by running the simulation of the Y-branch's layout through the Luceda Link for Ansys Lumerical.
It outputs the simulation result in the data folder for use in the circuit model.
Use this script to replicate the data whenever the layout is updated in order to keep this circuit model in sync.
"""

from si_fab import all as pdk
from bdc.cell import BroadbandDirectionalCoupler
from regen_utils import regenerate_bdc

regenerate_bdc(bdc_class=BroadbandDirectionalCoupler, wavelengths=(1.25, 1.35, 101), center_wavelength=1.3,
               resimulate=True, plot=True)
