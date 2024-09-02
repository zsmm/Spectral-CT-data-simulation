#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/5 上午11:10
# @Author  : Sesame CT
# @describe :
# @File    : config.py
import os
import numpy as np

save_ct_path = './Train/Basis/'  # Image save path
if not os.path.exists(save_ct_path):
    os.makedirs(save_ct_path)

save_sino_path = './Train/Sino/' # Sino generates using reconstruction packages, such as LEAP CT or Matalb astra
if not os.path.exists(save_sino_path):
    os.makedirs(save_sino_path)

save_LH_path = './Train/SinoLH/'
if not os.path.exists(save_LH_path):
    os.makedirs(save_LH_path)

save_FBP_path = './Train/FBP/'
if not os.path.exists(save_FBP_path):
    os.makedirs(save_FBP_path)

tube_radius = [12, 27]  # Test tube value radius
boundary_distance = [10, 25]  # The distance range from the test tube to the boundary of the base circle
total_circular = 0
image_size = 512
tube_min_distance = 10
I2_density_range = [0.0015, 0.03]

######High and low energy Sino generation parameters#######.
gaussian_operator = [0.0005, 0.1196, 0.7599, 0.1196, 0.0005]  # Call Matlab and use the fspecific ('Gaussian ', [5,1], sigma) function to obtain sigma=0.52
gaussian_kernel = np.zeros([5, 5])
for i in range(len(gaussian_operator)):
    gaussian_kernel[2][i] = gaussian_operator[i]

NumDet = 700
Views = 900
Pixels = 512
I0_base = 1000000
# I0 = I0_base
I0 = [1e4, 3e4, 5e4, 1e5, 3e5, 5e5]
sigma = 0.52
energy_weighted = 100

spectrum_xlsx_path = './xlsx/spectrum_75-125kvp.xlsx'
sensitometry_xlsx_path = './xlsx/sensitometrydata_2013Ver.xlsx'

#######Sino reconstruction parameters##############
detector_num = 700
img_size = 512
rotate_num = 900
factor_ray = 1

SO = 1200
OD = 410
scale = 0.35
det_size = 0.417
nt = 1
nv_pi = 360
y_os = 0
tmp_size = rotate_num
BATCH_SIZE = 1

##########Density simulation parameters of base material map###########
water_density = 1.0
cacl_density = 0.5
iodine_density = 0.03
air_density = 1.293 * 1e-3

threshold1 = 0.1
threshold2 = 0.3
threshold3 = 0.5
threshold4 = 0.85