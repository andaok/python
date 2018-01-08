#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# -----------------
# 生成随机20个ID
# 格式: 时间戳_三位随机数字密码_8位随机小写字母
# 例：1506571959_089_xxkeabef
# -----------------

import time 
import random

id_list = []

for id in range(20):
    TimeStamp = str(int(time.time()))
    RandomPwd = ''.join([str(random.randint(0,9)) for i in range(3)])
    RandomLower = ''.join([chr(random.randint(97,122)) for _ in range(8)])
    id_list.append("%s_%s_%s"%(TimeStamp,RandomPwd,RandomLower))

print id_list

# -----------------
# 判断密码强弱
# 要求密码必须由10-15位指定字符组成：十进制数字，大写字母，小写字母，下划线
# 要求四种类型的字符都要出现才算合法的强密码
# (itwye:我理解成密码只包含十进制数字，大写字母，小写字母，下划线，不含其它字符了)
# -----------------

PwdStr = ""

def CheckPwd(PwdStr):

    flag_1_bool = False
    flag_2_bool = False
    flag_3_bool = False
    flag_4_bool = False

    IsHavingInvalidChar = False

    flag_1 = [ str(i) for i in range(10)]
    flag_2 = [ chr(97+i) for i in range(26)]
    flag_3 = [ chr(97+i).upper() for i in range(26)]
    flag_4 = ["_"]

    #print flag_1,flag_2,flag_3,flag_4

    PwdCharList = [PwdStr[i] for i in range(len(PwdStr))]

    for char in PwdCharList:

        if char in flag_1:flag_1_bool = True
        if char in flag_2:flag_2_bool = True
        if char in flag_3:flag_3_bool = True
        if char in flag_4:flag_4_bool = True

        if char in flag_1 or char in flag_2 or char in flag_3 or char in flag_4:
            continue
        else:
            IsHavingInvalidChar = True
            break
    
    if flag_1_bool and flag_2_bool and flag_3_bool and flag_4_bool and not IsHavingInvalidChar and 10 <= len(PwdStr) <= 15:
        return True
    else:
        return False

#print CheckPwd("9ZCXCX_Sc_")


# -----------------
# 判断密码强弱
# 要求密码必须由10-15位指定字符组成：十进制数字，大写字母，小写字母，下划线
# 要求四种类型的字符都要出现才算合法的强密码
# (itwye:密码必须包含十进制数字，大写字母，小写字母，下划线,可以包含其它字符)
# -----------------
    
PwdStr = ""

def CheckPwdNew(PwdStr):

    char_type_1 = [ str(i) for i in range(10)]
    char_type_2 = [ chr(97+i) for i in range(26)]
    char_type_3 = [ chr(97+i).upper() for i in range(26)]
    char_type_4 = ["_"]

    flag1,flag2,flag3,flag4 = True,True,True,True

    count = 0

    if 10 <= len(PwdStr) <= 15:

        for i in PwdStr:

            if i in char_type_1:
                if flag1:
                    count+=1
                    flag1 = False

            if i in char_type_2:
                if flag2:
                    count+=1
                    flag2 = False

            if i in char_type_3:
                if flag3:
                    count+=1
                    flag3 = False

            if i in char_type_4:
                if flag4:
                    count+=1
                    flag4 = False

        if count == 4:
            return True
        else:
            return False
    else:
        return False

print CheckPwdNew("Sc0_909090009")

# --------------------
# 日志统计:状态200的不同jsp页面访问次数
# 统计不同类型文件的访问次数，文件类型有静态类(js,css),图片类(jpg,jpeg,gif,png),动态类(action,jsp,do)
# --------------------

lst=['116.226.208.136 – – [28/Apr/2015:09:01:38 +0800] “GET /js/check.js HTTP/1.1” 304 -'
,'59.53.22.67 – – [28/Apr/2015:09:01:38 +0800] “GET /jquery/jquery.datepick.css HTTP/1.1” 304 -'
,'117.93.56.165 – – [28/Apr/2015:09:01:38 +0800] “GET /jquery/jquery-1.4.2.js HTTP/1.1” 304 -'
,'106.39.189.200 – – [28/Apr/2015:09:01:38 +0800] “GET /jquery/jquery.datepick.js HTTP/1.1” 304 -'
,'219.146.71.17 – – [28/Apr/2015:09:01:38 +0800] “GET /jquery/jquery.datepick-zh-CN.js HTTP/1.1” 304 -'
,'111.11.83.162 – – [28/Apr/2015:09:01:38 +0800] “GET /images/shim.gif HTTP/1.1” 304 -'
,'117.93.56.165 – – [28/Apr/2015:09:01:38 +0800] “GET /images/button_ok.gif HTTP/1.1” 304 -'
,'111.206.221.200 – – [28/Apr/2015:09:01:38 +0800] “GET /images/button_cancel.gif HTTP/1.1” 304 -'
,'112.80.144.85 – – [28/Apr/2015:09:01:46 +0800] “GET /user/list.jsp HTTP/1.1” 200 7644'
,'117.148.200.56 – – [28/Apr/2015:09:01:46 +0800] “GET /images/i_edit.gif HTTP/1.1” 304 -'
,'183.12.49.80 – – [28/Apr/2015:09:01:46 +0800] “GET /images/i_del.gif HTTP/1.1” 304 -'
,'175.19.57.147 – – [28/Apr/2015:09:01:46 +0800] “GET /images/button_view.gif HTTP/1.1” 304 -'
,'117.136.63.218 – – [28/Apr/2015:09:05:46 +0800] “GET /user/list.jsp HTTP/1.1” 200 7644'
,'157.55.39.102 – – [28/Apr/2015:09:05:56 +0800] “GET /login.jsp HTTP/1.1” 200 2607'
,'111.206.221.68 – – [28/Apr/2015:09:05:58 +0800] “POST /user_login.action HTTP/1.1” 200 2809'
,'117.93.56.165 – – [28/Apr/2015:09:06:12 +0800] “POST /user_login.action HTTP/1.1” 302 -'
,'223.98.218.205 – – [28/Apr/2015:09:06:12 +0800] “GET /login/home.jsp HTTP/1.1” 200 743'
,'117.136.97.78 – – [28/Apr/2015:09:06:12 +0800] “GET /login/welcome.jsp HTTP/1.1” 200 1142'
,'111.206.221.68 – – [28/Apr/2015:09:06:12 +0800] “GET /login.jsp HTTP/1.1” 200 803'
,'117.93.56.165 – – [28/Apr/2015:09:06:12 +0800] “GET /login/top.jsp HTTP/1.1” 200 2052'
,'111.206.221.68 – – [28/Apr/2015:09:06:13 +0800] “GET /login.jsp HTTP/1.1” 200 1113']


PageAccessNum = {}

print lst[0].split()

for i in lst:

    _,_,_,_,_,_,url,_,code,_ = i.split()

    if code == str(200):

        file_type = url.split(".")[1] 
        
        #print file_type

        PageAccessNum[file_type]  =  PageAccessNum.get(file_type,0) + 1

print PageAccessNum

# -------------------
# 打印矩阵外圈
# 1       2       6       7
# 3       5       8      13
# 4       9      12      14
# 10     11      15      16
# 打印顺序为1,2,6,7,13,14,16,15,11,10,4,3
# -------------------

matrix_list = [[1,2,6,7],[3,5,8,13],[4,9,12,14],[10,11,15,16]]

start_list ,middle_lists ,end_list = matrix_list[0] ,matrix_list[1:-1] ,matrix_list[-1]

top_nums = ",".join([ str(i) for i in start_list])

bottom_nums = ",".join([ str(i) for i in end_list][::-1])

middle_right_nums  = ",".join([ str(i[-1]) for i in middle_lists])

middle_left_nums = ",".join([ str(i[0]) for i in middle_lists][::-1])

matrix_outing_ring = top_nums +","+middle_right_nums + "," + bottom_nums + "," + middle_left_nums

print matrix_outing_ring
 





