"""
Script to demonstrate capabilities to load and post-process SOLPS results.
Note that SOLPS output is not distributed with Aurora; so, in order to run this script,
either you are able to access the default AUG SOLPS MDS+ server, or you need
to appropriately modify the script to point to your own SOLPS results.
"""
import numpy as np
import matplotlib.pyplot as plt

plt.ion()
from omfit_classes import omfit_eqdsk
import sys, os
import aurora
import glob

shot = 1070614013
experiment = sys.argv[1]
name = sys.argv[2]

SOLPSWORK = '/nobackup1/users/millerma/solps-iter/runs'

run_path = '{}/{}/{}/{}'.format(SOLPSWORK,shot,experiment,name)
base_path = '{}/{}/{}/baserun'.format(SOLPSWORK,shot,experiment)
# alternatively, one may want to load SOLPS results from files on disk:
so = aurora.solps_case(
    b2fstate_path="{}/b2fstate".format(run_path),
    b2fgmtry_path="{}/b2fgmtry".format(run_path),
    geqdsk = glob.glob("{}/g{}.*".format(base_path,shot))[0]
#    geqdsk = '/nobackup1/millerma/solps-iter/runs/{}/{}/baserun/g1070614013.00793_610'.format(shot, experiment)
)

# pull source from balance.nc file - interpolate from cell faces onto cell centers
import netCDF4 as nc
fn = '{}/balance.nc'.format(run_path)
ds = nc.Dataset(fn)

sna = ds['eirene_mc_papl_sna_bal']
vol = ds['vol'] # cell volumes
crx = ds['crx'] # x-coords
cry = ds['cry'] # y-coords

sna_sum = np.sum(sna,axis=0) # sum over EIRENE strata
sna_Dplus_vol = sna_sum[1]/vol # get source per vol

sna_b2grid = sna_Dplus_vol[1:-1,1:-1]

# plot some important fields
fig, axs = plt.subplots(1, 2, figsize=(10, 6), sharex=True)
ax = axs.flatten()
so.plot2d_b2(so.data("ne"), ax=ax[0], scale="log", label=r"$n_e$ [$m^{-3}$]")
so.plot2d_b2(so.data("te"), ax=ax[1], scale="linear", label=r"$T_e$ [eV]")

if hasattr(so, "fort46") and hasattr(so, "fort44"):
    # if EIRENE data files (e.g. fort.44, .46, etc.) are available,
    # one can plot EIRENE results on the original EIRENE grid.
    # SOLPS results also include EIRENE outputs on B2 grid
    fig, axs = plt.subplots(1, 2, figsize=(10, 6), sharex=True)
    so.plot2d_eirene(
        so.fort46["pdena"][:, 0] * 1e6,
        scale="log",
        label=r"$n_D$ ($m^{-3}$)",
        ax=axs[0]
    )
    axs[0].set_ylabel('Z (m)', fontsize=14)
    axs[0].set_xlabel('R (m)', fontsize=14)
    axs[0].set_xlabel('R (m)', fontsize=14)
    axs[0].tick_params(axis='y', labelsize=14)
    axs[0].tick_params(axis='x', labelsize=14)
    so.plot2d_b2(sna_b2grid, label=r"$S_{ion}$ [$m^{-3}s^{-1}$]", ax=axs[1])
   #so.plot2d_b2(so.fort44["dab2"][:, :, 0].T, label=r"$n_n$ [$m^{-3}$]", ax=axs[1])
    plt.tight_layout()
