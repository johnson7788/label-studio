#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2021/7/9 上午10:28
# @File  : fix_json.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 对于json文件的损坏进行修复

import os
import json

def fix_json(des_dir='/Users/admin/git/label-studio/label7081'):
    """
    修复这个路径下的所有的json
    :param des_dir:
    :type des_dir:
    :return:
    :rtype:
    """
    json_files = filter_file(path=des_dir, extention=['.json'])
    for jf in json_files:
        with open(jf,'r') as f:
            try:
                json_content = json.load(f)
            except Exception as e:
                print(jf)

def filter_file(path, extention=None):
    """
    :param path: 在这个路径下搜索, 不会搜索点开头的隐藏文件,  例如.xxx
    :param extention: 只过滤到所有的包含后缀的文件, 注意必须是后缀带点['.zip','.pdf']的文件, 如果extension是None，那么返回所有文件
    :return: 列表，包含特定后缀的文件列表
    """
    allfiles = []
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if extention is None:
                allfiles.append(os.path.join(root, name))
            elif os.path.splitext(name)[-1].lower() and os.path.splitext(name)[-1].lower() in extention:
                allfiles.append(os.path.join(root, name))
    return allfiles

if __name__ == '__main__':
    fix_json()
