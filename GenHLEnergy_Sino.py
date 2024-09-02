#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/14 上午9:15
# @Author  : Sesame CT
# @describe :生成高低能sino图像
# @File    : GenHLEnergy_Sino.py
import pandas as pd
from config import *
import scipy.ndimage
import time
from multiprocessing.pool import Pool
import random

def XlsRead(file_name, sheet, column, row_range):
    """
    Read xlsx files
    : paramfile_name: file path+file name
    : paramsheet: Sheet ordinal number, starting from 0
    : param column: column index, starting from 0
    : paramrow_range: Line range, specific subscripts should be calculated from the actual number in Excel, starting from 0
    """
    df = pd.read_excel(file_name, sheet_name=sheet)
    data = df.iloc[row_range[0]: row_range[1], column].values
    return data


def LoadSino(files_path, sub_num, NumDet, Views):
    """
    Loading Multi Energy Sino
    : paramfiles_path: nino storage location
    : paramOrdinal_number: Total ordinal number of the image
    : paramnumdet: Number of detectors
    : param views: Projection angle degree
    """
    sc = np.fromfile(os.path.join(files_path, '{}_label_bone.raw'.format(sub_num)), dtype=np.float32)
    si = np.fromfile(os.path.join(files_path, '{}_label_I2.raw'.format(sub_num)), dtype=np.float32)
    sw = np.fromfile(os.path.join(files_path, '{}_label_water.raw'.format(sub_num)), dtype=np.float32)

    sc = np.reshape(sc, [Views, NumDet])
    si = np.reshape(si, [Views, NumDet])
    sw = np.reshape(sw, [Views, NumDet])
    return sc, si, sw


def MultiGenHighLowEnergySino(parms):
    """
    Generate high and low energy sine maps
    """

    sino_low = np.zeros([parms[3], parms[2]], dtype=np.float32)
    sino_high = np.zeros([parms[3], parms[2]], dtype=np.float32)

    sino_low_esq = np.zeros([parms[3], parms[2]], dtype=np.float32)
    sino_high_esq = np.zeros([parms[3], parms[2]], dtype=np.float32)

    sino_Bone50, sino_I2, sino_water = LoadSino(parms[0], parms[1], parms[2], parms[3])

    np_exp = []
    pow_number = []
    for j in range(len(parms[5])):
        np_exp.append(np.exp(-parms[6][j] * sino_water - parms[7][j] * sino_Bone50 - parms[8][j] * sino_I2))
        pow_number.append(pow((j + 20) / energy_weighted * parms[14][j], 2))

    for j in range(len(parms[4])):
        n_low = parms[9] * parms[4][j] * np_exp[j]
        sino_low = sino_low + n_low * (j + 20) / energy_weighted * parms[14][j]
        sino_low_esq = sino_low_esq + n_low * pow_number[j]

    for j in range(len(parms[5])):
        n_high = parms[9] * parms[5][j] * np_exp[j]
        sino_high = sino_high + n_high * (j + 20) / energy_weighted * parms[14][j]  # /100 energy weighted
        sino_high_esq = sino_high_esq + n_high * pow_number[j]

    sino_low = np.float32(sino_low + np.random.normal(size=sino_low.shape) * np.sqrt(sino_low_esq))
    sino_low = np.reshape(sino_low, [parms[2] // parms[10], parms[3], parms[10]])
    sino_low = np.mean(sino_low, axis=2)
    sino_low[sino_low < 0] = 1

    sino_high = np.float32(sino_high + np.random.normal(size=sino_high.shape) * np.sqrt(sino_high_esq))
    sino_high = np.reshape(sino_high, [parms[2] // parms[10], parms[3], parms[10]])
    sino_high = np.mean(sino_high, axis=2)
    sino_high[sino_high < 0] = 1

    sino_low = scipy.ndimage.filters.convolve(sino_low, parms[11], mode='nearest')
    sino_high = scipy.ndimage.filters.convolve(sino_high, parms[11], mode='nearest')

    sino_low_poisson = -np.log(sino_low / parms[12])
    sino_high_poisson = -np.log(sino_high / parms[13])

    sino_low_poisson.astype(np.float32).tofile(save_LH_path + '{}_sino_low.raw'.format(parms[1]))
    sino_high_poisson.astype(np.float32).tofile(save_LH_path + '{}_sino_high.raw'.format(parms[1]))


def MultiMain():
    file_path = save_sino_path
    imgs = os.listdir(file_path)
    imgs = [img.split('_')[0] for img in imgs]
    imgs = set(imgs)

    Csl_absorption_efficiency = XlsRead('./xlsx/xplot_CsI.xlsx', sheet=0, column=9, row_range=[14, 120])

    rate_20_75 = XlsRead(spectrum_xlsx_path, sheet=0, column=2, row_range=[12, 68])  # 20-75KeV
    rate_20_125 = XlsRead(spectrum_xlsx_path, sheet=1, column=2, row_range=[7, 113])  # 20-125KeV

    water = XlsRead(sensitometry_xlsx_path, sheet=5, column=6, row_range=[0, 106])
    Bone50 = XlsRead(sensitometry_xlsx_path, sheet=10, column=6, row_range=[0, 106])
    I2 = XlsRead(sensitometry_xlsx_path, sheet=12, column=1, row_range=[0, 106])

    water = water / 10
    Bone50 = Bone50 / 10
    I2 = I2 / 10

    E_l = np.asarray([i for i in range(20, 75 + 1)], dtype=np.float32)
    E_h = np.asarray([i for i in range(20, 125 + 1)], dtype=np.float32)

    I0_temp = random.choice(I0)

    # 乘以CsI吸收效率
    bkg_low = np.float32(I0_temp * E_l.dot(rate_20_75 * Csl_absorption_efficiency[0:56]) / energy_weighted)
    bkg_high = np.float32(I0_temp * E_h.dot(rate_20_125 * Csl_absorption_efficiency[0:106]) / energy_weighted)

    parms = [(file_path, img, NumDet, Views, rate_20_75, rate_20_125, water, Bone50, I2, I0_temp,
              factor_ray, gaussian_kernel, bkg_low, bkg_high, Csl_absorption_efficiency) for img in imgs]

    start = time.time()
    pool = Pool(processes=os.cpu_count())
    pool.map(MultiGenHighLowEnergySino, parms)
    end = time.time()
    print(end - start)


if __name__ == '__main__':
    MultiMain()
