#!/bin/bash

# script run-real.sh
#SBATCH -J real_WRF4
#SBATCH -p workq2
#SBATCH -N 3
#SBATCH --ntasks-per-node 42
#SBATCH --exclusive
#SBATCH -o slurm.%x.%j.out
#SBATCH -e slurm.%x.%j.err
#SBATCH --mail-user=pohema.gonzalez@gmail.com
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END

cd /LUSTRE/ID/hidromet/WRF/Dominio3/WRFV4/WRF
ml load intel/2022u2/compilers
ml load curl hdf5 jasper libaec libpng mpi netcdf-c netcdf-fortran zlib
ml load wrf/4.2.1

export CORES=126
/sbin/logsave REGISTRO_REAL_n_210_5_workq2_dCorona mpirun -np $CORES real.exe

