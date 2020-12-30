#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2020/12/22 10:34 上午
# @File  : use_api.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  :  比较复杂的ABSA，根据关键字进行情感分类的api
# 初始化项目的方法 :  label_studio/server.py start labeling_project --template text_classification --init --force --debug -b
# 启动项目: label_studio/server.py start labeling_project --debug


import requests
import json
import pprint
import os
import hashlib

headers = {'content-type': 'application/json;charset=UTF-8'}
host = "http://localhost:8080/api/"
pp = pprint.PrettyPrinter(indent=4)


def setup_config():
    """
    配置项目, 判断给定关键字的情感
    :return:
    """
    data = {"label_config":
"""
<View>
  <View style="flex: 30%; color:red">
    <Header value="关键字" />
    <Text name="keyword" value="$keyword"/>
  </View>
  <View style="flex: 30%">
      <Labels name="label" toName="text">
        <Label value="积极" background="red"></Label>
        <Label value="消极" background="darkorange"></Label>
        <Label value="中性" background="green"></Label>
      </Labels>
      <Text name="text" value="$text"></Text>
  </View>
</View>
"""}
    r = requests.post(host + "project/config", data=json.dumps(data), headers=headers)
    print(r.status_code)
    print(r.text)


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


def delete_tasks():
    """
    删除所有task, 数据, 同时会删除已标注的数据
    :return:
    """
    r = requests.delete(host + "tasks", headers=headers)
    print("完成，返回code:")
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
        r = requests.get(host + "tasks/" + taskid + "/completions", headers=headers)
    else:
        r = requests.get(host + "completions", headers=headers)
    print(r.status_code)
    print(r.text)


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
    data = [{"text": "很好，实惠方便，会推荐朋友", "channel":"jd", "keyword":""},{"text": "一直买的他家这款洗发膏，用的挺好的，洗的干净也没有头皮屑"}]
    :return:
    """
    data = [{'channel': 'jd', 'keyword': '芦荟', 'md5': '503d422e3c12b9bf33d5833a84aea219',
      'text': '套装设计很贴心，效果是不错的。芦荟镇定效果可以，刺鼻味是有的。操作容易-效果不错。缺点是漂色不到半月，颜色又开始悄咪咪的恢复了，估计2-3周要做一次。仅个人经验。', 'wordtype': '成分'},
     {'channel': 'jd', 'keyword': '海藻', 'md5': 'ec57fe5052e5304e4dccb05f438e3c0b', 'text': '孕期的时候就使用它家的海藻面膜，挺好用的',
      'wordtype': '成分'},
     {'channel': 'jd', 'keyword': '控油', 'md5': 'f3d1857051db73f637255f0db14686d0', 'text': '泡沫数量：666666产品香味：麝香控油效果：#',
      'wordtype': '功效'},
     {'channel': 'jd', 'keyword': '麝香', 'md5': 'b1d0dda097bdb011e7cb19887e51c89b', 'text': '泡沫数量：666666产品香味：麝香控油效果：#',
      'wordtype': '成分'}, {'channel': 'jd', 'keyword': '保湿', 'md5': 'f40089e74b1cf93dac1fbb2d1589fb36',
                          'text': '这是第三购买了，碰上京东七夕活动也趁机买下，原来虽然还没有用完，因为活动就多囤点，面膜总是要用的反正，一直买的是这个牌子，用起来还是很放心的，没有酒精味，保湿效果很好，就是价钱小贵了些，如果平时再优惠点就更好了，不过这次没有送有点遗憾。',
                          'wordtype': '功效'},
     {'channel': 'jd', 'keyword': '酒精', 'md5': '11187ff91e2cea54bebba96d3b265e92',
      'text': '这是第三购买了，碰上京东七夕活动也趁机买下，原来虽然还没有用完，因为活动就多囤点，面膜总是要用的反正，一直买的是这个牌子，用起来还是很放心的，没有酒精味，保湿效果很好，就是价钱小贵了些，如果平时再优惠点就更好了，不过这次没有送有点遗憾。',
      'wordtype': '成分'}, {'channel': 'jd', 'keyword': '没有酒精', 'md5': '83d8fa49556003e9e2662f8f410c7865',
                          'text': '这是第三购买了，碰上京东七夕活动也趁机买下，原来虽然还没有用完，因为活动就多囤点，面膜总是要用的反正，一直买的是这个牌子，用起来还是很放心的，没有酒精味，保湿效果很好，就是价钱小贵了些，如果平时再优惠点就更好了，不过这次没有送有点遗憾。',
                          'wordtype': '成分'},
     {'channel': 'jd', 'keyword': '质感', 'md5': 'd1549cc845f00afcb2e200377d296444',
      'text': '产品质感：打开一股特殊的味道，有点像酒精味，也有点像发酵的味道适合肤质：适合肤质：适合 敏感肌使用补水效果：补水效果不错。贴合效果：面膜大小正好，贴合面部非常好使用感受：总体来说还可以。本人敏感皮肤，用着不错',
      'wordtype': '功效'}, {'channel': 'jd', 'keyword': '补水', 'md5': 'e09d37df17e5d972d46f57c11950e4e4',
                          'text': '产品质感：打开一股特殊的味道，有点像酒精味，也有点像发酵的味道适合肤质：适合肤质：适合 敏感肌使用补水效果：补水效果不错。贴合效果：面膜大小正好，贴合面部非常好使用感受：总体来说还可以。本人敏感皮肤，用着不错',
                          'wordtype': '功效'},
     {'channel': 'jd', 'keyword': '酒精', 'md5': 'cec263f850791af51fc447f701a076e5',
      'text': '产品质感：打开一股特殊的味道，有点像酒精味，也有点像发酵的味道适合肤质：适合肤质：适合 敏感肌使用补水效果：补水效果不错。贴合效果：面膜大小正好，贴合面部非常好使用感受：总体来说还可以。本人敏感皮肤，用着不错',
      'wordtype': '成分'}]

    r = requests.post(host + "project/import", data=json.dumps(data), headers=headers)
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
            #说明不存在md5这个字段，开始计算
            content = data['keyword'] + data['text']
            md5_value = cal_md5(content=content)
        md5_list.append(md5_value)
    return md5_list

def import_absa_data(channel=['jd','tmall'],number=10):
    """
    导入情感分析数据, 从hive数据库中导入, 导入到label-studio前，需要检查下这条数据是否已经导入过
    12月份，功效4000条，其它维度各1500条
    :param number:
    :return:
    """
    leibie = ['成分', '功效', '香味', '包装', '肤感']
    from read_hive import get_absa_corpus
    #要导入的数据
    valid_data = []
    #已经导入的数据, 注意更改获取的样本数目，默认是5000条
    imported_data = get_tasks(page_size=5000)
    imported_data_md5 = get_imported_data_md5(imported_data)
    #开始从hive数据库拉数据
    data = get_absa_corpus(channel=['jd','tmall'], requiretags=None, number=10)
    # 获取到的data数据进行排查，如果已经导入过了，就过滤掉
    for one_data in data:
        content = one_data['keyword'] + one_data['text']
        data_md5 = cal_md5(content)
        if data_md5 in imported_data_md5:
            # 数据已经导入到label-studio过了，不需要重新导入
            continue
        else:
            # 没有导入过label-studio，那么加入到valid_data，进行导入
            # 设置md5字段，方便以后获取
            one_data['md5'] = data_md5
            valid_data.append(one_data)
    print(f"可导入的有效数据是{len(valid_data)}, 有重复数据{len(data)-len(valid_data)} 是无需导入的")
    if not valid_data:
        #如果都是已经导入过的数据，直接放弃导入
        return
    r = requests.post(host + "project/import", data=json.dumps(valid_data), headers=headers)
    pp.pprint(r.json())
    print(f"共导入数据{len(valid_data)}条")
def import_absa_data_host(channel=['jd','tmall'],number=10, hostname=None):
    """
    按比例导入不同的host, 导入情感分析数据, 从hive数据库中导入, 导入到label-studio前，需要检查下这条数据是否已经导入过
    12月份，功效4000条，其它维度各1500条
    :param number:
    :param hostname:平均导入每个host中,列表或None
    :return:
    """
    leibie = ['成分', '功效', '香味', '包装', '肤感']
    from read_hive import get_absa_corpus
    #要导入的数据
    valid_data = []
    #已经导入的数据, 注意更改获取的样本数目，默认是5000条
    if hostname != None:
        host = hostname
    imported_data = []
    for h in host:
        host_imported_data = get_tasks(page_size=5000,hostname=h)
        imported_data.extend(host_imported_data)
    imported_data_md5 = get_imported_data_md5(imported_data)
    #开始从hive数据库拉数据
    data = get_absa_corpus(channel=['jd','tmall'], requiretags=None, number=10)
    # 获取到的data数据进行排查，如果已经导入过了，就过滤掉
    for one_data in data:
        content = one_data['keyword'] + one_data['text']
        data_md5 = cal_md5(content)
        if data_md5 in imported_data_md5:
            # 数据已经导入到label-studio过了，不需要重新导入
            continue
        else:
            # 没有导入过label-studio，那么加入到valid_data，进行导入
            # 设置md5字段，方便以后获取
            one_data['md5'] = data_md5
            valid_data.append(one_data)
    print(f"可导入的有效数据是{len(valid_data)}, 有重复数据{len(data)-len(valid_data)} 是无需导入的")
    if not valid_data:
        #如果都是已经导入过的数据，直接放弃导入
        return
    every_host_number = int(len(valid_data) /len(host))
    print(f"每个主机导入数据{every_host_number}")
    vdatas = [valid_data[i:i + every_host_number] for i in range(0, len(valid_data), every_host_number)]
    for h, vdata in zip(host,vdatas):
        r = requests.post(h + "project/import", data=json.dumps(vdata), headers=headers)
        pp.pprint(r.json())
        print(f"共导入主机host{h}中数据{len(vdata)}条")

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
    print(f"共有重复数据{len(datas)-len(not_repeat_data)}条")
if __name__ == '__main__':
    # check_data()
    setup_config()
    # get_project()
    # import_data()
    # get_tasks()
    # get_tasks(taskid=0)
    # delete_tasks()
    # get_completions()
    # delete_completions()
    # health()
    # list_models()
    # train_model()
    # predict_model()
    # import_absa_data_host(channel=['jd','tmall'],number=10, hostname=["http://localhost:8080/api/"])
