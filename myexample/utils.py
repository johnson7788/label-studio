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

def re_create(name):
    """
    :param name:
    :return:
    """
    port = name_port[name]
    del_docker(name)
    create_docker(name,port)

def recreate_all():
    """
    停止所有docker
    :return:
    """
    for name in name_port.keys():
        re_create(name)

def stopall():
    """
    停止所有docker
    :return:
    """
    for name in name_port.keys():
        stop_docker(name)

def startall():
    """
    停止所有docker
    :return:
    """
    for name in name_port.keys():
        start_docker(name)

def start8185():
    start_docker(name="label8081")
    start_docker(name="label8085")

if __name__ == '__main__':
    host= 'l3'
    name_port = {"label8080":8080,
                 "label8081":8081,
                 "label8082":8082,
                 "label8083": 8083,
                 "label8084": 8084,
                 "label8085": 8085,
                 "label8086": 8086,
                 "label8087": 8087,
                 "label8088": 8088,
                 "label8089": 8089,
                 }
    # create_local_docker_user_pass(name='v1')
    # start_ocker(name='label8087')
    # stop_docker(name='label8088')
    # start_docker(name='label8088')
    # del_docker(name='label8080')
    # create_docker(name='label8080')
    # stop_docker(name='label8080')
    # del_docker(name='label8089')
    # create_docker(name='label8089',port=8089)
    # del_docker(name='label8090')
    # stop_docker(name='label8089')
    # docker_ps()
    # re_create(name='label8087')
    # stopall()
    # start_docker(name='label8083')
    # start_docker(name='label8084')
    # recreate_all()
    # start8185()
    re_create(name='label8083')
    # re_create(name='label8081')
    # re_create(name='label8085')
    # stop_docker(name='label8081')
    # stop_docker(name='label8085')
