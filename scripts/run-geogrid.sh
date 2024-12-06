#!/bin/bash
# script run-geogrid.sh
#SBATCH -J WRF4_geogrid
#SBATCH -p workq2
#SBATCH -N1
#SBATCH --ntasks-per-node 1
#SBATCH --exclusive
#SBATCH -o slurm.%x.%j.out
#SBATCH -e slurm.%x.%j.err
#SBATCH --mail-user=pohema.gonzalez@gmail.com
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END

cd /LUSTRE/ID/hidromet/WRF/Dominio3/WRFV4/WPS
ml load intel/2022u2
ml load curl hdf5 jasper libaec libpng mpi netcdf-c netcdf-fortran zlib
ml load wrf/4.2.1
srun /sbin/logsave REGISTRO_GEOGRID geogrid.exe
