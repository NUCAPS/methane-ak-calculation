import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr
import sys
from glob import glob

# Custom params
plt.rcParams.update({'font.size': 22})

# Read pressure levels
plevs = pd.read_csv('nucaps-pressure-grid.csv')

#Single pass through std using Welford's algorithm
# https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
def update(existingAggregate, newValue):
    (count, mean, M2) = existingAggregate
    count += 1
    delta = newValue - mean
    mean += delta / count
    delta2 = newValue - mean
    M2 += delta * delta2
    return (count, mean, M2)

def finalize(existingAggregate):
    (count, mean, M2) = existingAggregate
    if count < 2:
        return float("nan")
    else:
        (mean, variance) = (mean, M2 / count)
        return (mean, variance)

# Open conversion file
trans_m = xr.open_dataset("NUCAPS_transformation_matrix.nc")
g_t_T = trans_m.ch4_f_plus_matrix.values[:-1,:] #12x100
g_t_T = np.ma.masked_invalid(g_t_T)
g_t = np.transpose(g_t_T) #100x12

def get_ak_100(ak):
    return np.ma.dot(np.ma.dot(g_t, ak), g_t_T)

# Open all AK files
files = glob('/mnt/firex-s3/2019/*/*/akfiles/'+'*.nc')
num_files = len(files)

sum_x=np.zeros(11)
sum_sq=np.zeros(11)
sum_x_100=np.zeros(100)
sum_sq_100=np.zeros(100)
n=0

agg =  (n, sum_x, sum_sq)
agg_100 =  (n, sum_x_100, sum_sq_100)

# Cycle through all files and FORs, extract the AK of variable to compute mean and std
for ii, file in enumerate(files):
    print('-- Processing:', file, ii, '/', num_files)

    try:
        # skip corrupt files
        df = xr.open_dataset(file)
    except:
        continue

    if ii == 0:
        cris_fors = df['atrack*xtrack'].values
        pch4 = df.ch4_func_pres.values

    for i in cris_fors:
        # There are some funky AK values (e.g. beyond the 0 to 1 range...), but perform QC using if statement
        if ((np.nansum(df.ch4_ave_kern.values[:-1,:-1, i]) > 0) & (df.qcmask.values[i] == 0)):
            n=n+1

            # Fine layer AKM
            tmp_100 = get_ak_100(df.ch4_ave_kern.values[:-1,:-1, i])
            tmp_100 = np.diag(tmp_100).filled()

            # Coarse layer AKM
            tmp = np.diag(df.ch4_ave_kern.values[:-1,:-1, i])

            # Single pass variance, mean calculation parameters
            agg = update(agg, tmp)
            agg_100 = update(agg_100, tmp_100)

# Calc mean and std
mean_ak, std_ak = finalize(agg)
mean_ak_100, std_ak_100 = finalize(agg_100)

# Test plot
fig, ax = plt.subplots(1,1, figsize=(8, 8))
ax.set_title("Methane Ave. Kern")
ax.errorbar(mean_ak, pch4, xerr=std_ak, c='tab:red', linewidth=2, label='Coarse Layers')
ax.errorbar(mean_ak_100, plevs.effective_pressure.values, xerr=std_ak_100, c='tab:blue', linewidth=2, label='Fine Layers')
plt.legend()

ax.set_ylim(1000,0)
ax.set_xlim(0,0.25)
# plt.show()
plt.savefig('methane-ak.png')
plt.close()

# Save output
d = {'press': pch4, 'mean': mean_ak, 'std': std_ak}
df = pd.DataFrame(data=d)
df.to_csv('firex-ch4-aks.csv', index=False)

d = {'press': plevs.effective_pressure.values, 'mean': mean_ak_100, 'std': std_ak_100}
df = pd.DataFrame(data=d)
df.to_csv('firex-ch4-aks-100.csv', index=False)
