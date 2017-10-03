"""
% 根据识别到图像中的所有数据进行替换
% input:
% letters 所有数字 的矩阵 [ 1 2 3 4 5]';
% notes 数字对应的  升降号  高低音号 1[has_sharp,up_dot,down_dot]
% box_locs 数字对应的位置  1[left,right,top,bottom]
% box_notes 升、降、高音、低音  的位置[left,right,top,bottom]

%“删除”原im_input_rgb图中的 升、降、高音、低音 号
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
def replaceImgTone(im_input_rgb,letters,notes,box_locs,box_notes):

    max_pixVa=im_input_rgb.max()
    #“删除”原im_input_rgb图中的 升、降、高音、低音 号
    num=box_notes.shape[0]
    box_notes=box_notes.astype(int)
    for i in range(0,num,1):
        box_white=box_notes[i,:]
        im_input_rgb[box_white[2]-2:box_white[3]+4,box_white[0]-2:box_white[1]+1,:]=max_pixVa
    num=len(letters)

    #“删除”原im_input_rgb图中原音符位置上的字符
    box_locs=box_locs.astype(int)
    for i in range(0, num, 1):
        top = box_locs[i, 2]
        bottom = box_locs[i, 3]
        right = box_locs[i, 1]
        left = box_locs[i, 0]
        box_ori = [left, right, top, bottom]
        im_input_rgb[box_ori[2] - 2: box_ori[3] + 2, box_ori[0] - 2: box_ori[1] + 2, :]=max_pixVa
    #box_locs高度的众数
    heightbox_median=np.median(box_locs[:,3]-box_locs[:,2])

    #下面在box_locs 处添加音符
    Fontsize_Num=1.2*np.median(box_locs[:,3]-box_locs[:,2])
    Fontsize_sub=Fontsize_Num*0.7
    font_num = ImageFont.truetype("msyh.ttf", Fontsize_Num.astype(int))
    font_sub=  ImageFont.truetype("msyh.ttf", Fontsize_sub.astype(int))#arial.ttf  simhei.ttf
    #基于原图，创建绘图图像
    Image_to_draw=Image.fromarray(im_input_rgb)
    d = ImageDraw.Draw(Image_to_draw)
    for i in range(0,num,1):
        x1=box_locs[i,0]
        y1=box_locs[i,2]
        x2=box_locs[i,1]
        y2=box_locs[i,3]
        #add nums
        moveup=(y2-y1)*0.1
        if (y2-y1)<0.8*heightbox_median:
            d.text((x1,y1-moveup), str(letters[i]), font=font_sub, fill=(255, 0, 0, 255))
        else:
            d.text((x1, y1-moveup), str(letters[i]), font=font_num, fill=(255, 0, 0, 255))
        #add down_dot
        radiu_circle=(x2-x1)*0.15 #半径
        distance_down = (y2 - y1) * 1
        for j in range(0, notes[i, 2].astype(int)):
            movedown = j * radiu_circle * 2.75
            box_down_dot=((x2+x1)/2-radiu_circle,y2+distance_down-radiu_circle+movedown,(x1+x2)/2+radiu_circle,y2+distance_down+radiu_circle+movedown)
            d.ellipse(box_down_dot, fill=(255,0,0,255), outline=None)
        #add up_dot
        distance_up = radiu_circle * 2
        for j in range(0,notes[i,1].astype(int)):
            moveup = j * radiu_circle * 2.75
            box_up_dot=((x2+x1)/2-radiu_circle,y1-distance_up-radiu_circle-moveup,(x1+x2)/2+radiu_circle,y1-distance_up+radiu_circle-moveup)
            d.ellipse(box_up_dot, fill=(255, 0, 0, 255), outline=None)

        #add sharp
        if notes[i,0]>0:
            d.text((x1-0.4*(x2-x1), y1-0.2*(y2-y1)), '#', font=font_sub, fill=(255, 0, 1, 225),outline=(0, 1, 1, 225))

    return Image_to_draw