"""
%TONETRANSLATE 实现调性的转换
% noteNum,音符数字
# has_sharp,has_b,up_dot,down_dot  : 升号  降号  高音号  低音号
% toneOri 原调 如 D#
% toneOut 需要转成的调 如  C
% toneOut_img 需要转成的调的图片
% notes [noteNums,sharps,up_dot,down_dot]
"""
import numpy as np
def noteTranslate(noteNums,notes_,toneOri,toneOut):

    tones = ['.C', '.C#', '.D', '.D#', '.E', '.F', '.F#', '.G', '.G#', '.A', '.A#', '.B', # 低音
             'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B',# 中音
             'C.', 'C#.', 'D.', 'D#.', 'E.', 'F.', 'F#.', 'G.', 'G#.', 'A.', 'A#.', 'B.']# 高音

    # 转调的音程
    distance_tone = tones.index(toneOut) - tones.index(toneOri)

    letterGroup=np.array([7,6,6,5,5,4,4,3,2,2,1,1]) #数字
    sharp      =np.array([0,1,0,1,0,1,0,0,1,0,1,0]) #升号
    u          =np.array([1,1,1,1,1,1,1,1,1,1,1,1]) #高音号
    d          =np.array([1,1,1,1,1,1,1,1,1,1,1,1]) #低音
    note_flags=np.hstack((np.array([letterGroup, sharp, u * 2, d * 0]),
                          np.array([letterGroup, sharp, u * 1, d * 0]),
                          np.array([letterGroup, sharp, u * 0, d * 0]),
                          np.array([letterGroup, sharp, u * 0, d * 1]),
                          np.array([letterGroup, sharp, u * 0, d * 2]),
                          )).T
    note_flags=np.vstack((note_flags,np.array([0,0,0,0])))#添加止符
    #note_flags格式[notenum,has_shap,up_dot,down_dot]
    indx_s        =np.zeros((len(noteNums),1))
    for i in range(0,len(noteNums),1):
        up_dot  =notes_[i,2]
        down_dot=notes_[i,3]
        has_sharp=notes_[i,0]
        has_b   =notes_[i,1]
        if noteNums[i]==1:
            indx_s[i]=36-up_dot*12+down_dot*12-has_sharp+has_b
        if noteNums[i]==2:
            indx_s[i] = 34 - up_dot * 12 + down_dot * 12 - has_sharp + has_b
        if noteNums[i] == 3:
            indx_s[i] = 32 - up_dot * 12 + down_dot * 12 - has_sharp + has_b
        if noteNums[i] == 4:
            indx_s[i] = 31 - up_dot * 12 + down_dot * 12 - has_sharp + has_b
        if noteNums[i] == 5:
            indx_s[i] = 29 - up_dot * 12 + down_dot * 12 - has_sharp + has_b
        if noteNums[i] == 6:
            indx_s[i] = 27 - up_dot * 12 + down_dot * 12 - has_sharp + has_b
        if noteNums[i] == 7:
            indx_s[i] = 25 - up_dot * 12 + down_dot * 12 - has_sharp + has_b

    indx_s=indx_s+distance_tone
    #如果indx_s超出边界
    while sum(indx_s>60) and sum(indx_s<1):
        indx_s[indx_s>60]=indx_s[indx_s>60]-12
        indx_s[indx_s<1] =indx_s[indx_s<1]+12
    # 音符的还原号
    indx_s[noteNums == 0] = 61
    trans=note_flags[indx_s.astype(int)-1,:]
    trans.resize((len(indx_s),4))
    noteNums_trans=trans[:,0] # 1,2,3,4..
    notes_trans   =trans[:,1:] #[has_sharp,up_dot,downdot]



    return noteNums_trans,notes_trans

