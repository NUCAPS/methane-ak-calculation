import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr
import sys
from glob import glob

# Open conversion file
# trans_m = xr.open_dataset("NUCAPS_transformation_matrix.nc")
# g_t_T = trans_m.ch4_f_plus_matrix.values #12x100
# g_t_T = np.ma.masked_invalid(g_t_T)
# g_t = np.transpose(g_t_T) #100x12

# def get_ak_100(ak):
#     return np.ma.dot(np.ma.dot(g_t, ak), g_t_T)

# Open all AK files
files = glob('/mnt/firex-s3/2019/*/*/akfiles/'+'*.nc')
num_files = len(files)

dims = (num_files*1800, 11)
diag_ch4 = np.full(dims, np.nan)

# Can't allocate enough mem
# dims = (num_files*1800, 100)
# diag_ch4_100 = np.full(dims, np.nan)

start_pos = 0

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

    # There are some funky AK values (e.g. beyond the 0 to 1 range...), but perform QC using if statement
    ak_ch4 = [np.diag(df.ch4_ave_kern.values[:-1,:-1, i]) for i in cris_fors if ((np.nansum(df.ch4_ave_kern.values[:-1,:-1,i]) > 0) & (df.qcmask.values[i] == 0))]
    # ak_ch4_100 = [np.diag(get_ak_100(df.ch4_ave_kern.values[:-1,:-1, i])) for i in cris_fors if ((np.nansum(df.ch4_ave_kern.values[:-1,:-1,i]) > 0) & (df.qcmask.values[i] == 0))]


    for j in np.arange(0, len(ak_ch4)):
        diag_ch4[start_pos+j,:] = ak_ch4[j]
        # diag_ch4_100[start_pos+j,:] = ak_ch4_100[j]

    start_pos = start_pos+j+1

np.savez('diag_ch4.npx', diag_ch4)
# np.savez('diag_ch4_100.npx', diag_ch4)

sys.exit()
# Calc mean/standard deviation
mean_ak = np.nanmean(diag_ch4, axis=0)
std_ak = np.nanstd(diag_ch4, axis=0)

# Test plot
fig, ax = plt.subplots(1,1, figsize=(3, 3))
ax.set_title("Methane Ave. Kern")
ax.errorbar(mean_ak, pch4, xerr=std_ak, c='tab:red', linewidth=1)
ax.set_ylim(1000,0)
ax.set_xlim(0,0.25)
plt.savefig('methane-ak.png')
plt.close()

# Save output
d = {'press': pch4, 'mean': mean_ak, 'std': std_ak}
df = pd.DataFrame(data=d)
df.to_csv('firex-ch4-aks.csv', index=False)


