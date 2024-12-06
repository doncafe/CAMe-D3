#!/bin/bash

# script run-wrf.sh
#SBATCH -J wrf_WRF4
#SBATCH -p operativo2
#SBATCH -N 4
#SBATCH --ntasks-per-node 39
#SBATCH --exclusive
#SBATCH -o slurm.%x.%j.out
#SBATCH -e slurm.%x.%j.err
#SBATCH --mail-user=pohema.gonzalez@gmail.com,poropeza@atmosfera.unam.mx
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END

cd /LUSTRE/ID/hidromet/WRF/Dominio3/WRFV4/WRF
ml load intel/2022u2/compilers
ml load curl hdf5 jasper libaec libpng mpi netcdf-c netcdf-fortran zlib
ml load wrf/4.2.1

export CORES=156
/sbin/logsave REGISTRO_WRF_n_156_4_operativo2_dCorona_operativo mpirun -np $CORES wrf.exe
