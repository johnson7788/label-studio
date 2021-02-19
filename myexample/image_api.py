#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2020/12/22 10:34 上午
# @File  : use_api.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  :  图像的目标检测的标注


import requests
import json
import pprint
import os
import hashlib
import time
import re
import zipfile

headers = {'content-type': 'application/json;charset=UTF-8'}
host = "http://localhost:8080/api/"
localhost = "http://localhost:8080/api/"
pp = pprint.PrettyPrinter(indent=4)


def setup_config(hostname=None):
    """
    配置项目, 判断给定关键字的情感
    :return:
    """
    data = {"label_config":
                """
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="表格" background="green"/>
    <Label value="图像" background="blue"/>
    <Label value="公式" background="red"/>
  </RectangleLabels>
</View>
                """}
    if hostname != None:
        host = hostname
    r = requests.post(host + "project/config", data=json.dumps(data), headers=headers)
    print(r.status_code)
    print(r.text)


def setup_config_host(hostnames):
    """
    删除所有task, 数据, 同时会删除已标注的数据
    :param hostnames: 要设置的hostname
    :return:
    """
    for hostname in hostnames:
        setup_config(hostname=hostname)


def get_project():
    """
    获取项目的信息
    :return:
    """
    r = requests.get(host + "project/", headers=headers)
    print(r.json())
    pp.pprint(r.json())


def get_tasks(taskid=None, page_size=5000, hostname=None):
    """
    获取task, 获取数据，如果标注完成，返回标注的状态
    :param: taskid 获取第几条数据，如果为None，获取所有数据
    :return:
    """
    if hostname != None:
        host = hostname
    if taskid:
        taskid = str(taskid)
        r = requests.get(host + "tasks/" + taskid, headers=headers)
    else:
        payload = {'fields': 'all', 'page': 1, 'page_size': page_size, 'order': 'id'}
        r = requests.get(host + "tasks", params=payload, headers=headers)
    print(r.json())
    pp.pprint(r.json())
    results = r.json()
    return results


def get_tasks_host(hostnames):
    """
    删除所有task, 数据, 同时会删除已标注的数据
    :return:
    """
    for hostname in hostnames:
        get_tasks(hostname=hostname)


def delete_tasks(hostname, taskid=None):
    """
    如果taskid=None删除所有task, 数据, 同时会删除已标注的数据
    :return:
    """
    if taskid:
        taskid = str(taskid)
        r = requests.delete(hostname + "tasks/" + taskid, headers=headers)
    else:
        r = requests.delete(hostname + "tasks", headers=headers)
    print("完成，返回code:")
    print(r.status_code)
    print(r.text)


def delete_tasks_host(hostnames):
    """
    删除所有task, 数据, 同时会删除已标注的数据
    :return:
    """
    for hostname in hostnames:
        delete_tasks(hostname)


def get_completions(taskid=None, hostname=None, proxy=False):
    """
    获取完成的task，默认获取所有完成的样本，可以获取部分样本,指定taskid
    :param taskid:
    :return:  返回完成的task的id， task就是样本， {"ids":[0,1]}
    """
    if hostname != None:
        host = hostname
    if taskid:
        taskid = str(taskid)
        if proxy:
            r = requests.get(host + "tasks/" + taskid + "/completions", headers=headers,
                             proxies=dict(http='socks5://127.0.0.1:9080', https='socks5://127.0.0.1:9080'))
        else:
            r = requests.get(host + "tasks/" + taskid + "/completions", headers=headers)
    else:
        if proxy:
            r = requests.get(host + "completions", headers=headers,
                             proxies=dict(http='socks5://127.0.0.1:9080', https='socks5://127.0.0.1:9080'))
        else:
            r = requests.get(host + "completions", headers=headers)
    # print(r.status_code)
    # print(r.text)
    complete_ids = r.json()["ids"]
    print(f"{host}  标注完成{len(complete_ids)}条")
    return len(complete_ids)


def get_completions_host(hostnames):
    """
    删除所有task, 数据, 同时会删除已标注的数据
    :return:
    """
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
    total = 0
    for hostname in hostnames:
        complete_num = get_completions(hostname=hostname)
        total += complete_num
    print(f"总共已完成{total}条数据标注")


def delete_completions():
    """
    删除所有已完成的标注样本
    :return:
    """
    r = requests.delete(host + "completions", headers=headers)
    print(r.status_code)
    print(r.text)


def import_data():
    """
    导入字典里面包含多个key和value的格式
    例如
    data = xxxx
    :return:
    """
    data = [{'image': 'http://127.0.0.1:9090/IMG_1505.JPG'},
            {'image': 'http://127.0.0.1:9090/IMG_1506.JPG'}]

    r = requests.post(host + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())

def import_dir_data(hostname, url):
    """
    导入字典里面包含多个key和value的格式
    例如
    data = xxxx
    :param hostname: label-studio hostname
    :param url: http目录，里面包含要训练的图片的下载地址
    :return:
    """
    data = []
    r = requests.get(url)
    text = r.text
    # <li><a href="ALBERT_A-17.jpg">ALBERT_A-17.jpg</a></li>
    results = re.findall("<li><a href=.*>(.*)</a></li>", text)
    for name in results:
        image = os.path.join(url, name)
        one_data = {}
        one_data['image'] = image
        data.append(one_data)
    print(f"共收集图片{len(data)}张")
    r = requests.post(hostname + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())


def health():
    """
    测试健康
    :return:
    """
    r = requests.get(host + "health", headers=headers)
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
    r = requests.get(host + "models", headers=headers)
    print(r.status_code)
    print(r.text)


def train_model():
    """
    训练模型, 训练所有的后端模型, 只有在有新的标注后，才调用后端自定义的fit接口，没有新的标注，就不调用后端的fit训练模型
    例如：调用absa_classifier.py的ABSATextClassifier类的init，然后调用fit
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
    r = requests.post(host + "models/train", headers=headers)
    print(r.status_code)
    print(r.text)


def predict_model():
    """
    调用模型的预测接口, 首先调用自定义的分了器，例如absa_classifier.py的init，然后对所有tasks进行调用absa_classifier.py的predict进行预测
    /api/models/predictions?mode={data|all_tasks}
    :return: eg: {"details":"predictions are ready"}
    """
    r = requests.post(host + "models/predictions?mode=all_tasks", headers=headers)
    print(r.status_code)
    print(r.text)


def cal_md5(content):
    """
    计算content字符串的md5
    :param content:
    :return:
    """
    # 使用encode
    result = hashlib.md5(content.encode())
    # 打印hash
    md5 = result.hexdigest()
    return md5


def get_imported_data_md5(imported_data):
    """
    对已经导入的数据，计算所有md5，如果data['md5']存在，直接过去，否则用keyword+text计算md5
    :return: 按列表顺序返回md5的列表[]
    """
    md5_list = []
    for res in imported_data:
        data = res['data']
        md5_value = data.get('md5')
        if not md5_value:
            # 说明不存在md5这个字段，开始计算
            content = data['keyword'] + data['text']
            md5_value = cal_md5(content=content)
        md5_list.append(md5_value)
    return md5_list


def check_data():
    """
    查看下已导入的数据
    :return:
    """
    datas = get_tasks()
    not_repeat_id = []
    not_repeat_data = []
    for data in datas:
        content = data['data']['keyword'] + data['data']['text']
        if content not in not_repeat_data:
            not_repeat_data.append(content)
            not_repeat_id.append(data['id'])
        else:
            repeat_idx = not_repeat_data.index(content)
            repeat_id = not_repeat_id[repeat_idx]
            print(f"发现重复数据:{data['id']}和{repeat_id}")
    print(f"共有重复数据{len(datas) - len(not_repeat_data)}条")


def export_data(hostname=None, dirpath="/opt/labeled_pdf/", jsonfile=None, proxy=False, format='COCO'):
    """
    导出数据
    :param hostname:
    :return:
    """
    if hostname != None:
        host = hostname
    # 获取下标注完成了多少了数据
    get_completions(hostname=host, proxy=proxy)
    p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
    m = re.search(p, host)
    hostip = m.group('host')
    port = m.group('port')
    url = host + f"project/export?format={format}"
    local_zipfile = hostip + "_" + port + "_" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".zip"
    local_zipfile = os.path.join(dirpath, local_zipfile)
    if proxy:
        with requests.get(url, stream=True,
                          proxies=dict(http='socks5://127.0.0.1:9080', https='socks5://127.0.0.1:9080')) as r:
            r.raise_for_status()
            with open(local_zipfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    else:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_zipfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    # 创建一个压缩包对象
    parent_archive = zipfile.ZipFile(local_zipfile)
    # 解压
    parent_archive.extractall(dirpath)
    # 获取文件夹的压缩包列表
    namelist = parent_archive.namelist()
    files = [dirpath + name for name in namelist]
    parent_archive.close()
    os.remove(local_zipfile)
    print(f"{host}: 下载完成{local_zipfile}, 解压到{files}")
    return files


def export_data_host(hostnames, dirpath="/opt/labeled_pdf/", format='COCO'):
    """
    导出所有标注完的数据
    :return:
    """
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
    for hostname in hostnames:
        export_data(hostname=hostname, dirpath=dirpath, format=format)


def conver2image(dir_path='/Users/admin/Documents/papers/', output_folder='/opt/pdfimages'):
    """
    pdf文件转换成图片文件
    :param dir_path: 路径，自动搜索路径下的pdf文件
    :param output_folder: 图片保存的路径，保存到文件夹下
    :return:
    """
    from pdf2image import convert_from_path
    from pathlib import Path
    for pdf_path in Path(dir_path).rglob('*.pdf'):
        base_name_without_ext = os.path.splitext(pdf_path.name)[0]
        images = convert_from_path(pdf_path=pdf_path, output_folder=output_folder,
                                   fmt='jpeg', output_file=base_name_without_ext)
        images_name = [i.filename for i in images]
        print(f'{pdf_path}保存成功到{images_name}')


if __name__ == '__main__':
    # check_data()
    # get_project()
    # get_tasks()
    # get_tasks(taskid=0)
    # delete_tasks(hostname="http://192.168.50.119:8090/api/")
    # get_completions()
    # delete_completions()
    # health()
    # list_models()
    # train_model()
    # predict_model()
    # hostnames = ["http://192.168.50.139:8087/api/"]
    # hostnames = ["http://192.168.50.139:8080/api/", "http://192.168.50.139:8081/api/"]
    # hostnames = ["http://192.168.50.139:8081/api/"]
    hostnames = ["http://127.0.0.1:8080/api/"]
    # import_absa_data_host(channel=['jd','tmall'],number=50, hostname=hostnames)
    # hostnames = ["http://192.168.50.119:8080/api/", "http://192.168.50.119:8081/api/"]
    # setup_config_host(hostnames=hostnames)
    # get_tasks_host(hostnames=hostnames)
    # get_completions_host(hostnames=hostnames)
    # export_data(hostname="http://192.168.50.119:8090/api/")
    export_data_host(hostnames=hostnames, dirpath="/opt/labeled_pdf/")
    # delete_tasks_host(hostnames=hostnames)
    # import_data()
    # conver2image(dir_path='/Users/admin/Documents/sentiment')
    # import_dir_data(hostname=hostnames[0], url='http://127.0.0.1:9090/')
