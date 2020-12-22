#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2020/12/22 10:34 上午
# @File  : use_api.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  :  使用requests调用api示例,
# 初始化项目的方法 :  label_studio/server.py start labeling_project --template text_classification --init --force --debug -b
# 启动项目: label_studio/server.py start labeling_project --debug


import requests
import json
import pprint

headers = {'content-type': 'application/json;charset=UTF-8'}
host = "http://localhost:8080/api/"
pp = pprint.PrettyPrinter(indent=4)

def setup_config():
    """
    配置项目
    :return:
    """
    data = {"label_config":
"""
<View>
  <Text name="text" value="$text"/>
  <Choices name="sentiment" toName="text" choice="single">
    <Choice value="积极"/>
    <Choice value="消极"/>
    <Choice value="中性"/>
  </Choices>
</View>
"""}
    r = requests.post(host+"project/config", data=json.dumps(data), headers=headers)
    print(r.status_code)
    print(r.text)

def get_project():
    """
    获取项目的信息
    :return:
    """
    r = requests.get(host+"project/", headers=headers)
    print(r.json())
    pp.pprint(r.json())

def get_tasks(taskid=None):
    """
    获取task, 获取数据，如果标注完成，返回标注的状态
    :param: taskid 获取第几条数据，如果为None，获取所有数据
    :return:
    """
    if taskid:
        taskid = str(taskid)
        r = requests.get(host+"tasks/"+taskid, headers=headers)
    else:
        r = requests.get(host+"tasks", headers=headers)
    print(r.json())
    pp.pprint(r.json())

def delete_tasks():
    """
    删除所有task, 数据, 同时会删除已标注的数据
    :return:
    """
    r = requests.delete(host+"tasks", headers=headers)
    print(r.status_code)
    print(r.text)

def get_completions(taskid=None):
    """
    获取完成的task，默认获取所有完成的样本，可以获取部分样本,指定taskid
    :param taskid:
    :return:  返回完成的task的id， task就是样本， {"ids":[0,1]}
    """
    if taskid:
        taskid = str(taskid)
        r = requests.get(host+"tasks/"+taskid+"/completions", headers=headers)
    else:
        r = requests.get(host+"completions", headers=headers)
    print(r.status_code)
    print(r.text)

def delete_completions():
    """
    删除所有已完成的标注样本
    :return:
    """
    r = requests.delete(host+"completions", headers=headers)
    print(r.status_code)
    print(r.text)


def import_data():
    """
    导入数据
    例如
    data = [{"text": "很好，实惠方便，会推荐朋友"},{"text": "一直买的他家这款洗发膏，用的挺好的，洗的干净也没有头皮屑"}]
    :return:
    """
    data = [{"text": "很好，实惠方便，会推荐朋友"},{"text": "一直买的他家这款洗发膏，用的挺好的，洗的干净也没有头皮屑"}, {"text": "不太顺滑"},{"text": "特别香，持久"}]
    r = requests.post(host+"project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())

def health():
    """
    测试健康
    :return:
    """
    r = requests.get(host+"health", headers=headers)
    print(r.status_code)
    print(r.text)
    r = requests.get("http://localhost:8080/version", headers=headers)
    print(r.status_code)
    print(r.text)

def list_models():
    """
    模型后端api
    :return:
    """
    r = requests.get(host+"models", headers=headers)
    print(r.status_code)
    print(r.text)


def train_model():
    """
    训练模型, 训练所有的后端模型
    label_studio 调用 label_studio_ml的  'http://localhost:9090/train'接口
    调用的post的参数
    request = {dict: 4} {'completions': [{'completions': [{'created_at': 1608617962, 'id': 1, 'lead_time': 5.162, 'result': [{'from_name': 'sentiment', 'id': '8BAF02Fcq5', 'to_name': 'text', 'type': 'choices', 'value': {'choices': ['积极']}}]}], 'data': {'text': '很好，实惠方便，会推荐朋友'}, '
     'completions' = {list: 4} [{'completions': [{'created_at': 1608617962, 'id': 1, 'lead_time': 5.162, 'result': [{'from_name': 'sentiment', 'id': '8BAF02Fcq5', 'to_name': 'text', 'type': 'choices', 'value': {'choices': ['积极']}}]}], 'data': {'text': '很好，实惠方便，会推荐朋友'}, 'id': 0}, {'completions': [{'created_at': 1608617965, 'id': 1001, 'lead_time': 3.101, 'result': [{'from_name': 'sentiment', 'id': 'UvcGY6ZCM7', 'to_name': 'text', 'type': 'choices', 'value': {'choices': ['中性']}}]}], 'data': {'text': '一直买的他家这款洗发膏，用的挺好的，洗的干净也没有头皮屑'}, 'id': 1}, {'completions': [{'created_at': 1608617968, 'id': 2001, 'lead_time': 2.085, 'result': [{'from_name': 'sentiment', 'id': 'h1qNhxHSyQ', 'to_name': 'text', 'type': 'choices', 'value': {'choices': ['消极']}}]}], 'data': {'text': '不太顺滑'}, 'id': 2}, {'completions': [{'created_at': 1608617970, 'id': 3001, 'lead_time': 2.583, 'result': [{'from_name': 'sentiment', 'id': 'V0Q1xEHQQX', 'to_name': 'text', 'type': 'choices', 'value': {'choices': ['积极']}}]}], 'data': {'text': '特别香，持久'}, 'id': 3}]
     'project' = {str} 'text_classification_project1a43'
     'label_config' = {str} '<View>  <Text name="text" value="$text"/>  <Choices name="sentiment" toName="text" choice="single">    <Choice value="积极"/>    <Choice value="消极"/>    <Choice value="中性"/>  </Choices></View>'
     'params' = {dict: 3} {'login': '', 'password': '', 'project_full_path': '/Users/admin/git/label-studio/text_classification_project'}
     __len__ = {int} 4
    :return:
    """
    r = requests.post(host+"models/train", headers=headers)
    print(r.status_code)
    print(r.text)

if __name__ == '__main__':
    # setup_config()
    # get_project()
    # import_data()
    # get_tasks()
    # get_tasks(taskid=1)
    # delete_tasks()
    # get_completions()
    # health()
    # list_models()
    train_model()
