# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 12:08:21 2017

@author: luoshengfeng
"""
"""
% Computes the correlation between template and input image
% and its output is a string containing the letter.
% Size of 'imagn' must be 42 x 24 pixels
% Example:
% imagn=imread('D.bmp');
% letter=read_letter(imagn)
% type: 1 识别数字  2 识别升降号
"""
# debug
import matplotlib.pylab as pl

import numpy as np
def read_letter(imagn, templates, thresh, type):
    # 归一化
    imagn = imagn / imagn.max()
    img = np.double(imagn.T.reshape(-1, 1))
    forder_col = templates[0, :]
    numbers = templates[1:, :]
    max_corl = 0
    indx_max = 0
    if type == 1:  # 识别数字
        inxstart = 0;
        inxend = np.where(forder_col == 9)[0][0]
    else:  # 识别升降号
        inxstart = np.where(forder_col == 9)[0][0]
        inxend = len(forder_col)

    for n in range(inxstart, inxend, 1):
        temp = numbers[:, n]
        temp.shape = len(temp), 1
        #corrl = np.sum(temp * img) / (np.linalg.norm(temp) * np.linalg.norm(img))# 相关系数
        corrl = np.sum(temp * img) / (np.sum(img+temp)-np.sum(temp * img))   # 杰卡德相似系数
        #print(corrl)
        if corrl > max_corl:
            max_corl = corrl
            indx_max = n

    letter = "0"
    status=False
    if max_corl < thresh:
        return letter,status

    indx_ford = forder_col[indx_max]
    #
    if indx_ford == 1:
        letter = "1"
    if indx_ford == 2:
        letter = "2"
    if indx_ford == 3:
        letter = "3"
    if indx_ford == 4:
        letter = "4"
    if indx_ford == 5:
        letter = "5"
    if indx_ford == 6:
        letter = "6"
    if indx_ford == 7:
        letter = "7"
    if indx_ford == 8:
        letter = "0"
    if indx_ford == 9:
        letter = "b"
    if indx_ford == 10:
        letter = "#"
    if indx_ford == 11:
        letter = " "  # 还原号 返回空格
    status =True
    return letter,status






