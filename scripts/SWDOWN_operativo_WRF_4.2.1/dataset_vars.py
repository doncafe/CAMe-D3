#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read WRF variables
"""
import netCDF4 as nc
WRF_file = "/LUSTRE/ID/hidromet/WRF/Salidas_WRF_mayo_2022/wrfout_d02_2022-05-02_00.nc"
dataset = nc.Dataset(WRF_file, 'r')
print(dataset.variables.keys())