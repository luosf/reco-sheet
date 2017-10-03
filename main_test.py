# -*- coding: utf-8 -*-

import numpy as np
import getLeter
import matplotlib.pylab as pl
import scipy.io as so
from PIL import Image
from replaceimgTone import replaceImgTone
from noteTranslate import noteTranslate
im=Image.open(r'c:\Users\luoshengfeng\Desktop\L\jianpu\a.png')
img_gray=im.convert('L')
img_array_rgb=np.array(im.convert('RGB'))#RBG
im.close()

array_imo=np.array(img_gray)
array_img=np.array(array_imo,dtype="float64")
array_img=array_img/array_img.max()
"""
  templates
"""
templates=so.loadmat('templates.mat')['templates']

"""
  template_img_replace
"""
temp_rep=so.loadmat('template_img_replace.mat')['template_img_replace']
#notes [has_sharp, has_b, up_dot, down_dot]
letters, notes, box_locs_,box_notes=getLeter.getLetterLoc(array_img,templates)
"""
翻译
"""
toneOri='C'
toneOut='C'
letters_,notes_=noteTranslate(letters,notes,toneOri,toneOut)
#letters_ 1,2,3,4
#notes_ [has_sharp,up_dot,downdot]
"""
替换
"""

img_result=replaceImgTone(img_array_rgb,letters_,notes_,box_locs_,box_notes)
pl.imshow(img_result)
pl.show()
img_result.save('12.jpg',format='JPEG', subsampling=0, quality=100)
