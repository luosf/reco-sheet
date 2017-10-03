# -*- coding: utf-8 -*-
"""
"""
from scipy import ndimage
from scipy.misc import imresize
import numpy as np
from read_letter import read_letter
from reco_note import reco_note


def getLetterLoc(im_input_gray, templates):
    im_bw = (im_input_gray > 0.7)
    # 黑白反转
    im_input_gray = 1 - im_input_gray
    im_bw = (im_bw == 0)
    im_bw_or = im_bw  # 用来对点进行识别
    im_bw, Y_section = remove_noise_getSection(im_bw)
    struct = ndimage.generate_binary_structure(2, 2)
    L, num = ndimage.label(im_bw, structure=struct)  # 这里
    letters = np.zeros((num, 1))
    notes = np.zeros((num, 4))
    box_locs = np.zeros((num, 4))
    box_notes = np.zeros((1, 4))

    # 针对每一个连通区域
    k = -1;
    # 记录每个识别区域的大小
    for i in range(1, num + 1, 1):
        SELECTOR = (L == i)
        n, m = np.where(SELECTOR)
        top = n.min()
        bottom = n.max()
        left = m.min()
        right = m.max()
        # 判断识别到的数字是否在小节线内 Y_section
        if Y_section[int(np.floor(bottom * 4 / 5 + top * 1 / 5))] == 0 and np.sum(Y_section) > 0.05 * len(Y_section):
            continue
        # 识别
        region = im_input_gray[top:bottom + 1, left:right + 1]
        # 识别数字 (same size of template)
        img_r = imresize(region, [42, 24], 'cubic')
        noteNum, status = read_letter(img_r, templates, 0.4, 1)  # 识别数字  返回 字符
        if (status):
            L[L == i] = 1
            k = k + 1
            position_region = [left, top, right - left, bottom - top]  # [x y w h]
            # 识别升降号  #,b, and .  并获得其位置box_letter_notes  [left,right,top,bottom];   没有则用[0 0 0 0]表示
            # [has_sharp, has_b, up_dot, down_dot, box_letter_notes]
            has_sharp, has_b, up_dot, down_dot, box_letter_notes = reco_note(im_input_gray, im_bw_or,
                                                                             position_region,
                                                                             templates)
            letters[k] = int(noteNum)
            notes[k, :] = np.array([has_sharp, has_b, up_dot, down_dot])
            box_locs[k, :] = np.array([left, right, top, bottom])
            box_notes = np.vstack((box_notes, box_letter_notes))
        else:
            L[L == i] = 0

    # 删除box_notes中的0数据
    inx, iny = np.where(box_notes == 0)
    box_notes = np.delete(box_notes, inx, axis=0)

    letters = letters[0:k + 1]
    notes = notes[0:k + 1, :]
    box_locs = box_locs[0:k + 1, :]
    # 删除部分错误识别部分
    size_im = im_input_gray.shape[0:2]
    [letters_, notes_, box_locs_] = removeMistaken(letters, notes, box_locs, size_im)
    return letters_, notes_, box_locs_, box_notes


"""
% 删除box_locs中高度异常的数据
% 所有box_locs（识别到的数字）的高度
"""


def removeMistaken(letters, notes, box_locs, size_im):
    Height_box_locs = box_locs[:, 3] - box_locs[:, 2]
    medianH = np.median(Height_box_locs)  # 中位数
    # 删除太高的 和太低的
    logical_select1 = np.array(Height_box_locs < (1.2 * medianH)) * np.array(Height_box_locs > (0.32 * medianH))
    # 如果box_locs位置太靠近图像上下左右边界
    logical_select2 = np.array(box_locs[:, 3] < size_im[0] - 0.8 * medianH) * np.array(
        box_locs[:, 2] > medianH + 5) * np.array(box_locs[:, 0] > 0.8 * medianH - 5);
    logical_select = logical_select1 * logical_select2
    letters_ = letters[logical_select]
    notes_ = notes[logical_select, :]
    box_locs_ = box_locs[logical_select, :]

    return letters_, notes_, box_locs_


"""

"""


def remove_noise_getSection(bwim_input: object) -> object:
    struct = ndimage.generate_binary_structure(2, 2)
    L, num = ndimage.label(bwim_input, structure=struct)
    bwim_sectionLine = np.zeros(L.shape)
    bwim_output = np.zeros(L.shape)
    Height_section = np.zeros((num, 1))  # 记录小节线高度
    ks = 1
    Height_zone = np.zeros((num, 1))  # %记录区域高度
    bwim_Letter = np.zeros(L.shape)  # %记录文字区域
    kz = 1

    for i in range(1, num + 1, 1):
        # 区域范围
        SELECTOR = (L == i)
        n, m = np.where(SELECTOR)
        top = n.min()
        bottom = n.max()
        left = m.min()
        right = m.max()
        # 区域长宽比
        ratio_wh = (right - left + 1) / (bottom - top + 1)
        ratio_hw = 1 / ratio_wh
        # 白色区域面积
        area = len(n)
        # 方框面积
        areabox = (bottom - top + 1) * (right - left + 1)
        # 为获得Y
        if (area > 0.75 * areabox and ratio_hw > 7) or (ratio_hw > 9):  # 识别为小节线
            Height_section[ks] = bottom - top
            bwim_sectionLine[SELECTOR] = Height_section[ks]
            ks = ks + 1

        # 为获得bwim_output
        if ratio_wh > 1.34 or area > 0.9 * areabox or ratio_hw > 6.6 or bottom - top < 5 or right - left < 3 or left < (
                    right - left) or right > ((bwim_input.shape[1]) - (right - left + 2)):
            continue
        else:
            Height_zone[kz] = bottom - top
            bwim_output[SELECTOR] = Height_zone[kz]
            kz = kz + 1

    Height_section = Height_section[0:ks]
    # 小节线高度的均值
    sectionHeigh_mean = Height_section.mean()
    # 小节线高度的方差
    sectionHeight_std = Height_section.std()
    # 过滤小节线图中的中的噪点  当高度小于一定值时 mean-3*std
    bwim_sectionLine[bwim_sectionLine < (sectionHeigh_mean - 3 * sectionHeight_std)] = 0
    Y_section = (bwim_sectionLine.sum(1) > 1)
    zoneHeight_median = np.median(Height_zone[0:kz])
    bwim_output[bwim_output < zoneHeight_median * 0.25] = 0
    bwim_output[bwim_output > 0] = 1
    return bwim_output, Y_section
