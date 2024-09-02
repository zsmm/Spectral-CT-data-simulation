#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/5 上午11:19
# @Author  : Sesame CT
# @describe :
# @File    : Genimg.py
import os
import cv2
import random
from config import *
from utils import DrawImage, GenCircularCoordAndRadius
import numpy as np
from multiprocessing.pool import Pool
import time
import copy


def imadjust(img, low_in, high_in, low_out, high_out, gamma=1):
    img_adj = ((img - low_in) / (high_in - low_in)) ** gamma
    img_adj = img_adj * (high_out - low_out) + low_out
    img_adj[img <= low_in] = low_out
    img_adj[img >= high_in] = high_out

    return img_adj


def circ_mask():
    """
    Randomly generate mask ellipse
    :param img_size:
    :return:
    """

    a = img_size / (2.5 + random.random())
    b = a
    circ_mask = np.zeros([img_size, img_size])

    O_i = img_size // 2 + random.randint(-4, 4) * 4

    O_j = img_size // 2 + random.randint(-4, 4) * 4
    for i in range(img_size):
        for j in range(img_size):
            if (j - O_j) ** 2 / (a ** 2) + (i - O_i) ** 2 / b ** 2 <= 1:
                circ_mask[i, j] = 1
    return circ_mask[:, :], a, b, O_i, O_j


def blur_img(img_mask, img_input, is_bone=False):
    """
    Edge Feather
    canny edge detection
    Use Dilate for puffing, use one coarse particle and then another fine particle
    The puffing results of coarse particles are used to extract the original image, and then Gaussian blur is applied
    The puffing result of fine particles is used to locate the result that covers the original image, and the edge part is pasted back
    :param img:
    :return:
    """
    img_mask[img_mask != 0] = 255
    img = np.asarray(img_mask, dtype=np.uint8)  # Used for edge computing
    g = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # Fine particles
    g2 = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))  # Coarse particles
    imgCanny = cv2.Canny(img, threshold1=50, threshold2=220)
    water_density = np.zeros([img_size, img_size], dtype=np.float32)  # The density of water in bones
    # Puffing treatment
    img_dilate = cv2.dilate(imgCanny, g)
    img_dilate2 = cv2.dilate(imgCanny, g2)

    img_temp = copy.deepcopy(img_input)
    img_output = copy.deepcopy(img_input)

    img_temp[img_dilate2 == 0] = 0

    dst = cv2.GaussianBlur(img_temp, (3, 3), 0, 0, cv2.BORDER_DEFAULT)

    if is_bone:
        if random.choice([True, False]):  # Randomly decide whether to directly return to the bone boundary
            img_output[img_dilate != 0] = 0  # Set the bone boundary to 0 for generating water
            Bone_img = dst  # Bone edge image
            Bone_mean = Bone_img[np.nonzero(Bone_img)].mean()  # Find the minimum value in the bone image
            if Bone_mean > 1.4:
                Bone_mean = 1.4

            water_img = img_output
            water_max = np.max(water_img[np.nonzero(water_img)])
            water_min = np.min(water_img[np.nonzero(water_img)])
            if Bone_mean > water_max:  # If the minimum value in the bone is greater than the maximum value in the water, no treatment should be done
                water_density[water_img != 0] = 1.0 - (water_img[water_img != 0] / 1.4)
                img_output[img_dilate != 0] = Bone_img[img_dilate != 0]
            else:  # If opposite, the values in the water need to be scaled.
                water_img = imadjust(water_img, low_in=water_min, high_in=water_max, low_out=0, high_out=Bone_mean,
                                     gamma=1)
                water_density[water_img != 0] = 1.0 - (water_img[water_img != 0] / 1.4)
                img_output[img_dilate != 0] = dst[img_dilate != 0]
                img_output[water_img != 0] = water_img[water_img != 0]
            return img_output, water_density

    img_output[img_dilate != 0] = dst[img_dilate != 0]

    return img_output, water_density


def genbasis_imgs(img_path):
    """
    :param img: Input channel BGR
    :return:
    """
    name = img_path.split('_')[-1]
    name = name.split('.')[0]
    name = str(int(name))
    im_bgr = cv2.imread(img_path)
    im_rgb = im_bgr[:, :, ::-1]

    # 直方图均衡
    for i in range(3):
        im_rgb[:, :, i] = cv2.equalizeHist(im_rgb[:, :, i])

    shape = im_rgb.shape
    if shape[2] < 3:
        return
    img = cv2.resize(im_rgb, (img_size, img_size))
    img = img.astype(np.float32) / 255.0

    R_img = img[:, :, 0]

    img = cv2.resize(img, (64, 64))  # blurring image
    img = cv2.resize(img, (img_size, img_size))

    img[img < 0] = 0

    R_channel = img[:, :, 0]

    Circ_mask, a, b, O_i, O_j = circ_mask()
    I2_tubes = GenCircularCoordAndRadius(int(a), int(O_i), int(O_j))  # Coordinates and radii of test tubes
    I2_mask = DrawImage(I2_tubes)
    I2_mask_bool = np.array(I2_mask, dtype=bool)

    bone_mask = R_channel >= threshold4
    bone_mask = bone_mask * Circ_mask
    if (np.sum(bone_mask == 1) / np.sum(Circ_mask == 1)) <= 0.4 and (
            np.sum(bone_mask == 1) / np.sum(
        Circ_mask == 1)) >= 0.2:  # Define the range of bone area between 10% and 30%
        Bone_adj = imadjust(R_img, low_in=threshold3, high_in=1, low_out=0.6, high_out=1, gamma=1)
        Bone_img = Bone_adj * bone_mask * (0.8 + random.randint(0, 2) * 0.2)

        I2_img = I2_mask

        water_mask = (R_channel < threshold4) & (R_channel >= threshold1)
        water_adj = imadjust(R_img, low_in=threshold1, high_in=threshold4, low_out=threshold4, high_out=1.15, gamma=1)
        water_img = water_adj * water_mask

        Basis_bone = Bone_img * cacl_density * Circ_mask
        Basis_bone, Bone_water_density = blur_img(bone_mask, Basis_bone, is_bone=True)
        Basis_bone[I2_mask_bool] = 0  # There should be no bones in areas with iodine

        Basis_water = water_img * (1 - I2_mask) * water_density
        Basis_water, _ = blur_img(water_mask, Basis_water, is_bone=False)
        Basis_water = Basis_water + Bone_water_density
        Basis_water[I2_mask_bool] = (1 - I2_img[I2_mask_bool] / iodine_density)
        Basis_water = (Basis_water) * Circ_mask

        Basis_I2 = I2_img * Circ_mask
        Basis_I2, _ = blur_img(I2_mask, Basis_I2, is_bone=False)

        Basis_Air = np.ones(shape=[512, 512], dtype=np.float32)
        Basis_Air = Basis_Air - (Basis_water / water_density) - (Basis_bone / cacl_density) - (
                    Basis_I2 / iodine_density)
        Basis_Air = Basis_Air * air_density

        Basis_water.astype(np.float32).tofile(save_ct_path + '{}_label_water.raw'.format(name))
        Basis_I2.astype(np.float32).tofile(save_ct_path + '{}_label_I2.raw'.format(name))
        Basis_bone.astype(np.float32).tofile(save_ct_path + '{}_label_bone.raw'.format(name))
        Basis_Air.astype(np.float32).tofile(save_ct_path + '{}_label_air.raw'.format(name))


if __name__ == '__main__':
    path = './data/'
    images = os.listdir(path)  # Due to threshold operations, not all graphs may be usable
    images = [os.path.join(path, img) for img in images]

    p1 = time.time()
    cores = 1
    pool = Pool(processes=cores)
    pool.map(genbasis_imgs, images)
    p2 = time.time()
    print(p2 - p1)
