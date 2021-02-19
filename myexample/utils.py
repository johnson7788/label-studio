#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2021/2/19 12:05 下午
# @File  : utils.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 一些常用命令，例如启动容器，关闭容器，创建容器等待
from pycol_infos import run_command

def dockerps():
    command = "sudo docker ps"
    res = run_command(host=host,command=command)
    print(res)

def dockerpsa():
    command = "sudo docker ps -a"
    res = run_command(host=host,command=command)
    print(res)

def dockerimages():
    command = "sudo docker images"
    res = run_command(host=host,command=command)
    print(res)

def stopdocker(name):
    """
    :param name:  label8081
    :return:
    """
    command = f"sudo docker stop {name}"
    res = run_command(host=host,command=command)
    print(res)

def startdocker(name):
    """
    :param name:  label8081
    :return:
    """
    command = f"sudo docker start {name}"
    res = run_command(host=host,command=command)
    print(res)

if __name__ == '__main__':
    host= 'l3'
    dockerps()
