#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# -------------------
# 二分查找算法
# 在有序数组中找指定的元素
# 循环法
# -------------------

arr_list = [2,27,34,23,12,56,42,102]

arr_list.sort() #[2, 12, 23, 27, 34, 42, 56, 102]

# print arr_list

# def two_split_find_cycle(key,arr_list):

#     keep_arr_list = arr_list

#     while len(keep_arr_list) > 0:

#         cmp_key_id = len(keep_arr_list)/2 
#         cmp_key = keep_arr_list[cmp_key_id]

#         if cmp_key == key:
#             return True
#         elif cmp_key > key and cmp_key_id > 1:
#             keep_arr_list = keep_arr_list[0:cmp_key_id-1] # arr_list[0:0] error
#         elif cmp_key > key and cmp_key_id == 1:
#             keep_arr_list = keep_arr_list[0:cmp_key_id]
#         else:
#             keep_arr_list = keep_arr_list[cmp_key_id+1::]

#     return False

# print two_split_find_cycle(2,arr_list)


def two_split_find_cycle(key,arr):

    start = 0
    end = len(arr) -1

    while start <= end:

        mid = start + (end - start)/2

        if arr[mid] > key:
            end = mid - 1 

        if arr[mid] < key:
            start = mid + 1

        if arr[mid] == key:
            return mid
    
    return -1

print two_split_find_cycle(27,arr_list)


# --------------------
# 二分查找算法
# 在有序数组中找指定的元素
# 递归法
# --------------------

arr_list = [2,27,34,23,12,56,42,102]

arr_list.sort() #[2, 12, 23, 27, 34, 42, 56, 102]


# def two_split_find_recursive(key,arr_list):

#     if len(arr_list) == 0:
#         return False
#     else:
#         cmp_key_id = len(arr_list)/2 
#         cmp_key = arr_list[cmp_key_id]

#         print "arr_list %s , cmp_key_id %s , cmp_key %s"%(arr_list,cmp_key_id,cmp_key)

#         if cmp_key == key:
#             return True
#         elif cmp_key > key and cmp_key_id > 1:
#             return two_split_find_recursive(key,arr_list[0:cmp_key_id])
#         elif cmp_key > key and cmp_key_id == 1:
#             return two_split_find_recursive(key,arr_list[0:cmp_key_id])
#         else:
#             return two_split_find_recursive(key,arr_list[cmp_key_id+1::])

# print two_split_find_recursive(23,arr_list)


def two_split_find_recursive(key,arr,start,end):

    if start > end:
        return -1

    #print "start %s,end %s"%(start,end)
    mid = start + (end - start)/2
    #print "mid is %s"%(mid)

    if arr[mid] > key:
        return two_split_find_recursive(key,arr,start,mid-1)
    if arr[mid] < key:
        return two_split_find_recursive(key,arr,mid+1,end)

    return mid

print two_split_find_recursive(42,arr_list,0,len(arr_list)-1)

