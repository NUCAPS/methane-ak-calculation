# Examples for Computing Averaging Kernels

This repository shows how we calculated averaging kernels using a "science version" of NUCAPS that has averaging kernel inforamtion. Prior to v3.1, averaging kernals were not written to the NUCAPS EDR files. However, v3.1 of NUCAPS (~released Early 2024) will contain averaging kernel for temperature, water vapor, and most trace gases.  While the repository says "methane" in the title, the code was generalized for all trace gases.

We recommend looking at aks.ipynb to see how averaging kernels can be extracted for a dataset. The dataset used to generate the figrues is not publicly available, but the code can illustrate how to work with the NUCAPS EDRv3.1 averaging kernels when it is released (early 2024). firex-aks.py is similar to aks.ipynb, but is a scripted version and can be run in the background. Both sets of code will iterate through a given file directory, open the files, extract the averaging kernel information, and calculate the mean and standard deviation of the averaging kernel data, save it as a csv file, and then make a plot. The variable names will certainly be different in NUCAPS v3.1 than those shown here. We also included the transformation matrix (NUCAPS_transformation_matrix.nc) to convert the AKs on the reduced pressure coordinates to the fixed 100-level/layer grid in the NUCAPS EDR.

To learn more about averaging kernels:
* Maddy, E. S., & Barnet, C. D. (2008). Vertical Resolution Estimates in Version 5 of AIRS Operational Retrievals. IEEE Transactions on Geoscience and Remote Sensing, 46(8), 2375–2384. https://doi.org/10.1109/TGRS.2008.917498
* Maddy, E. S., Barnet, C. D., & Gambacorta, A. (2009). A Computationally Efficient Retrieval Algorithm for Hyperspectral Sounders Incorporating A Priori Information. IEEE Geoscience and Remote Sensing Letters, 6(4), 802–806. https://doi.org/10.1109/LGRS.2009.2025780
* Rodgers, C. D. (1998). Information content and optimisation of high spectral resolution remote measurements. Advances in Space Research, 21(3), 361–367. https://doi.org/10.1016/S0273-1177(97)00915-0
* Rodgers, C. D. (2004). Inverse methods for atmospheric sounding: theory and practice (Reprinted). Singapore: World Scientific.

