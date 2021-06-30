#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2020/12/22 10:34 上午
# @File  : use_api.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  :  购买意向的数据提取，并导入标注系统
"""
数据的格式, 7分类, 喜欢，研究，想要，购买，复购，粉丝，推荐
title	content	关键词

"""
import requests
import json
import pprint
import os
import hashlib
import time
import re
import zipfile
import math
import collections

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
  <View style="flex: 30%; color:red">
    <Header value="$title" />
    <Text name="keyword" value="$keyword"/>
  </View>
  <View style="flex: 30%">
      <Labels name="label" toName="text">
        <Label value="喜欢" background="red"></Label>
        <Label value="想要" background="green"></Label>
        <Label value="研究" background="blue"></Label>
        <Label value="购买" background="black"></Label>
        <Label value="复购" background="gold"></Label>
        <Label value="粉丝" background="pink"></Label>
        <Label value="推荐" background="orange"></Label>
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
        r = requests.get(host + "tasks/" + taskid, data=json.dumps({'filters':None}), headers=headers)
    else:
        payload = {'fields': 'all', 'page': 1, 'page_size': page_size, 'order': 'id'}
        r = requests.get(host + "tasks", params=payload, data=json.dumps({'filters':None}), headers=headers)
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
    :return:
    """
    data = [{'title': '',
             'text': '还吃瓜呢？还不快来找一款合适自己的男士眼霜？科颜氏男士小冰棒眼霜，专门针对双眼易于疲劳，产生浮肿或者黑眼圈的人群，易于涂抹，轻轻一扫，双眼即被唤醒。放心交友的秘密武器#本人黑眼圈声明#',
             'keyword': '科颜氏男士小冰棒眼霜'},
            {'title': '我是标题',
             'text': '转眼就要过年啦~如果你问我有什么新年愿望~那自然是祈福新的一年红红火火，万事如意~这不~就特应景的入了自然堂X天坛祈福限量版礼盒！喜庆的红色礼盒包装，一收到就有种来年要鸿运当头的feel~礼盒包含了小紫瓶精华、小紫瓶熬夜眼霜、小紫瓶冰肌水和乳液四件套！重点来说下这个小紫瓶精华，真的是我秋冬的熬夜补水救星了~轻薄的质地，上脸意外的滋润，轻拍几下就能吸收~还添加有自然堂独家成分喜马拉雅红球藻，富含天然虾青素，有效对抗自由基，抗氧化的一把好手～4%烟酰胺焕亮肌肤，二裂酵母修护肌底，强强联手的成分，还怕什么熬夜黄！对像我这样长时间熬夜的妹子就比较友好~我差不多用了一周左右，脸上因为干燥形成的起皮都缓解不少，肤色也有所提亮噢！PS：搭配它的熬夜cp小紫瓶熬夜眼霜，修护效果更double！必须把好气色带到新的一年#祈福2021 天坛x自然堂# 收起全文d',
             'keyword': '小紫瓶熬夜眼霜'},
            ]
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


def import_absa_data_host_first(channel=['jd', 'tmall'],channel_num=[6,6,6,6,6], leibie_num=[100, 100, 100, 100, 100,100,100,100], require_tags=["component","effect","fragrance","pack","skin","promotion","service","price"],num_by_channel=False, number=30, hostname=None, mirror=False, unique_type=1, ptime_keyword=">:2021-01-12", table="da_wide_table_before",keyword_threhold=20):
    """
    按比例导入不同的host, 导入成分分析数据, 从hive数据库中导入, 导入到label-studio前，需要检查下这条数据是否已经导入过
    12月份，功效4000条，其它维度各1500条
    :param channel: channel:包括 "jd","weibo","redbook","tiktok","tmall"
    :param keyword_threhold: 0表示不进行keyword的过滤，如果给定数字，例如10，表示这个keyword不会在过滤次数中超过10次
    :param number: 从数据库检索的条目，不是最终数目，最终数目根据leibie_num确定
    :param require_tags: 需要哪些维度的语料
    :param hostname:平均导入每个host中,列表或None
    :return: 这个主机上现有的数据条数 int
    """
    # 对应着require_tags的中文名字
    leibie = ['成分', '功效', '香味', '包装', '肤感','促销','服务','价格']
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
    total_num = len(imported_data_md5) + len(vdata)
    return total_num

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
    #过滤出是wordtype的数据
    filter_data = [d for d in data if d[6] == wordtype]
    valid_data = []
    unique_data = []
    for d in filter_data:
        if d[0]+ d[1] in unique_data:
            continue
        else:
            unique_data.append(d[0]+ d[1])
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
    import pandas as pd
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
            last_data = {'data': {'channel': 'jd', 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"],
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
            #更新一下上一句的keyword
            previous_keyword = d["keyword"]
            previsou_text = d["text"]
            #更新last_data
            last_data = {'data': {'channel': 'jd', 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"],
                                 "meta_info": {"location": "North Pole"}},
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
            last_data = {'data': {'channel': 'jd', 'keyword': d["keyword"], 'text': d["text"], 'wordtype': d["wordtype"],
                                 "meta_info": {"location": "North Pole"}},
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


def save_json_toexcel(jsonfile):
    """
    把导出的label-studio的导出的某个json文件导出为excel格式
    :param jsonfile: /opt/lavector/package/192.168.50.139_8081.json
    :return:
    """
    from convert_label_studio_data import get_all, save_excel
    data, cancel_data = get_all(keep_cancel=True, split=False, dirpath=jsonfile)
    save_excel(data=data,output_file='export.xlsx')


def import_type_data(channel_num=[600, 600, 600, 600, 600]):
    """
    导入某个数据的data
    :param channel_num:  需要导入的数据的数量
    :type channel_num:
    :return:
    :rtype:
    """
    # leibie_num ： [100, 100, 100, 100, 100, 100, 100, 100]
    # leibie = ['成分', '功效', '香味', '包装', '肤感', '促销', '服务', '价格']
    total_num = sum(channel_num)
    type_config = [
        {
          'host': "http://192.168.50.139:7081/api/",
            'leibie_num': [0, 600, 0, 0, 0,0,0,0],
            'require_tags': ["effect"]
        },
        {
            'host': "http://192.168.50.139:7082/api/",
            'leibie_num': [0, 0, 0, 600, 0, 0, 0, 0],
            'require_tags': ["pack"]
        },
        {
            'host': "http://192.168.50.139:7083/api/",
            'leibie_num': [0, 0, 600, 0, 0, 0, 0, 0],
            'require_tags': ["fragrance"]
        },
        {
            'host': "http://192.168.50.139:7084/api/",
            'leibie_num': [0, 0, 0, 0, 0, 600, 0, 0],
            'require_tags': ["promotion"]
        },
    ]
    for conf in type_config:
        thishost = conf['host']
        leibie_num_init = conf['leibie_num']
        require_tags = conf['require_tags']
        delete_tasks_host(hostnames=[thishost])
        setup_config_host(hostnames=[thishost])
        ptimes_list = [">:2021-05-20", ">:2021-04-20", ">:2021-03-20", ">:2021-02-20", ">:2021-01-20"]
        iter_num = len(ptimes_list)
        start_iter = 0
        start_num = 0
        # 继续导入，直到导入的数量没问题了, 只是修改日期
        while start_num < total_num and start_iter < iter_num:
            should_num = total_num - start_num
            should_import_num = int(should_num/len(channel_num))
            should_import_num = 1 if should_import_num == 0 else should_import_num
            should_channel_num = [should_import_num] * len(channel_num)
            ptimes_keyword =ptimes_list[start_iter]
            # 更改下leibie_num，每个channel搜到的类别数量等于所有类别之和才可以
            leibie_num = [i if i ==0 else should_import_num for i in leibie_num_init]
            import_num = import_absa_data_host_first(channel=["jd", "weibo", "redbook", "tiktok", "tmall"],
                                        channel_num=should_channel_num, leibie_num=leibie_num,
                                        require_tags=require_tags, number=1000, hostname=[thishost], num_by_channel=True,
                                        ptime_keyword=ptimes_keyword, table="da_wide_table_before", keyword_threhold=30)
            start_iter += 1
            start_num = import_num

def read_arrow(arrow_file):
    import pyarrow as pa
    import json
    file_obj = pa.OSFile(arrow_file)
    result_all = file_obj.read()
    decode_res = result_all.decode('utf-8')
    res = json.loads(decode_res)
    return res

def import_raw_excel_data(hostname):
    """
    不从数据库中导入数据了，从最原始的excel中导入数据
    导入3个列， content, title, tag_format_品牌(aspect)
    :return:
    """
    import pandas as pd
    arrow_dir = '/Users/admin/Documents/lavector/购买意向分类/excel_data'
    arrow_list = os.listdir(arrow_dir)
    arrow_list_filter = [ex for ex in arrow_list if ex.endswith('.arrow')]
    data = []
    #按关键字过滤和content过滤
    # unique_keywords = []
    contents = []
    for arr_file in arrow_list_filter:
        arr_file_path = os.path.join(arrow_dir, arr_file)
        read_data = read_arrow(arrow_file=arr_file_path)
        select_data = zip(read_data['title'].values(), read_data['content'].values(), read_data['tag_format_品牌(aspect)'].values())
        count_data = 0
        for title, content, aspect in select_data:
            if not isinstance(title, str):
                title = ''
            if isinstance(content, str) and isinstance(aspect,str):
                # aspect 可能是逗号分隔的，那么只取第一个
                aspect_list = aspect.split(',')
                aspect = aspect_list[0]
                aspect = aspect.replace('_',' ')
                # if aspect not in unique_keywords:
                #     unique_keywords.append(aspect)
                # else:
                #     continue
                if content not in contents:
                    contents.append(content)
                else:
                    continue
                one_data = {'title': title, 'text': content, 'keyword': aspect}
                data.append(one_data)
                count_data += 1
            if len(data) > 5000:
                break
        print(f"从{arr_file}中共收集到数据 {count_data}条")
    print(f"共收集到数据 {len(data)}条")
    # 统计下数据，筛选出我们需要的数据
    title_counter = collections.Counter([d['title'] for d in data])
    content_counter = collections.Counter([d['text'] for d in data])
    keyword_counter = collections.Counter([d['keyword'] for d in data])
    print(f"共收集到的不同的句子数{len(content_counter)}, 不同的关键字数{len(keyword_counter)},不同的title数{len(title_counter)}")
    # 按照keywords过滤后的data
    r = requests.post(hostname + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())

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
    hostnames = ["http://192.168.50.139:7085/api/"]
    # hostnames = ["http://192.168.50.139:7081/api/","http://192.168.50.139:7082/api/","http://192.168.50.139:7083/api/","http://192.168.50.139:7084/api/"]
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
    # export_data(hostname=hostnames[0],dirpath="/opt/lavector/effect/",jsonfile="effect_3000_0623.json")
    # export_data(hostname=hostnames[1],dirpath="/opt/lavector/pack/",jsonfile="pack_3000_0623.json")
    # export_data(hostname=hostnames[2],dirpath="/opt/lavector/fragrance/",jsonfile="fragrance_3000_0623.json")
    # export_data(hostname=hostnames[3],dirpath="/opt/lavector/promotion/",jsonfile="promotion_3000_0623.json")
    # export_data_host(hostnames=hostnames, dirpath="/opt/lavector/package/")
    delete_tasks_host(hostnames=hostnames)
    # setup_config_host(hostnames=hostnames)
    # import_data(hostname=hostnames[0])
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
    # import_absa_data_host_first(channel=["jd","weibo","redbook","tiktok","tmall"],channel_num=[600,600,600,600,600],leibie_num=[0, 600, 0, 0, 0,0,0,0], require_tags=["effect"],number=1000, hostname=hostnames, num_by_channel=True, ptime_keyword=">:2021-05-20", table="da_wide_table_before",keyword_threhold=30)
    # import_absa_data_host_first(channel=["jd","weibo","redbook","tiktok","tmall"],channel_num=[40,40,40,40,40],leibie_num=[5, 5, 5, 5, 5, 5, 5, 5], number=100, hostname=hostnames, num_by_channel=True)
    # import_dev_data(hostname=hostnames[0])
    # import_excel_data(hostname=hostnames[0])
    # import_data(hostname=hostnames[0])
    # import_pure_data(host=hostnames, wordtype='包装')
    # save_json_toexcel(jsonfile='/opt/lavector/package/192.168.50.139_8081.json')
    # import_type_data()
    import_raw_excel_data(hostname=hostnames[0])
