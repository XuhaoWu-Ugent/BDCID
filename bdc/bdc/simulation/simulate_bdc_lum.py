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
# For the details of the licensing contract and the conditions under which you may use this software, we refer to the
# EULA which was distributed along with this program. It is located in the root of the distribution folder. (
# luceda_academy/library/si_fab/si_fab/ipkiss/si_fab/components/dir_coupler/simulation/simulate_lum_BDC.py)

from ipkiss3 import all as i3
from ipkiss3.all.device_sim import lumerical_macros


def simulate_bdc_fdtd(layout, project_folder, mesh_accuracy=2, wavelengths=(1.25, 1.35, 101)):
    """Simulation recipe for a directional coupler in Lumerical FDTD.

    Parameters
    ----------
    layout : PCell.Layout object
        The layout of the directional coupler to be simulated.
    project_folder : str
        Folder where the simulation results should be stored.
    mesh_accuracy : float, optional
        Accuracy of the meshing.
    wavelengths : tuple, optional
        List of wavelengths at which to run the simulation.

    Returns
    -------
    smatrix : smatrix of the specified directional coupler in the specified wavelength range
    """

    # Simulation definition
    monitors = [i3.device_sim.Port(name=p.name, box_size=(0.5, 0.5)) for p in layout.ports]
    geometry = i3.device_sim.SimulationGeometry(layout=layout,
                                                waveguide_growth=layout.cladding_offset)
    outputs = [i3.device_sim.SMatrixOutput(name="smatrix",
                                           symmetries=[],
                                           wavelength_range=wavelengths)
               ]
    setup_macros = [lumerical_macros.fdtd_mesh_accuracy(mesh_accuracy=mesh_accuracy),
                    lumerical_macros.fdtd_profile_xy(alignment_port='in1')]
    material_map = {i3.TECH.MATERIALS.SILICON: 'Si (Silicon) - Palik',
                    i3.TECH.MATERIALS.SILICON_OXIDE: 'SiO2 (Glass) - Palik'}

    # Simulation job
    simjob = i3.device_sim.LumericalFDTDSimulation(
        geometry=geometry,
        outputs=outputs,
        monitors=monitors,
        setup_macros=setup_macros,
        project_folder=project_folder,
        solver_material_map=material_map,
        verbose=True,
        headless=False)

    # Execute and save_results
    smatrix = simjob.get_result(outputs[0].name)
    return smatrix
