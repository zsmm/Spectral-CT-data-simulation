#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/13 下午2:19
# @Author  : Sesame CT
# @describe :工具函数
# @File    : utils.py
from config import *
import random
import math
import numpy as np
import cv2


def CalDistance(p1, p2):
    """
    求两点直线距离
    :param p1:
    :param p2:
    :return:
    """
    return math.sqrt(math.pow((p2[0] - p1[0]), 2) + math.pow((p2[1] - p1[1]), 2))


def GenCircularCoordAndRadius(base_r, base_x, base_y):
    """
    圆坐标生成函数
    :return: [[base_x, base_y, base_r],[x1, y1, r1],...,[xn, yn, rn]]
    """
    # base_r = random.randint(basewater_radius[0], basewater_radius[1])  # 随机生成基圆的半径
    # base_x = random.randint(center_coord_offset[0], center_coord_offset[1]) + (image_size // 2)
    # base_y = random.randint(center_coord_offset[0], center_coord_offset[1]) + (image_size // 2)  # 随机生成基圆中心坐标点

    circular_list = []
    while len(circular_list) < total_circular:  # 生成10个试管坐标
        tube_circular = RandomGenCircular(base_x, base_y, base_r)  # 生成一个试管坐标
        if IntersectionDetect(circular_list, tube_circular):
            circular_list.append(tube_circular)

    circular_list.insert(0, [base_x, base_y, base_r])
    return circular_list


def IntersectionDetect(circular_list, tube_circular):
    """
    相交检测
    :param circular_list: 坐标集
    :param tube_circular: 新生成的试管坐标
    :return: Bool
    """
    if circular_list == []:
        return True

    for i in range(len(circular_list)):
        distance = CalDistance([circular_list[i][0], circular_list[i][1]],
                               [tube_circular[0], tube_circular[1]])  # 计算两圆之间的距离
        if distance < (circular_list[i][2] + tube_circular[2] + tube_min_distance):  # 判断两圆之间距离小于半径之和加最小试管距离
            return False

    return True


def RandomGenCircular(base_x, base_y, base_r):
    """
    随机生成圆的坐标与半径
    :param base_x:
    :param base_y: 基圆坐标
    :param base_r: 基圆半径
    :return: 试管的坐标与半径（包括厚度）
    """
    tube_r = random.randint(tube_radius[0], tube_radius[1])  # 生成试管半径
    draw_r = base_r - random.randint(boundary_distance[0], boundary_distance[1])  # 计算试管到边界的距离范围,避免中心坐标落到基圆边界
    draw_r = draw_r - tube_r  # 减去试管半径,避免与基圆重合

    x_min = base_x - draw_r  # 计算试管坐标范围
    x_max = base_x + draw_r

    y_min = base_y - draw_r
    y_max = base_y + draw_r

    while True:  # 生成合适的坐标
        tube_x = random.randint(int(x_min), int(x_max))
        tube_y = random.randint(int(y_min), int(y_max))
        distance = CalDistance([base_x, base_y], [tube_x, tube_y])  # 计算试管到中心的距离
        if distance < draw_r:
            break
    return [tube_x, tube_y, tube_r]


def DrawImage(circular_list):
    """
    画图像
    :return:
    """
    label_I2 = np.zeros([image_size, image_size], dtype=np.float32)

    # 画I2
    for circular in circular_list[1:]:
        tube_x = circular[0]
        tube_y = circular[1]
        tube_r = circular[2]  # 试管半径
        I2_density = random.uniform(I2_density_range[0], I2_density_range[1])
        solution_r = tube_r # 溶液半径
        # 画圆
        cv2.circle(label_I2, (tube_x, tube_y), solution_r, I2_density, -1)

    return label_I2