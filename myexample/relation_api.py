#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2020/12/22 10:34 上午
# @File  : use_api.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  :  关系抽取判断
"""
关系抽取的相关设置
"""

import requests
import json
import pprint
import os
import hashlib
import time
import re
import zipfile
import pandas as pd
import random
import string

headers = {'content-type': 'application/json;charset=UTF-8'}
host = "http://localhost:8080/api/"
localhost = "http://localhost:8080/api/"
pp = pprint.PrettyPrinter(indent=4)


def setup_config(hostname=None):
    """
    ner分类的config
    :return:
    """
    data = {"label_config":
                """
<View>
  <Header value="关系判断，判断品牌和消费者需求之间是否存在关系" />
  <Relations>
    <Relation value="是" />
    <Relation value="否" />
  </Relations>

  <Labels name="label" toName="text">
    <Label value="品牌" />
    <Label value="需求" />
  </Labels>
  <Text name="text" value="$text" />
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
        r = requests.get(host + "tasks/" + taskid, data=json.dumps({'filters': None}), headers=headers)
    else:
        payload = {'fields': 'all', 'page': 1, 'page_size': page_size, 'order': 'id'}
        r = requests.get(host + "tasks", params=payload, data=json.dumps({'filters': None}), headers=headers)
    # print(r.json())
    # pp.pprint(r.json())
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


def import_data(hostname):
    """
    导入字典里面包含多个key和value的格式
    例如
    data = [{"text": "很好，实惠方便，会推荐朋友", "channel":"jd", "keyword":""},{"text": "一直买的他家这款洗发膏，用的挺好的，洗的干净也没有头皮屑"}]
    channel	content	关键词	判断是否准确	理由
tmall	有薄荷，抹上凉凉的，没有什么不适	薄荷	准确	说的是成分
tmall	整体评价：很大一瓶 水的质地比较浓稠 有股那种洗护的味道 刺鼻 不好闻 上脸比较滋润 鼻翼附近会刺痛 一分钱一分货吧 感受不好 不会回购 我一直在用红石榴和微精华水这两款水肤感都很好 推荐购买	红石榴	不准确	红石榴指的是产品
tmall	发货特别的快，我第1天买的，第2天就到了，迫不及待的打开试用了一下，吸收效果不错的，提亮肤色效果特别好，我的肤质比较偏干，正好适合秋冬季用，只是味道有一点点不太喜欢，自己加了两滴玫瑰精油一起，还挺好的。本来以为送了一盒膜，打开发现是个祝福的相框吧，还挺尴尬的。哈哈???	玫瑰	不准确	说的是精油，并非成分
tmall	不错，湿敷比擦拭更舒服，冰冰凉凉的有点提神，好闻的薄荷感	薄荷	不准确	说的是使用感受，并非成分
tmall	买来收敛毛孔的，看着是天猫超市，价格也便宜，标签包装都挺完整的，我都一层一层撕下来了，闻着是橙子和牙膏薄荷的味道。这个的产品有好多假冒的，希望是真的吧！	薄荷	不准确	说的是味道和使用感受，并非成分
tmall	湿敷的，有薄荷跟橘子的味道，才用，期待以后的效果吧	薄荷	不准确	说的是味道，并非成分
tmall	这个水可以用来湿敷 虽然用来湿敷有些贵 ！里面含有薄荷，涂上非常舒服，洗面奶面霜也炒鸡适合我 我油皮痘痘肌	薄荷	准确	说的是成分
redbook	今天分享一下我在夏天非常喜欢用的三款水：1??悦木之源菌菇水真的太太太喜欢啦，非常的清爽，不油腻，上脸吸收速度很快，湿敷对痘痘消肿有不错的效果。常年囤货。2??skii神仙水控油效果非常明显，对油皮和混油皮友好，干皮渗入。除了贵和味道之外，没有别的缺点，有预算的宝宝买就对了。3??城野医生收敛水可以调理你的皮脂分泌，但是没有收缩毛孔和去黑头的功效，使用感很好，清清凉凉的，但其实不添加酒精，而是添加了薄荷醇，肤感和气味都和酒精有点类似，但是很温和，不会造成屏障受损。@生活薯  @薯队长	薄荷	准确	说的是成分
tmall	用在白泥之后还是很不错的，觉得有二次湿敷出白头，收缩毛孔大概是有的吧	白泥	不准确	说的是产品，并非成分
weibo	#空瓶记# #空瓶记城野医生的毛孔收敛水 每周毛孔清洁后必备的水儿 配合奥尔滨的化妆棉进行二次清洁 平价好用 推了一万年了 我去日本就背了七八瓶回来颐莲的玻尿酸护发原液 因为我头发经常烫染所以发梢有点受损 每次洗完头发按三泵涂抹 不粘腻及时补水然后再涂抹护发精油锁住水份 颐莲这个牌子是福瑞达旗下的 福瑞达和华西生物都是国内做玻尿酸的大牛 雅诗兰黛的玻尿酸供应商 所以不要瞧不起他们 有这么便宜好用性价比高的国货不支持 还等啥呢 收起全文d	玻尿酸	不准确	说的是产品，并非成分

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
    :param: imported_data是每个tasks
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


def import_com_data_host(channel=['jd', 'tmall'], number=10, hostname=None):
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


def import_com_data_host_first(channel=['jd', 'tmall'], keyword_threhold=0, leibie_num=[1000, -1, -1, -1, -1],
                               require_tags=["component", "effect", "fragrance", "pack", "skin"], number=10,
                               unique_type=1, hostname=None, ptime_keyword=">:2020-12-01", not_cache=True,
                               table="da_wide_table_new"):
    """
    按比例导入不同的host, 导入成分分析数据, 从hive数据库中导入, 导入到label-studio前，需要检查下这条数据是否已经导入过
    12月份，功效4000条，其它维度各1500条
    :param channel: channel:包括 "jd","weibo","redbook","tiktok","tmall"
    :param keyword_threhold: 0表示不进行keyword的过滤，如果给定数字，例如10，表示这个keyword不会在过滤次数中超过10次
    :param number: 从数据库检索的条目，不是最终数目，最终数目根据leibie_num确定
    :param require_tags: 需要哪些维度的语料
    :param hostname:平均导入每个host中,列表或None
    :return:
    """
    from math_tags import get_emotional_words
    confirm_file = "com_100.txt"
    all_tags = []
    # 收集所有tags
    with open(confirm_file, 'r') as f:
        for line in f:
            line = line.strip()
            tmp = {}
            tmp['0'] = line.split('|')
            all_tags.append(str(tmp))
    leibie = ['成分', '功效', '香味', '包装', '肤感']
    from read_hive import get_absa_corpus
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
    data = get_absa_corpus(channel=channel, requiretags=require_tags, number=number, unique_type=unique_type,
                           ptime_keyword=ptime_keyword, not_cache=not_cache, table=table)
    # 获取到的data数据进行排查，如果已经导入过了，就过滤掉
    initial_count = [0, 0, 0, 0, 0]
    # keywords的unique记录
    keywords_dict = {}
    for one_data in data:
        get_index = leibie.index(one_data['wordtype'])
        if initial_count[get_index] < leibie_num[get_index]:
            initial_count[get_index] += 1
        else:
            continue
        content = one_data['keyword'] + one_data['text']
        data_md5 = cal_md5(content)
        # 用于匹配当前这个数据的关键字是否和我们提供的100%确定是成分的关键字匹配
        match_keywords = []
        # 已经获取了多少个这个关键字的示例, 如果不存在，那么为0
        keyword_num = keywords_dict.get(one_data['keyword'], 0)
        for current_tags in all_tags:
            keywords, keyword_dictid = get_emotional_words(tag_words=current_tags, content=content)
            match_keywords.extend(keywords)
        if data_md5 in imported_data_md5:
            # 数据已经导入到label-studio过了，不需要重新导入
            continue
        if one_data['keyword'] in match_keywords:
            print(f'这个句子的关键字: {one_data["keyword"]} 在白名单中出现，跳过，句子是: {one_data["text"]}')
            continue
        elif keyword_threhold != 0 and keyword_num > keyword_threhold:
            # 这个keyword出现的次数已经超过所需要阈值，可以过滤掉, 加到数据库中，统计下
            keywords_dict[one_data['keyword']] = keyword_num + 1
            continue
        else:
            # 没有导入过label-studio，那么加入到valid_data，进行导入
            # 设置md5字段，方便以后获取
            # 把keywords中的这个关键字的数量+1
            keywords_dict[one_data['keyword']] = keyword_num + 1
            one_data['md5'] = data_md5
            valid_data.append(one_data)
    print(f'关键字出现的总的次数：{keywords_dict}')
    print(f"可导入的有效数据是{len(valid_data)}, 有重复数据或不需要数据{len(data) - len(valid_data)} 是无需导入的")
    if not valid_data:
        # 如果都是已经导入过的数据，直接放弃导入
        return
    if len(valid_data) < number:
        print(f"收集的数据量过少，很可能是因为get_absa_corpus的unique type设置问题")
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


def import_pure_data(host, dirpath='/opt/lavector/absa', wordtype='包装', limit=None):
    """
    导入纯数据，不包含标签，从json文件中导入
    :param host: 主机列表
    :param dirpath: 文件夹或路径
    :param wordtype:      功效  成分  香味 包装 肤感
    :param limit:  限制导入数据条数，
    :return:
    """
    from convert_label_studio_data import get_all
    data = get_all(split=False, dirpath=dirpath)
    # 过滤出是wordtype的数据
    filter_data = [d for d in data if d[6] == wordtype]
    valid_data = []
    unique_data = []
    for d in filter_data:
        if d[0] + d[1] in unique_data:
            continue
        else:
            unique_data.append(d[0] + d[1])
        one_data = {'channel': d[5], 'keyword': d[1], 'text': d[0], 'wordtype': d[-1]}
        valid_data.append(one_data)
    if limit and len(valid_data) > limit:
        valid_data = valid_data[:limit]
    every_host_number = int(len(valid_data) / len(host))
    print(f"每个主机导入数据{every_host_number}")
    vdatas = [valid_data[i:i + every_host_number] for i in range(0, len(valid_data), every_host_number)]
    for h, vdata in zip(host, vdatas):
        r = requests.post(h + "project/import", data=json.dumps(vdata), headers=headers)
        pp.pprint(r.json())
        print(f"共导入主机host{h}中数据{len(vdata)}条")


def import_excel_data(hostname):
    """
    导入模型人工标注后的excel模型, excel包含字段
    	Text	                Keyword	        Label	    Predict	    Location	    Probability	    Check
        控油效果：不错产品香味：很香泡沫数量：中适合发质：中性。。。	控油	中性	积极	(0, 2)	0.720	积极
    :return:
    """
    testfile = "/Users/admin/Desktop/full_wrong.xlsx"
    df = pd.read_excel(testfile)
    data = []
    # 合并相同的Text，里面有n个关键字
    previous_keyword = None
    previsou_text = None
    result = []
    last_data = None
    for idx, d in df.iterrows():
        # one_data = {'channel': 'jd','keyword': d[1],'text': d[0], 'wordtype': '未知'}
        if d["Check"] == "无法判断":
            d["Check"] = "中性"
        # start和end必须是数字，否则无法显示
        one_result = {"from_name": "label",
                      "to_name": "text",
                      "type": "labels",
                      "value": {
                          "end": int(d["location"].lstrip('(').rstrip(')').split(',')[1]),
                          "labels": [
                              d["Check"]
                          ],
                          "start": int(d["location"].lstrip('(').rstrip(')').split(',')[0]),
                          "text": d["keyword"]
                      }
                      }
        # 初始化
        if previous_keyword is None and previsou_text is None:
            previous_keyword = d["keyword"]
            previsou_text = d["text"]
            last_data = {
                'data': {'channel': 'jd', 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"],
                         "meta_info": {"location": "North Pole"}},
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
            # 更新一下上一句的keyword
            previous_keyword = d["keyword"]
            previsou_text = d["text"]
            # 更新last_data
            last_data = {
                'data': {'channel': 'jd', 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"],
                         "meta_info": {"location": "North Pole"}},
                "completions": [
                    {
                        "result": result  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                    }
                ],
                }
            # 把下一句也添加进来, 如果不是最后一个元素，才继续循环下一句
            if idx == (len(df) - 1):
                data.append(last_data)
        else:
            # 把上一个词添加进去
            data.append(last_data)
            previous_keyword = d["keyword"]
            previsou_text = d["text"]
            # 重置result,添加完成后
            result = []
            result.append(one_result)
            last_data = {
                'data': {'channel': 'jd', 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"],
                         "meta_info": {"location": "North Pole"}},
                "completions": [
                    {
                        "result": result  # 标注结果, 这里对应的是一个人标注的结果，里面可能进行了多个标注
                    }
                ],
                }
            if idx == (len(df) - 1):
                # 最后一个元素也加进去
                data.append(last_data)
    r = requests.post(hostname + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())


def save_json_toexcel(jsonfile):
    """
    把导出的label-studio的导出的某个json文件导出为excel格式
    :param jsonfile: /opt/lavector/package/192.168.50.139_8081.json
    :return:
    """
    from convert_label_studio_data import get_all, save_excel
    data, cancel_data = get_all(keep_cancel=True, split=False, dirpath=jsonfile)
    save_excel(data=data, output_file='export.xlsx')


def import_raw_excel(hostname, excel, fake_anotate=False, repeat_content=False, keep_data=10000):
    """
    从excel中读取数据，导出到label-studio中，进行数据标注
    :param hostname:
    :param excel: excel的路径
    :param fake_anotate: bool 是否虚拟一个标注结果，如果不是，那么就导入原始数据
    :param repeat_content: bool content是否存在重复，如果存在，需要去重
    :param keep_data: -1,表示保留所有数据
    :return:
    """
    df = pd.read_excel(excel)
    data = []
    if fake_anotate and repeat_content:
        def text_in_result(result, text):
            """
            判断text 是否已经在result中了, 如果存在，那么返回True和它的id的组成的列表，只有一个元素的列表
                  "result": [
                        {
                          "value": {
                            "start": 175,
                            "end": 178,
                            "text": "理肤泉",
                            "labels": [
                              "品牌"
                            ]
                          },
                          "id": "gXLA_EAdg5",
                          "from_name": "label",
                          "to_name": "text",
                          "type": "labels"
                        },
                        {
                          "value": {
                            "start": 495,
                            "end": 497,
                            "text": "补水",
                            "labels": [
                              "需求"
                            ]
                          },
                          "id": "WsYfTtxa7B",
                          "from_name": "label",
                          "to_name": "text",
                          "type": "labels"
                        },
                        ]
            result: list[dict]
            text : string
            return: bool
            """
            if not result:
                return False, []
            all_result_text = {i["value"]["text"]: i["id"] for i in result}
            text_id = all_result_text.get(text)
            if text_id:
                return True, [text_id]
            else:
                return False, []

        def add_brand_requirement(content, result, text, label="品牌"):
            """
            需要搜索text，把text添加到result中, 需要生成id，id是10位随机字符，其他参数默认,生一个item，返回
             result中的一个元素  {
              "value": {
                "start": 175,
                "end": 178,
                "text": "理肤泉",
                "labels": [
                  "品牌"
                ]
              },
              "id": "gXLA_EAdg5",
              "from_name": "label",
              "to_name": "text",
              "type": "labels"
            }
            Args:
                result ():
                content ():
                label (): "品牌"或者"需求"
                text (): string
            Returns: result和branch_ids
            """
            text_locations = search_text(content, text)
            exists_ids = [i["id"] for i in result]
            # assert len(text_locations) > 0, f"{label}: {text}关键字不在内容里面，这是有问题的"
            ids = []
            for loc in text_locations:
                id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                assert id not in exists_ids, "随机生成的id和已有的id是重复的，这个概率太小了"
                item = {
                    "value": {
                        "start": loc[0],
                        "end": loc[1],
                        "text": text,
                        "labels": [
                            label
                        ]
                    },
                    "id": id,
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels"
                }
                ids.append(id)
                result.append(item)
            return result, ids

        def search_text(content, text):
            """
            从给定的content中搜索text的位置，返回的是一个列表
            Args:
                content ():
                text ():
            Returns: text 的索引位置的列表
            """
            text_locations = []
            text_re = re.escape(text)
            res = re.finditer(text_re, content)
            for i in res:
                start = i.start()
                end = i.end()
                text_locations.append((start, end))
            assert text_locations, "搜索的结果不能为空"
            return text_locations

        def do_fake_rel(result, from_ids, to_ids, labels=["是", "否"]):
            """
            生成reuslt的新的内容，对每个from_ids和每个to_ids之间的关系进行生成一个假的关系
            Args:
                result ():
                from_ids (): 品牌的id的列表
                to_ids (): 需求的id的列表
                labels
            Returns:
            """
            for fid in from_ids:
                for tid in to_ids:
                    label = random.choice(labels)
                    item = {
                        "from_id": fid,
                        "to_id": tid,
                        "type": "relation",
                        "direction": "right",
                        "labels": [
                            label
                        ]
                    }
                    result.append(item)
            return result

        def update_result(result, content, brand, requirement):
            """
            Args:
                result ():
                content ():
                brand ():
                requirement ():
            Returns:

            """
            # 合并前需要确定品牌和需求的内容是否已经加入到了result中，如果没有，那么在开始添加
            brand_isin, brand_ids = text_in_result(result, brand)
            if not brand_isin:
                # 从content中国搜索关键字的位置，然后加入到result中,生成新的brand_id
                result, brand_ids = add_brand_requirement(content=content, result=result, text=brand, label="品牌")
            requirement_isin, requirement_ids = text_in_result(result, requirement)
            if not requirement_isin:
                # 从content中国搜索关键字的位置，然后加入到result中,生成新的brand_id
                result, requirement_ids = add_brand_requirement(content=content, result=result, text=requirement,
                                                                label="需求")
            # 开始生成fake的关系，最终需要人工去判断关系是否正确
            result = do_fake_rel(result=result, from_ids=brand_ids, to_ids=requirement_ids)
            return result

        previous_text = None
        previous_data_content = None
        result = []
        for idx, d in df.iterrows():
            # 假设一条数据的标注结果
            content = d["content"]
            content = content.lower()
            channel = d["channel"]
            brand = d["品牌"]
            brand_num = d["品牌_词语数量"]
            requirement = d["消费者需求"]
            requirement_num = d["消费者需求_词语数量"]
            data_content = {"text": content, "channel": channel,
                            "brand": brand, "requirement": requirement}
            if brand_num == 0 or requirement_num == 0:
                #跳过无效数据
                continue
            brand_list = brand.split(',')
            requirement_list = requirement.split(',')
            assert len(brand_list) == brand_num, "品牌逗号分隔的数量和得到的结果不相等"
            assert len(requirement_list) == requirement_num, "需求的分隔的数量和预设的结果不相等"
            if previous_text is None or previous_text == content:
                # 如果previous_text是None，或和这一次相等，那么更新result即可
                result = update_result(result=result, content=content, brand=brand, requirement=requirement)
                # 更新下previous_text
                previous_text = content
                previous_data_content = data_content
            else:
                # 不同的text，可以加到data中了
                one_data = {"data": previous_data_content, "completions": [{"result": result}]}
                data.append(one_data)
                previous_text = content
                previous_data_content = data_content
                # 更新result的内容
                result = update_result(result=result, content=content, brand=brand, requirement=requirement)
        # 最后一个数据也加入
        last_data = {"data": previous_data_content, "completions": [{"result": result}]}
        data.append(last_data)
    elif fake_anotate and not repeat_content:
        #不存在重复的content
        def add_brand_requirements(result, content, text, label="品牌"):
            """
            需要搜索text，把text添加到result中, 需要生成id，id是10位随机字符，其他参数默认,生一个item，返回
             result中的一个元素  {
              "value": {
                "start": 175,
                "end": 178,
                "text": "理肤泉",
                "labels": [
                  "品牌"
                ]
              },
              "id": "gXLA_EAdg5",
              "from_name": "label",
              "to_name": "text",
              "type": "labels"
            }
            Args:
                result ():
                content ():
                label (): "品牌"或者"需求"
                text (): list
            Returns: result和branch_ids
            """
            ids = []
            for one_text in text:
                #对于每个需求或这每个品牌，都要有一个id，不同位置也是不同的id
                text_locations = search_texts(content, one_text)
                for loc in text_locations:
                    id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                    item = {
                        "value": {
                            "start": loc[0],
                            "end": loc[1],
                            "text": one_text,
                            "labels": [
                                label
                            ]
                        },
                        "id": id,
                        "from_name": "label",
                        "to_name": "text",
                        "type": "labels"
                    }
                    ids.append(id)
                    result.append(item)
            return result, ids

        def search_texts(content, text):
            """
            从给定的content中搜索text的位置，返回的是一个列表
            Args:
                content ():
                text ():
            Returns: text 的索引位置的列表
            """
            text_locations = []
            text_re = re.escape(text)
            res = re.finditer(text_re, content)
            for i in res:
                start = i.start()
                end = i.end()
                text_locations.append((start, end))
            assert text_locations, "搜索的结果不能为空"
            return text_locations

        def do_fake_rels(result, from_ids, to_ids, labels=["是", "否"]):
            """
            生成reuslt的新的内容，对每个from_ids和每个to_ids之间的关系进行生成一个假的关系
            Args:
                result ():
                from_ids (): 品牌的id的列表
                to_ids (): 需求的id的列表
                labels
            Returns:
            """
            for fid in from_ids:
                for tid in to_ids:
                    label = random.choice(labels)
                    item = {
                        "from_id": fid,
                        "to_id": tid,
                        "type": "relation",
                        "direction": "right",
                        "labels": [
                            label
                        ]
                    }
                    result.append(item)
            return result

        def update_results(content, brand, requirement):
            """
            Args:
                content (): 文本内容
                brand (): list
                requirement (): list
            Returns:

            """
            result = []
            # 从content中国搜索关键字的位置，然后加入到result中,生成新的brand_id
            result, brand_ids = add_brand_requirements(result=result, content=content, text=brand, label="品牌")
            # 从content中国搜索关键字的位置，然后加入到result中,生成新的brand_id
            result, requirement_ids = add_brand_requirements(result=result, content=content,text=requirement,label="需求")
            # 开始生成fake的关系，最终需要人工去判断关系是否正确
            result = do_fake_rels(result=result, from_ids=brand_ids, to_ids=requirement_ids, labels=["是", "否"])
            return result, brand_ids, requirement_ids
        #用于统计跳过的数据和brands的数量和requirments需求的数量
        skip_data = 0
        brids = []
        reqids = []
        for idx, d in df.iterrows():
            # 假设一条数据的标注结果
            content = d["content"]
            content = content.lower()
            channel = d["channel"]
            brand = d["品牌"]
            brand_num = d["品牌_词语数量"]
            requirement = d["消费者需求"]
            requirement_num = d["消费者需求_词语数量"]
            data_content = {"text": content, "channel": channel,
                            "brand": brand, "requirement": requirement}
            if brand_num == 0 or requirement_num == 0:
                skip_data += 1
                #跳过无效数据
                continue
            brand_list = brand.split(',')
            requirement_list = requirement.split(',')
            assert len(brand_list) == brand_num, "品牌逗号分隔的数量和得到的结果不相等"
            assert len(requirement_list) == requirement_num, "需求的分隔的数量和预设的结果不相等"
            # 更新result的内容
            result, brand_ids, requirement_ids = update_results(content=content, brand=brand_list, requirement=requirement_list)
            brids.append(brand_ids)
            reqids.append(requirement_ids)
            # 不同的text，可以加到data中了
            one_data = {"data": data_content, "completions": [{"result": result}]}
            data.append(one_data)
        print(f"共跳过{skip_data}个数据，共收集{sum(len(i) for i in brids)}个品牌数据, 共收集{sum(len(i) for i in reqids)}个需求数据")
    else:
        for idx, d in df.iterrows():
            content = d["content"]
            content = content.lower()
            channel = d["channel"]
            brand = d["品牌"]
            brand_num = d["品牌_词语数量"]
            requirement = d["消费者需求"]
            requirement_num = d["消费者需求_词语数量"]
            if brand_num == 0 or requirement_num == 0:
                #跳过无效数据
                continue
            brand_list = brand.split(',')
            requirement_list = requirement.split(',')
            assert len(brand_list) == brand_num, "品牌逗号分隔的数量和得到的结果不相等"
            assert len(requirement_list) == requirement_num, "需求的分隔的数量和预设的结果不相等"
            data_content = {"text": content, "channel": channel,
                            "brand": brand, "requirement": requirement}
            data.append(data_content)
    if keep_data != -1:
        print(f"共收集到有效数据{len(data)}条,需要保留{keep_data}条数据")
        data = data[:keep_data]
    r = requests.post(hostname + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())


def prepare_unique_excel(input_excel, output_excel, limit=10000):
    """
    只保留da_index, title, content
    Args:
        input_excel ():
        output_excel ():
    Returns:

    """
    data = []
    indexes = []
    excels = os.listdir(input_excel)
    total_excels = len(excels)
    for num, ex in enumerate(excels):
        print(f"开始处理任务")
        excel = os.path.join(input_excel, ex)
        df = pd.read_excel(excel)
        for idx, d in df.iterrows():
            index = d["da_index"]
            title = d["title"]
            channel = d["channel"]
            content = d["content"]
            brand = d["tag_format_品牌(品牌中文)"]
            if isinstance(brand, float):
                # 跳过nan的
                continue
            if index in indexes:
                continue
            else:
                indexes.append(index)
                one_data = {
                    "da_index": index,
                    "title": title,
                    "content": content,
                    "channel": channel,
                    "brand": brand
                }
                data.append(one_data)
            if len(data) > 5000 * (num + 1):
                print(f"这个excel收集完成了{5000}条数据，退出")
                break
        print(f"Excel {ex} 已经处理完成")
    writer = pd.ExcelWriter(output_excel, engine='xlsxwriter')
    df = pd.DataFrame(data)
    df.to_excel(writer, sheet_name='标注数据')
    writer.save()


if __name__ == '__main__':
    # check_data()
    # setup_config(hostname=host)
    # get_project()
    # import_data()
    # get_tasks()
    # get_tasks(taskid=0)
    # get_completions()
    # delete_completions()
    # health()
    # list_models()
    # train_model()
    # predict_model()
    # hostnames = ["http://192.168.50.139:8084/api/"]
    hostnames = ["http://192.168.50.139:8080/api/"]
    # hostnames = ["http://192.168.50.139:8086/api/","http://192.168.50.139:8088/api/"]
    # hostnames = ["http://192.168.50.139:8081/api/","http://192.168.50.139:8082/api/", "http://192.168.50.139:8083/api/",
    #              "http://192.168.50.139:8084/api/","http://192.168.50.139:8085/api/","http://192.168.50.139:8086/api/",
    #              "http://192.168.50.139:8087/api/"]
    # hostnames = ["http://127.0.0.1:8080/api/"]
    # setup_config(hostname="http://192.168.50.119:8090/api/")
    # import_absa_data_host(channel=['jd','tmall'],number=50, hostname=hostnames)
    # hostnames = ["http://192.168.50.119:8080/api/", "http://192.168.50.119:8081/api/"]
    # hostnames = ["http://192.168.50.119:8080/api/", "http://192.168.50.119:8081/api/","http://192.168.50.119:8082/api/",
    #              "http://192.168.50.119:8083/api/", "http://192.168.50.119:8084/api/","http://192.168.50.119:8085/api/",
    #              "http://192.168.50.119:8086/api/", "http://192.168.50.119:8087/api/","http://192.168.50.119:8088/api/",
    #              "http://192.168.50.119:8089/api/"]
    # import_absa_data_host_first(channel=['jd','tmall'],number=4000, hostname=hostnames)
    # get_tasks_host(hostnames=hostnames)
    # get_completions_host(hostnames=hostnames)
    # export_data(hostname="http://192.168.50.119:8090/api/")
    export_data_host(hostnames=hostnames, dirpath="/opt/lavector/relation/")
    # setup_config_host(hostnames=hostnames)
    # delete_tasks_host(hostnames=hostnames)
    # get_tasks(hostname='http://127.0.0.1:8080/api/')
    # ptimes1 = ["<:2020-10-01","<:2020-10-08", "<:2020-10-15","<:2020-10-30","<:2020-11-08","<:2020-11-15","<:2020-11-30","<:2020-12-08","<:2020-12-15", "<:2020-12-30", "<:2021-01-08","<:2021-1-15", "<:2021-1-30"]
    # ptimes2 = ["<:2020-09-01","<:2020-09-08", "<:2020-09-15","<:2020-09-20","<:2020-09-25","<:2020-11-11","<:2020-12-11","<:2020-12-25", "<:2021-01-08","<:2021-1-20", "<:2021-1-25"]
    # ptimes3 = ["<:2020-08-01","<:2020-08-15"]
    # ptimes = ptimes1+ ptimes2 +ptimes3
    # ptimes = ["<:2021-1-3", "<:2021-1-6"]
    # for ptime in ptimes:
    #     print(ptime)
    #     import_com_data_host_first(channel=None,keyword_threhold=0,ptime_keyword=ptime, leibie_num=[5000, -1, -1, -1, -1], require_tags=['component'], number=1000, unique_type=2, hostname=hostnames, not_cache=True, table="da_wide_table_new")
    # import_com_data_host_first(channel=None,keyword_threhold=20,ptime_keyword=">:2020-1-20", leibie_num=[5000, -1, -1, -1, -1], require_tags=['component'], number=5000, unique_type=2, hostname=hostnames, not_cache=True, table="da_wide_table_new")
    # import_dev_data(hostname=hostnames[0])
    # import_excel_data(hostname=hostnames[0])
    # import_data(hostname=hostnames[0])
    # import_pure_data(host=hostnames, wordtype='包装')
    # save_json_toexcel(jsonfile='/opt/lavector/package/192.168.50.139_8081.json')
    # import_raw_excel(hostname=hostnames[0],excel='/Users/admin/Documents/资生堂产品最后结果/mini_test.xlsx')
    # import_raw_excel(hostname=hostnames[0], excel='/Users/admin/Documents/lavector/relation/data.xlsx',
    #                  fake_anotate=True, repeat_content=False, keep_data=5000)
    # prepare_unique_excel(input_excel='/Users/admin/Documents/资生堂品牌医美项目结果/', output_excel='/Users/admin/Downloads/o1.xlsx')
