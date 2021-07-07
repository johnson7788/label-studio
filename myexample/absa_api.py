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
  <View style="flex: 30%; color:red">
    <Header value="$wordtype" />
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
    if hostname != None:
        host = hostname
    r = requests.post(host + "project/config", data=json.dumps(data), headers=headers)
    print(r.status_code)
    print(r.text)
def setup_ner_config(hostname=None):
    """
    ner分类的config
    :return:
    """
    data = {"label_config":
                """
<View>
  <View style="flex: 30%">
      <Labels name="label" toName="text">
        <Label value="成分" background="red"></Label>
        <Label value="功效" background="darkorange"></Label>
        <Label value="香味" background="green"></Label>
        <Label value="包装" background="blue"></Label>
        <Label value="肤感" background="purple"></Label>
        <Label value="其它" background="black"></Label>
      </Labels>
      <Text name="text" value="$text"></Text>
  </View>
</View>
                """}
    if hostname != None:
        host = hostname
    r = requests.post(host + "project/config", data=json.dumps(data), headers=headers)
    print(r.status_code)
    print(r.text)


def setup_config_host(hostnames, absa=True):
    """
    删除所有task, 数据, 同时会删除已标注的数据
    :param hostnames: 要设置的hostname
    :param absa: 要设置absa还是ner的配置
    :return:
    """
    for hostname in hostnames:
        if absa:
            setup_config(hostname=hostname)
        else:
            setup_ner_config(hostname=hostname)


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
        r = requests.get(host + "tasks/" + taskid, data=json.dumps({'filters':None}), headers=headers)
    else:
        payload = {'fields': 'all', 'page': 1, 'page_size': page_size, 'order': 'id'}
        r = requests.get(host + "tasks", params=payload, data=json.dumps({'filters':None}), headers=headers)
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
    data = [{"text": "很好，实惠方便，会推荐朋友", "channel":"jd", "keyword":""},{"text": "一直买的他家这款洗发膏，用的挺好的，洗的干净也没有头皮屑"}]
    :return:
    """
    data = [{'channel': 'jd', 'keyword': '芦荟', 'md5': '503d422e3c12b9bf33d5833a84aea219',
             'text': '套装设计很贴心，效果是不错的。芦荟镇定效果可以，刺鼻味是有的。操作容易-效果不错。缺点是漂色不到半月，颜色又开始悄咪咪的恢复了，估计2-3周要做一次。仅个人经验。',
             'wordtype': '成分'},
            {'channel': 'jd', 'keyword': '海藻', 'md5': 'ec57fe5052e5304e4dccb05f438e3c0b',
             'text': '孕期的时候就使用它家的海藻面膜，挺好用的',
             'wordtype': '成分'},
            {'channel': 'jd', 'keyword': '控油', 'md5': 'f3d1857051db73f637255f0db14686d0',
             'text': '泡沫数量：666666产品香味：麝香控油效果：#',
             'wordtype': '功效'},
            {'channel': 'jd', 'keyword': '麝香', 'md5': 'b1d0dda097bdb011e7cb19887e51c89b',
             'text': '泡沫数量：666666产品香味：麝香控油效果：#',
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
            # 说明不存在md5这个字段，开始计算
            content = data['keyword'] + data['text']
            md5_value = cal_md5(content=content)
        md5_list.append(md5_value)
    return md5_list


def import_absa_data(channel=['jd', 'tmall'], number=10):
    """
    导入情感分析数据, 从hive数据库中导入, 导入到label-studio前，需要检查下这条数据是否已经导入过
    12月份，功效4000条，其它维度各1500条
    :param number:
    :return:
    """
    leibie = ['成分', '功效', '香味', '包装', '肤感']
    from read_hive import get_absa_corpus
    # 要导入的数据
    valid_data = []
    # 已经导入的数据, 注意更改获取的样本数目，默认是5000条
    imported_data = get_tasks(page_size=5000)
    imported_data_md5 = get_imported_data_md5(imported_data)
    # 开始从hive数据库拉数据
    data = get_absa_corpus(channel=['jd', 'tmall'], requiretags=None, number=10)
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
    print(f"可导入的有效数据是{len(valid_data)}, 有重复数据{len(data) - len(valid_data)} 是无需导入的")
    if not valid_data:
        # 如果都是已经导入过的数据，直接放弃导入
        return
    r = requests.post(host + "project/import", data=json.dumps(valid_data), headers=headers)
    pp.pprint(r.json())
    print(f"共导入数据{len(valid_data)}条")


def import_absa_data_host(channel=['jd', 'tmall'], number=10, hostname=None):
    """
    按比例导入不同的host, 导入情感分析数据, 从hive数据库中导入, 导入到label-studio前，需要检查下这条数据是否已经导入过
    12月份，功效4000条，其它维度各1500条
    :param number:
    :param hostname:平均导入每个host中,列表或None
    :return:
    """
    leibie = ['成分', '功效', '香味', '包装', '肤感']
    from read_hive import get_absa_corpus
    # 要导入的数据
    valid_data = []
    # 已经导入的数据, 注意更改获取的样本数目，默认是5000条
    if hostname != None:
        host = hostname
    imported_data = []
    for h in host:
        host_imported_data = get_tasks(page_size=5000, hostname=h)
        imported_data.extend(host_imported_data)
    imported_data_md5 = get_imported_data_md5(imported_data)
    # 开始从hive数据库拉数据
    data = get_absa_corpus(channel=channel, requiretags=None, number=number)
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
    print(f"可导入的有效数据是{len(valid_data)}, 有重复数据{len(data) - len(valid_data)} 是无需导入的")
    if not valid_data:
        # 如果都是已经导入过的数据，直接放弃导入
        return
    every_host_number = int(len(valid_data) / len(host))
    print(f"每个主机导入数据{every_host_number}")
    vdatas = [valid_data[i:i + every_host_number] for i in range(0, len(valid_data), every_host_number)]
    for h, vdata in zip(host, vdatas):
        r = requests.post(h + "project/import", data=json.dumps(vdata), headers=headers)
        pp.pprint(r.json())
        print(f"共导入主机host{h}中数据{len(vdata)}条")

def predict_dem8(test_data, host="192.168.50.139:3326"):
    """
    预测8个维度的数据，dem8接口调用
    :param test_data:
    :return:
    """
    post_data = []
    for d in test_data:
        text = d['text']
        keyword = d['keyword']
        wordtype = d['wordtype']
        post_data.append([text,keyword,wordtype])
    url = f"http://{host}/api/dem8_predict"
    data = {'data': post_data}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(data),  timeout=360)
    res_data = r.json()
    fitler_data = []
    for td,rd in zip(test_data,res_data):
        if rd[0] == "是":
            fitler_data.append(td)
    print(f"共有数据{len(test_data)}条，经过8个维度的模型的过滤后的剩余数据是{len(fitler_data)}条，去除无效数据{len(test_data)-len(fitler_data)}条")
    return fitler_data

def import_absa_data_host_first(channel=['jd', 'tmall'],channel_num=[6,6,6,6,6], leibie_num=[100, 100, 100, 100, 100,100,100,100], require_tags=["component","effect","fragrance","pack","skin","promotion","service","price"],num_by_channel=False, number=30, hostname=None, mirror=False, unique_type=1, ptime_keyword=">:2021-01-12", table="da_wide_table_before",keyword_threhold=20,predict_before=True):
    """
    按比例导入不同的host, 导入情感分析数据, 从hive数据库中导入, 导入到label-studio前，需要检查下这条数据是否已经导入过
    12月份，功效4000条，其它维度各1500条
    :param channel: 每个channel，都进行相同的搜索
    :param leibie_num: 每个类别的数量
    :param number: 搜索时的Limit的数量，不是最终的数量， 最终的数量由leibie_num确定
    :param num_by_channel: 按channel搜索，还是按类别搜索
    :param require_tags: 需要哪些维度的语料, eg: ["component", "effect"]
    :param hostname:平均导入每个host中,列表或None
    :param mirror: 给所有host导入一样的数据, 否则每个host平分所有数据
    :param predict_before: 在进行情感的数据导入前，通过8个维度的判断，筛选出符合8个维度判断的词
    :return:
    """
    # 对应着require_tags的中文名字
    if channel is None:
        channel = ["jd","weibo","redbook","tiktok","tmall"]
    leibie = ['成分', '功效', '香味', '包装', '肤感','促销','服务','价格']
    # leibie_num = [100, 100, 100, 100, 100]
    # leibie_num = [-1, -1, -1, -1, 200]
    # leibie_num = [2,4,2,2,2]
    from read_hive import get_absa_corpus, query_data_from_db
    # 要导入的数据
    valid_data = []
    # 已经导入的数据, 注意更改获取的样本数目，默认是5000条
    if hostname != None:
        host = hostname
    imported_data = []
    for h in host:
        print(f"获取{h}的任务")
        host_imported_data = get_tasks(page_size=8000, hostname=h)
        imported_data.extend(host_imported_data['tasks'])
    imported_data_md5 = get_imported_data_md5(imported_data)
    # 开始从hive数据库拉数据, 如果unique_type设置为2，那么数据可能过少
    # data = get_absa_corpus(channel=channel, requiretags=require_tags, number=number, unique_type=unique_type, ptime_keyword=ptime_keyword, table=table)
    data = query_data_from_db(channel=channel,channel_num=channel_num,leibie_num=leibie_num, require_tags=require_tags, num_by_channel=num_by_channel, unique_type=unique_type, ptime_keyword=ptime_keyword, table=table, add_search_num=number)
    # 获取到的data数据进行排查，如果已经导入过了，就过滤掉, 不需要initial_count进行二次类别检查了
    # initial_count = [0, 0, 0, 0, 0, 0, 0, 0]
    # keywords的unique记录
    keywords_dict = {}
    for one_data in data:
        # get_index = leibie.index(one_data['wordtype'])
        # if initial_count[get_index] < leibie_num[get_index]:
        #     initial_count[get_index] += 1
        # else:
        #     continue
        content = one_data['keyword'] + one_data['text']
        data_md5 = cal_md5(content)
        if data_md5 in imported_data_md5:
            # 数据已经导入到label-studio过了，不需要重新导入
            continue
        keyword_num = keywords_dict.get(one_data['keyword'], 0)
        if keyword_threhold !=0 and keyword_num > keyword_threhold:
            #这个keyword出现的次数已经超过所需要阈值，可以过滤掉, 加到数据库中，统计下
            keywords_dict[one_data['keyword']] = keyword_num + 1
            continue
        else:
            # 把keywords中的这个关键字的数量+1
            keywords_dict[one_data['keyword']] = keyword_num + 1
        # 没有导入过label-studio，那么加入到valid_data，进行导入
        # 设置md5字段，方便以后获取
        one_data['md5'] = data_md5
        valid_data.append(one_data)
    print(f'关键字出现的总的次数：{keywords_dict}')
    print(f"可导入的有效数据是{len(valid_data)}, 有重复数据或不需要数据{len(data) - len(valid_data)} 是无需导入的")
    if predict_before:
        valid_data = predict_dem8(test_data=valid_data)
    if not valid_data:
        # 如果都是已经导入过的数据，直接放弃导入
        return
    if len(valid_data) < number:
        print(f"收集的数据量过少，很可能是因为get_absa_corpus的unique type设置问题")

    if mirror:
        for h in host:
            r = requests.post(h + "project/import", data=json.dumps(valid_data), headers=headers)
            pp.pprint(r.json())
            print(f"共导入主机host{h}中数据{len(valid_data)}条")
    else:
        every_host_number = int(len(valid_data) / len(host))
        print(f"每个主机导入数据{every_host_number}")
        vdatas = [valid_data[i:i + every_host_number] for i in range(0, len(valid_data), every_host_number)]
        for h, vdata in zip(host, vdatas):
            r = requests.post(h + "project/import", data=json.dumps(vdata), headers=headers)
            pp.pprint(r.json())
            print(f"共导入主机host: {h}中数据{len(vdata)}条")


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


def export_data(hostname=None, dirpath="/opt/lavector/", jsonfile=None, proxy=False):
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
    url = host + "project/export?format=JSON"
    local_zipfile = hostip + "_" + port + "_" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".zip"
    local_zipfile = os.path.join("/tmp", local_zipfile)
    if jsonfile is None:
        local_jsonfile = hostip + "_" + port + ".json"
        local_jsonfile = os.path.join(dirpath, local_jsonfile)
    else:
        local_jsonfile = os.path.join(dirpath, jsonfile)
    if os.path.exists(local_jsonfile):
        print(f"注意，json文件已经存在即将覆盖json文件 {local_jsonfile}")
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
    assert (len(files) == 1), "压缩包里面不止一个文件，请检查"
    extract_file = files[0]
    os.rename(extract_file, local_jsonfile)
    print(f"{host}: 下载完成{local_zipfile}, 解压到{local_jsonfile}")
    return local_jsonfile


def export_data_host(hostnames, dirpath="/opt/lavector/"):
    """
    导出所有标注完的数据
    :return:
    """
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
    for hostname in hostnames:
        export_data(hostname=hostname, dirpath=dirpath)


def import_dev_data(hostname):
    """
    导入模型的开发数据集
    :return:
    """
    # testfile = "/Users/admin/git/TextBrewer/huazhuang/data_root_dir/newcos/dev.json"
    testfile = "/Users/admin/git/TextBrewer/huazhuang/utils/wrong.json"
    with open(testfile, 'r') as f:
        # 格式是[(text, keyword, labels)]
        loaddata = json.load(f)
    data = []
    for d in loaddata:
        # one_data = {'channel': 'jd','keyword': d[1],'text': d[0], 'wordtype': '未知'}
        one_data = {'data': {'channel': 'jd', 'keyword': d[1], 'text': d[0], 'wordtype': '未知',
                             "meta_info": {"location": "North Pole"}},
                    "completions": [
                        {
                            "result": [  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                                {
                                    "from_name": "label",
                                    "to_name": "text",
                                    "type": "labels",
                                    "value": {
                                        "end": d[3],
                                        "labels": [
                                            d[4]
                                        ],
                                        "start": d[2],
                                        "text": d[1]
                                    }
                                }
                            ]
                        }
                    ],
                    }
        data.append(one_data)
    r = requests.post(hostname + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())


def import_excel_per_data(hostname, testfile="/Users/admin/git/TextBrewer/huazhuang/utils/wrong.xlsx"):
    """
    导入模型人工标注后的excel模型, excel包含字段, 一个excel的一行仅一个标注数据
    	Text	                Keyword	        Label	    Predict	    Location	    Probability	    channel wordtype
        控油效果：不错产品香味：很香泡沫数量：中适合发质：中性。。。	控油	中性	积极	(0, 2)	0.720	jd 功效
    :return:
    """
    import pandas as pd
    df = pd.read_excel(testfile)
    data = []
    for idx, d in df.iterrows():
        # one_data = {'channel': 'jd','keyword': d[1],'text': d[0], 'wordtype': '未知'}
        # start和end必须是数字，否则无法显示
        post_data = {'data': {'channel': d["channel"], 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"]},
                    "completions": [
                        {
                            "result": [
                                {"from_name": "label",
                                 "id": "people",
                                 "to_name": "text",
                                 "type": "labels",
                                 "value": {
                                     "end": eval(d["location"])[1],
                                     "labels": [
                                         d["label"]
                                     ],
                                     "start": eval(d["location"])[0],
                                     "text": d["keyword"]
                                 }
                                 }
                            ]  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                        }
                    ],
                     "predictions": [
                        {
                            "model_version": "macbert",
                            "score": float(d["probability"]),
                            "result": [
                                {"from_name": "label",
                                 "id": "model1",
                                 "to_name": "text",
                                 "type": "labels",
                                 "value": {
                                     "end": eval(d["location"])[1],
                                     "labels": [
                                         d["predict"]
                                     ],
                                     "start": eval(d["location"])[0],
                                     "text": d["keyword"]
                                 }
                                 }
                            ]  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                        }
                    ],
                    }
        #把上一个词添加进去
        data.append(post_data)
    r = requests.post(hostname + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())


def import_excel_data(hostname):
    """
    导入模型人工标注后的excel模型
    	Text	                Keyword	        Label	    Predict	    Location	    Probability	    channel wordtype
        控油效果：不错产品香味：很香泡沫数量：中适合发质：中性。。。	控油	中性	积极	(0, 2)	0.720	jd 功效
    :return:
    """
    import pandas as pd
    testfile = "/Users/admin/git/TextBrewer/huazhuang/utils/wrong.xlsx"
    df = pd.read_excel(testfile)
    data = []
    # 合并相同的Text，里面有n个关键字
    previous_keyword = None
    previsou_text = None
    result = []
    last_data = None
    for idx, d in df.iterrows():
        # one_data = {'channel': 'jd','keyword': d[1],'text': d[0], 'wordtype': '未知'}
        # start和end必须是数字，否则无法显示
        one_result = {"from_name": "label",
                  "to_name": "text",
                  "type": "labels",
                  "value": {
                      "end": int(d["location"].lstrip('(').rstrip(')').split(',')[1]),
                      "labels": [
                          d["label"]
                      ],
                      "start": int(d["location"].lstrip('(').rstrip(')').split(',')[0]),
                      "text": d["keyword"]
                  }
                  }
        # 初始化
        if previous_keyword is None and previsou_text is None:
            previous_keyword = d["keyword"]
            previsou_text = d["text"]
            last_data = {'data': {'channel': d["channel"], 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"]},
                        "completions": [
                            {
                                "result": result  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                            }
                        ],
                        }
            result.append(one_result)
            continue
        elif previous_keyword == d["keyword"] and previsou_text == d["text"]:
            # 需要判断下一个句子的关键和text，如果相邻的2个句子和关键字是相同的，说明是一个句子中有几个关键词, 需要修改completions中的result
            result.append(one_result)
            #更新一下上一句的keyword
            previous_keyword = d["keyword"]
            previsou_text = d["text"]
            #更新last_data
            last_data = {'data': {'channel': d["channel"], 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"]},
                        "completions": [
                            {
                                "result": result  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                            }
                        ],
                        }
            # 把下一句也添加进来, 如果不是最后一个元素，才继续循环下一句
            if idx == (len(df)-1):
                data.append(last_data)
        else:
            #把上一个词添加进去
            data.append(last_data)
            previous_keyword = d["keyword"]
            previsou_text = d["text"]
            #重置result,添加完成后
            result = []
            result.append(one_result)
            last_data = {'data': {'channel': d["channel"], 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"]},
                        "completions": [
                            {
                                "result": result  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                            }
                        ],
                        }
            if idx == (len(df)-1):
                #最后一个元素也加进去
                data.append(last_data)
    r = requests.post(hostname + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())

def absa20000():
    for i in range(17,30):
        ptime = f">:2021-06-{i}"
        import_absa_data_host_first(channel=None,channel_num=[100,100,100,100,100], leibie_num=[500,500, 500, 500, 500,500,500,500],require_tags=["component","effect","fragrance","pack","skin","promotion","service","price"],number=10, hostname=hostnames, mirror=False, ptime_keyword=ptime,num_by_channel=False)

if __name__ == '__main__':
    # check_data()
    # setup_config(hostname=host)
    # get_project()
    # import_data()
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
    # hostnames = ["http://192.168.50.139:8081/api/", "http://192.168.50.139:8085/api/"]
    # hostnames = ["http://192.168.50.139:8089/api/"]
    hostnames = ["http://192.168.50.139:7081/api/","http://192.168.50.139:7082/api/","http://192.168.50.139:7083/api/","http://192.168.50.139:7084/api/"]
    # hostnames = ["http://127.0.0.1:8080/api/"]
    # setup_config(hostname="http://192.168.50.119:8090/api/")
    # import_absa_data_host(channel=['jd','tmall'],number=50, hostname=hostnames)
    # hostnames = ["http://192.168.50.119:8080/api/", "http://192.168.50.119:8081/api/"]
    # hostnames = ["http://192.168.50.119:8080/api/", "http://192.168.50.119:8081/api/","http://192.168.50.119:8082/api/",
    #              "http://192.168.50.119:8083/api/", "http://192.168.50.119:8084/api/","http://192.168.50.119:8085/api/",
    #              "http://192.168.50.119:8086/api/", "http://192.168.50.119:8087/api/","http://192.168.50.119:8088/api/",
    #              "http://192.168.50.119:8089/api/"]
    # delete_tasks_host(hostnames=hostnames)
    # setup_config_host(hostnames=hostnames)
    # import_absa_data_host_first(channel=["jd","weibo","redbook","tiktok","tmall"],channel_num=[40,40,40,40,40],leibie_num=[5, 5, 5, 5, 5, 5, 5, 5], number=100, hostname=hostnames, num_by_channel=True)
    # import_absa_data_host_first(channel=["jd","weibo","redbook","tiktok","tmall"],channel_num=[40,40,40,40,40],leibie_num=[0, 0, 0, 0, 0,40,0,0], number=200, hostname=hostnames, num_by_channel=True)
    # get_tasks_host(hostnames=hostnames)
    # get_completions_host(hostnames=hostnames)
    # export_data(hostname="http://192.168.50.119:8090/api/")
    export_data(hostname=hostnames[0], dirpath="/opt/lavector/absa/", jsonfile='7081-0707-2500.json')
    # import_absa_data_host_first(channel=None,channel_num=[200,200,200,200,200], leibie_num=[1000,1000, 1000, 1000, 1000,1000,1000,1000],require_tags=["component","effect","fragrance","pack","skin","promotion","service","price"],number=10, hostname=hostnames, mirror=False, ptime_keyword=">:2021-06-05",num_by_channel=False)
    # import_dev_data(hostname=hostnames[0])
    # import_excel_per_data(hostname=hostnames[0])
    # get_tasks(hostname=hostnames[0], taskid=1292)
    # absa20000()
