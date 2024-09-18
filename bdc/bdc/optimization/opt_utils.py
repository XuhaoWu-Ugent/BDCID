from ..simulation.simulate_bdc_lum import simulate_bdc_fdtd
import numpy as np
import os
import ipkiss3.all as i3
import scipy.optimize as opt
import matplotlib.pyplot as plt
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.sampling.lhs import LatinHypercubeSampling
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.util.display.display import Display


# NSGA2
class BroadbandDirectionalCouplerProblem(Problem):
    def __init__(self, bdc_class, wavelengths, center_wavelength):
        super().__init__(n_var=12, n_obj=5, n_constr=1,
                         # wg_length, t_length, t_width_u[1]~t_width_u[9], coupling_spacing
                         xl=np.array([0.18, 0.18, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.18]),
                         xu=np.array([2.0, 6.0, 0.76, 0.76, 0.76, 0.76, 0.76, 0.76, 0.76, 0.76, 0.76, 0.6]))
        self.bdc_class = bdc_class
        self.wavelengths = wavelengths
        self.center_wavelength = center_wavelength

    def _evaluate(self, x, out, *args, **kwargs):
        f = np.full((x.shape[0], 5), 1e10)  # Initialize with the worst possible values
        g = np.zeros((x.shape[0], 1))

        for i, params in enumerate(x):
            params = np.round(params, 3)
            print(f"Evaluating: {params}")

            # Check constraints
            if params[0] < 0.18 or params[1] < 0.18 or params[11] < 0.18:
                g[i] = -1  # Constraint violation
                continue  # Skip to the next iteration

            data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "data")
            os.makedirs(data_dir, exist_ok=True)
            base_directory = os.path.join(data_dir, self.bdc_class().data_tag)
            os.makedirs(base_directory, exist_ok=True)
            base_directory_lum = os.path.join(base_directory,
                                              f"lum_{params[0]}_{params[1]}_{params[2]}_{params[3]}_{params[4]}_{params[5]}_{params[6]}_{params[7]}_{params[8]}_{params[9]}_{params[10]}")
            os.makedirs(base_directory_lum, exist_ok=True)

            smatrix_path = os.path.join(base_directory_lum, "smatrix.s4p")

            bdc = self.bdc_class(
                wg_length=params[0],
                wg_width=0.38,
                t_length=params[1],
                t_width_u=[0.38, params[2], params[3], params[4], params[5], params[6], params[7], params[8], params[9],
                           params[10], 0.38],
                t_width_l=[0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38, 0.38],
                coupler_spacing=params[11],
            )
            lv = bdc.Layout()

            try:
                smatrix = simulate_bdc_fdtd(
                    layout=lv,
                    project_folder=base_directory_lum,
                    wavelengths=self.wavelengths
                )
                smatrix.to_touchstone(smatrix_path)
                index = np.searchsorted(np.linspace(self.wavelengths[0], self.wavelengths[1], self.wavelengths[2]),
                                        self.center_wavelength)

                trans_bar = i3.signal_power(np.abs(smatrix["in1", "out1"])[index])
                trans_cross = i3.signal_power(np.abs(smatrix["in1", "out2"])[index])
                max_min_bar_diff = max(np.abs(smatrix["in1", "out1"])) - min(np.abs(smatrix["in1", "out1"]))
                max_min_cross_diff = max(np.abs(smatrix["in1", "out2"])) - min(np.abs(smatrix["in1", "out2"]))
                reflection = i3.signal_power(np.abs(smatrix["in1", "in1"])[index])

                f[i] = [
                    max_min_bar_diff,
                    max_min_cross_diff,
                    np.abs(trans_bar / (trans_cross + trans_bar) - 0.5),
                    np.abs(trans_bar - 0.5),
                    reflection
                ]  # Objectives to minimize
                g[i] = 0

                print(f"Transmission bar: {trans_bar}, transmission cross: {trans_cross}, reflection: {reflection}"
                      f"Max-min bar diff: {max_min_bar_diff}, max-min cross diff: {max_min_cross_diff}")
            except Exception as e:
                print(f"Error in simulation: {e}")

        out["F"] = f
        out["G"] = g


class MyDisplay(Display):
    def _do(self, problem, evaluator, algorithm):
        super()._do(problem, evaluator, algorithm)
        self.output.append("Best bar difference", algorithm.pop.get("F")[:, 0].min())
        self.output.append("Best cross difference", algorithm.pop.get("F")[:, 1].min())
        self.output.append("Best trans ratio (difference with 0.5)", algorithm.pop.get("F")[:, 2].min())
        self.output.append("Best trans bar (difference with 0.5)", algorithm.pop.get("F")[:, 3].min())
        self.output.append("Best reflection", algorithm.pop.get("F")[:, 4].min())


def optimize_bdc_nsga2(
        bdc_class,
        max_gen=100,
        pop_size=50,
        wavelengths=(1.25, 1.35, 101),
        center_wavelength=1.31,
        verbose=True,
        plot=True,
        n_best_solutions=10
):
    problem = BroadbandDirectionalCouplerProblem(bdc_class, wavelengths, center_wavelength)

    ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)

    algorithm = NSGA2(
        pop_size=pop_size,
        n_offsprings=pop_size,
        sampling=LatinHypercubeSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True,
        ref_dirs=ref_dirs
    )

    class MyCallback:
        def __init__(self) -> None:
            self.data = {
                "best_trans_up": [],
                "best_reflection": [],
                "best_trans_down": []
            }

        def __call__(self, algorithm):
            self.data["Best bar difference"].append(algorithm.pop.get("F")[:, 0].min())
            self.data["Best cross difference"].append(algorithm.pop.get("F")[:, 1].min())
            self.data["Best trans ratio (difference with 0.5)"].append(algorithm.pop.get("F")[:, 2].min())
            self.data["Best trans bar (difference with 0.5)"].append(algorithm.pop.get("F")[:, 3].min())
            self.data["Best reflection"].append(algorithm.pop.get("F")[:, 4].min())


    callback = MyCallback()

    display = MyDisplay() if verbose else None

    res = minimize(
        problem,
        algorithm,
        ('n_gen', max_gen),
        callback=callback,
        verbose=verbose,
        display=display,
        seed=1
    )

    if plot:

        # 绘制目标函数随代数的变化
        plt.figure(figsize=(12, 4))
        plt.subplot(151)
        plt.plot(callback.data['Best bar difference'])
        plt.title("Best bar difference")
        plt.xlabel("Generation")
        plt.subplot(152)
        plt.plot(callback.data['Best cross difference'])
        plt.title("Best cross difference")
        plt.xlabel("Generation")
        plt.subplot(153)
        plt.plot(callback.data['Best trans ratio (difference with 0.5)'])
        plt.title("Best trans ratio (difference with 0.5)")
        plt.xlabel("Generation")
        plt.subplot(154)
        plt.plot(callback.data['Best trans bar (difference with 0.5)'])
        plt.title("Best trans bar (difference with 0.5)")
        plt.xlabel("Generation")
        plt.tight_layout()
        plt.subplot(155)
        plt.plot(callback.data['Best reflection'])
        plt.title("Best reflection")
        plt.xlabel("Generation")
        plt.savefig('objective_history.png')
        plt.close()

    # 按优先级排序所有解
    sorted_indices = np.lexsort((res.F[:, 4], res.F[:, 3], res.F[:, 2], res.F[:, 1], res.F[:, 0]))
    best_solutions = res.X[sorted_indices[:n_best_solutions]]
    best_objectives = res.F[sorted_indices[:n_best_solutions]]

    return best_solutions, best_objectives[:, 0], best_objectives[:, 1], best_objectives[:, 2], best_objectives[:, 3], best_objectives[:, 4]
