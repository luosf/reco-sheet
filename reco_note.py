"""
%RECO_ 用于识别升降号  #,b, and .
% im_gray 灰度图
% imbw 二值 图
% position_region 识别到数字的区域 [x,y,width,hight]
%imshow(im_gray(position_region(2):position_region(2)+position_region(4),position_region(1):position_region(1)+position_region(3)))
% box_notes  notes的位置[left,right,top,bottom];   没有则用[0 0 0 0]表示
%识别 是否有高音号^.   方法 ：%在region正上方判断是否有点
"""
import numpy as np
from scipy import ndimage
from scipy.misc import imresize
from read_letter import read_letter
def reco_note(im_gray,imbw,position_region,templates):
    h_up = position_region[3] * 1 / 1.5;
    box_region_up = [position_region[0] - 2, position_region[0] + position_region[2] + 3, position_region[1] - h_up,
                     position_region[1]]; # region的正上方的一个方框[left  right  top down]
    box_region_up = np.floor(box_region_up).astype(int)
    #如果框超出图像
    if box_region_up[2]<1:
        box_region_up[2]=1
    region_up = imbw[box_region_up[2]:box_region_up[3], box_region_up[0]: box_region_up[1]]
    # 判断region_up中是否有点
    num_dot, box_updot = isDot(region_up)
    up_dot = num_dot
    #将box_updot转换为相对imbw
    box_updot = box_updot + (num_dot > 0) * np.array([box_region_up[0], box_region_up[0], box_region_up[2], box_region_up[2]])
    # 识别 是否有低音号.方法 ： % 在region正下方判断是否有点
    h_dw = position_region[3] * 1.2
    #region的正下方的一个方框  [left right top down]
    box_region_down = [position_region[0] - 2, position_region[0] + position_region[2] + 3, #% left right
                       position_region[1] + position_region[3], position_region[1] + position_region[3] + h_dw] # topdown
    box_region_down = np.floor(box_region_down).astype(int)
    # 如果框超出图像
    if box_region_down[3] > imbw.shape[0] - 1:
        box_region_down[3] = imbw.shape[0]
    region_down = imbw[box_region_down[2]:box_region_down[3], box_region_down[0]: box_region_down[1]]
    #判断region_down中是否有点
    num_dot, box_downdot = isDot(region_down)
    down_dot = num_dot
    # 将box_downdot转换为相对imbw
    box_downdot = box_downdot + (num_dot > 0) * np.array([box_region_down[0], box_region_down[0], box_region_down[2], box_region_down[2]])
    #在position_region 的左上侧区域寻找
    box_region_left = np.array([position_region[0] - position_region[2] * 1.4, position_region[0] + position_region[2] * 0.55,# left, right
                       position_region[1] - position_region[3] * 1.4, position_region[1] + 0.98 * position_region[3]]) # top, botttom
    box_region_left = np.floor(box_region_left).astype(int)
    # 如果框超出图像
    box_region_left[box_region_left < 1] = 1
    region_left_gray = im_gray[box_region_left[2]:box_region_left[3], box_region_left[0]: box_region_left[1]]
    region_left_bw = imbw[box_region_left[2]:box_region_left[3], box_region_left[0]: box_region_left[1]]
    # 判断是否有升号
    has_sharp,has_b,box_note=has_sharp_b(region_left_gray,region_left_bw,templates)
    # 将box_notet转换为相对imbw
    box_note = box_note + (has_sharp > 0 or has_b > 0) *np.array( [box_region_left[0], box_region_left[0], box_region_left[2], box_region_left[2]])
    # 记录高低音点和升降号位置
    box_letter_notes=np.vstack((box_updot,box_downdot,box_note))

    return has_sharp,has_b,up_dot,down_dot,box_letter_notes



"""
# isDot(bw_region):
% 判断黑白区域是否有点
% num_dot点的个数
% box_dot 点在 bw_region 的位置[left,right,top,bottom];
"""
def isDot(bw_region):
    num_dot = 0
    box_dot = np.array([0,0,0,0])
    struct = ndimage.generate_binary_structure(2, 2)
    L, num = ndimage.label(bw_region, structure=struct)
    if num==0:
        return num_dot, box_dot
    for i in range(1,num+1,1):
        n, m = np.where(L==i)
        top = n.min()
        bottom = n.max()
        left = m.min()
        right = m.max()
        # 白色区域面积
        area = len(n)
        # 方框面积
        areabox = (bottom - top + 1) * (right - left + 1)
        #区域的长宽比
        ratio_wh = (right - left + 1) / (bottom - top + 1)
        if top < 2 or  bottom > bw_region.shape[0] - 2 or left < 2 or right > bw_region.shape[1] - 2 or ratio_wh > 3 or area < 0.35 * areabox or area<5:
            continue
        else:
            num_dot=num_dot+1
            box_dot=np.vstack((box_dot,np.array([left,right,top,bottom])))
    if num_dot>0:
        box_dot_return=box_dot[1:,:]
    else:
        box_dot_return=box_dot
    return num_dot, box_dot_return

"""
%判断黑白区域是否有升降号
% box_note 升降号在 bw_region 的位置[left,right,top,bottom];
"""
def has_sharp_b(gray_region,bw_region,templates):
    s = 0
    b = 0
    box_note=np.array([0,0,0,0])
    size_region = bw_region.shape
    struct = ndimage.generate_binary_structure(2, 2)
    L, num = ndimage.label(bw_region, structure=struct)
    if num==0:
        return s,b,box_note
    for i in range(1, num + 1, 1):
        n, m = np.where(L == i)
        top = n.min()
        bottom = n.max()
        left = m.min()
        right = m.max()
        # 白色区域面积
        area = len(n)
        # 方框面积
        areabox = (bottom - top + 1) * (right - left + 1)
        # 区域的长宽比
        ratio_wh = (right - left + 1) / (bottom - top + 1)
        if top < 2 or bottom > bw_region.shape[0] - 2 or left < 1 or right > bw_region.shape[1] - 2 \
                or area > 0.75 * areabox or (bottom - top) < 0.7 * size_region[0] / 2.3 or ratio_wh > 1.3 :
            continue
        else:
            region = gray_region[top:bottom+1, left: right+1]
            img_r = imresize(region, [42, 24], 'cubic')
            letter,status = read_letter(img_r, templates, 0.45, 2) #识别升降号
            if(status):
                if letter == '#':
                    box_note = np.array([left, right, top, bottom])
                    s = 1
                    return s,b,box_note
                if letter=='b':
                    box_note = np.array([left, right, top, bottom])
                    b=1
                    return s,b,box_note
    return s,b,box_note
