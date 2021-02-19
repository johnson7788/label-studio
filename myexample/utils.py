#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2021/2/19 12:05 下午
# @File  : utils.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 一些常用命令，例如启动容器，关闭容器，创建容器等待
from pycol_infos import run_command

def docker_ps():
    command = "sudo docker ps"
    res = run_command(host=host,command=command)
    print(res)

def docker_psa():
    command = "sudo docker ps -a"
    res = run_command(host=host,command=command)
    print(res)

def docker_images():
    command = "sudo docker images"
    res = run_command(host=host,command=command)
    print(res)

def stop_docker(name):
    """
    :param name:  label8081
    :return:
    """
    command = f"sudo docker stop {name}"
    res = run_command(host=host,command=command)
    print(res)

def start_docker(name):
    """
    :param name:  label8081
    :return:
    """
    command = f"sudo docker start {name}"
    res = run_command(host=host,command=command)
    print(res)

def create_local_docker(name):
    """
    :param name:  label8081
    :return:
    """
    command = f"docker run -d -p 8080:8080 --name {name} label-studio:v0"
    res = run_command(host='localhost',command=command)
    print(res)

def create_local_docker_user_pass(name):
    """
    :param name:  label8081
    :return:
    """
    username = 'admin'
    password = 'sunday'
    command = f"docker run -d -p 8080:8080 -e USERNAME={username} -e PASSWORD={password} --name {name} label-studio:v0"
    res = run_command(host='localhost',command=command)
    print(res)


def create_docker(name, port=8080):
    """
    :param name:  label8080
    :return:
    """
    command = f"sudo docker run -d -p {port}:8080 --name {name} label-studio:v0"
    res = run_command(host=host,command=command)
    print(res)

def del_docker(name):
    """
    :param name:  label8080
    :return:
    """
    stop_docker(name)
    command = f"sudo docker rm {name}"
    res = run_command(host=host,command=command)
    print(res)

def create_docker_user_pass(name, port=8080):
    """
    :param name:  label8081
    :return:
    """
    username = 'admin'
    password = 'sunday'
    command = f"sudo docker run -d -p {port}:8080 -e USERNAME={username} -e PASSWORD={password} --name {name} label-studio:v0"
    res = run_command(host=host,command=command)
    print(res)


if __name__ == '__main__':
    host= 'l3'
    # create_local_docker_user_pass(name='v1')
    # start_ocker(name='label8087')
    # stop_docker(name='label8087')
    # start_docker(name='label8088')
    # del_docker(name='label8080')
    # create_docker(name='label8080')
    # stop_docker(name='label8080')
    # del_docker(name='label8089')
    # create_docker(name='label8089',port=8089)
    # del_docker(name='label8090')
    stop_docker(name='label8089')
    docker_ps()
