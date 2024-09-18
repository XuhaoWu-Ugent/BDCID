# BDCID
Broadband Directional Coupler Inverse Design


## Introduction
Based on Xuhao Wu's master thesis: [Broadband optical 2x2 couplers](https://lib.ugent.be/catalog/rug01:002945568). 
So far the code is migrated to Python 3 and realized in IPKISS for the layout design and Lumerical FDTD for the simulation. 

## Installation
To run the v1.0 code, you need to install the following dependencies:
- [IPKISS](https://www.lucedaphotonics.com/luceda-photonics-design-platform)
- [Lumerical FDTD](https://www.ansys.com/products/optics/fdtd)
- [Pymoo](https://pymoo.org/)

And the simulation code using REME is provided as well. To know more about REME, please refer to [REME](https://www.siliconphotonics.com.au/reme-software)

## Update history
2024/09/18: v1.0 code is released with IPKISS Layout code and Lumerical simulation code. (REME simulation code only in history)
Optimization algorithm is realized via NSGA-II.

## To-do list
1. Migrate the layout code to Gdsfactory and the simulation code to Meep.
2. Realize the optimization algorithm on GPU.
