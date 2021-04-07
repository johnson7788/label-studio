import pickle
import os
import numpy as np
import string
import re
import random
import requests
import json
from label_studio.ml import LabelStudioMLBase

class RelationExtract(LabelStudioMLBase):

    def __init__(self, **kwargs):
        """
        模拟关系抽取的预测结果，用于标注数据时更方便
        :param kwargs:
        {'label_config': '<View>  <View style="flex: 30%; color:red">    <Header value="关键字" />    <Text name="keyword" value="$keyword"/>  </View>  <View style="flex: 30%">    <Header value="句子" />    <Text name="text" value="$text"/>    <Choices name="sentiment" toName="text" choice="single">      <Choice value="积极"/>      <Choice value="消极"/>      <Choice value="中性"/>    </Choices>  </View></View>', 'train_output': {'labels': ['中性', '积极'], 'model_file': '/Users/admin/git/label-studio/my_ml_backend/text_classification_project1a43/1608710349/model.pkl'}}
        """
        # don't forget to initialize base class...
        super(RelationExtract, self).__init__(**kwargs)

        self.train_url = "http://192.168.50.139:5010/api/train_truncate"
        self.predict_url = "http://192.168.50.139:5010/api/predict_truncate"

        # 然后从配置中收集所有key，这些key将用于从任务中提取数据并形成预测
        # 解析的label配置仅包含一个<Choices>类型的输出
        assert len(self.parsed_label_config) == 1
        self.from_name, self.info = list(self.parsed_label_config.items())[0]
        # 分类的方式，验证标签的方式
        # assert self.info['type'] == 'Choices'
        # ner的方式，验证标签的方式
        assert self.info['type'] == 'Labels'

        # 模型的输入, 校验
        assert len(self.info['to_name']) == 1
        assert len(self.info['inputs']) == 1
        assert self.info['inputs'][0]['type'] == 'Text'
        # self.to_name: text
        self.to_name = self.info['to_name'][0]
        #self.value: text
        self.value = self.info['inputs'][0]['value']

    def predict(self, tasks, **kwargs):
        """
        每次用户开始标注labeling的时候，进行一下预测,
        用户使用页面http://localhost:8080/进行标注的时候，进行一下预测
        :param tasks: 传入过来一条数据，被一条一条预测，有些奇怪, [{'id': 4498, 'data': {'text': '我都已经是修丽可b5的忠实粉丝啦啦啦啦。最近天气有点干，白天也要用上，之前没有那么干的时候就是晚上用的。真的觉得用完b5后皮肤稳定了很多，痘痘越来越少，超级无敌补水。', 'channel': 'redbook', 'brand': '修丽可b5', 'requirement': '补水'}, 'predictions': []}]
        :param kwargs:
        :return:
        """
        #存储data的数据是[(text, brand, requirement)]
        data = []
        for task in tasks:
            one_data = (task['data'][self.value], task['data']['brand'], task['data']['requirement'])
            data.append(one_data)
        assert len(data) == 1, "只能有一条数据过来"
        print(f"开始模拟预测: 数据量{len(data)}, 数据是{data}")
        # data = {'data': data}
        # headers = {'content-type': 'application/json'}
        # r = requests.post(self.predict_url, headers=headers, data=json.dumps(data), timeout=600)
        # results = r.json()
        predictions = []
        result = self.simulate(data)
        # 把所有样本的预测结果和分数加到predictions后返回
        predictions.append({'result': result, 'score': 0.5})
        return predictions

    def simulate(self, data):
        """
        模拟预测结果，data是一条数据
        :params data: 数据的列表格式
        Returns:
        """
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

        def do_fake_rels(result, from_ids, to_ids, labels=["是", "否"], ignore_require_in_brand=True, ignore_require_in_brand_pop=True, inverse_proportion=-1):
            """
            生成reuslt的新的内容，对每个from_ids和每个to_ids之间的关系进行生成一个假的关系
            Args:
                result ():
                from_ids (): 品牌的id的列表
                to_ids (): 需求的id的列表
                ignore_require_in_brand: 忽略需求在品牌内的情况
                ignore_require_in_brand_pop：是否移除这个需求在品牌内的单词
                inverse_proportion: 随品牌单词越远的需求，被选中作为fake关系的概率越小, 如果是-1，表示不适用，否是，需要传入一个句子的单词的总数
                labels
            Returns:
            """
            for fid in from_ids:
                #品牌的start和end的索引位置
                startfid = [r['value']['start'] for r in result if r.get('id') == fid][0]
                endfid = [r['value']['end'] for r in result if r.get('id') == fid][0]
                for tid in to_ids:
                    starttid = [r['value']['start'] for r in result if r.get('id') == tid][0]
                    endtid = [r['value']['end'] for r in result if r.get('id') == tid][0]
                    if starttid >= startfid and endtid <=endfid and ignore_require_in_brand:
                        # 如果需求在品牌范围内，那么忽略这个需求关键字
                        if ignore_require_in_brand_pop:
                            idx0 = [idx for idx, r in enumerate(result) if r.get('id') == tid][0]
                            result.pop(idx0)
                        continue
                    if inverse_proportion > 100 and abs(starttid-startfid) >50 and inverse_proportion != -1:
                        # 当句子长度大于100时，才考虑这个随机筛选,品牌和需求的距离越近，那么越可能被标注
                        probability = 1- abs(starttid-startfid)/inverse_proportion
                        choice = random.choices([False,True], [1-probability, probability],k=1)
                        #如果是False，那么不进行标注数据
                        if not choice[0]:
                            continue
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
            result = do_fake_rels(result=result, from_ids=brand_ids, to_ids=requirement_ids, labels=["是","否"],inverse_proportion=len(content))
            return result, brand_ids, requirement_ids
        #用于统计跳过的数据和brands的数量和requirments需求的数量
        for idx, d in enumerate(data):
            # 假设一条数据的标注结果
            content = d[0]
            content = content.lower()
            brand = d[1]
            requirement = d[2]
            brand_list = brand.split(',')
            requirement_list = requirement.split(',')
            # 更新result的内容
            result, brand_ids, requirement_ids = update_results(content=content, brand=brand_list, requirement=requirement_list)
        return result
    def fit(self, completions, workdir=None, **kwargs):
        """
        训练模型, 调用train的api接口时，进行训练，会获取所有已标注完成的数据，如果训练过模型，并且没有新的标注数据时，
        self.train_output会有数据，就不会走到这个训练接口了
        :param completions: 迭代器， 一条数据如 {'completions': [{'created_at': 1609124242, 'id': 6001, 'lead_time': 28.101, 'result': [{'from_name': 'label', 'id': '6fH8RpHe_5', 'to_name': 'text', 'type': 'labels', 'value': {'end': 21, 'labels': ['积极'], 'start': 19, 'text': '酒精'}}]}], 'data': {'channel': 'jd', 'keyword': '酒精', 'md5': '3003f5a1636b3155625da965c07f9c94', 'text': '搽在脸上很滋润。很保湿，感觉不错。不含酒精和香精兴致很。', 'wordtype': '成分'}, 'id': 6}
        :param workdir:
        :param kwargs:
        :return:
        """
        #训练数据格式是[(sentence, apspect_keyword, start_idx, end_idx, label),....]
        data = []
        # output_labels保存所有标注的labels， output_labels_idx保存labels对应的id
        output_labels, output_labels_idx = [], []
        # eg: label2idx: {'积极': 0, '消极': 1, '中性': 2}
        label2idx = {l: i for i, l in enumerate(self.labels)}
        for completion in completions:
            # 获取已标注完成的所有数据
            if completion['completions'][0].get('skipped') or completion['completions'][0].get('was_cancelled'):
                continue
            # input_text是一条文本
            input_text = completion['data'][self.value]

            #获取aspect关键词
            # input_aspect = completion['data']['keyword']
            # output_label = completion['completions'][0]['result'][0]['value']['choices'][0]

            #获取标注的样本的label, eg: '中性'
            completion_results = completion['completions'][0]['result']
            for completion_result in completion_results:
                input_aspect = completion_result['value']['text']
                start_idx = completion_result['value']['start']
                end_idx = completion_result['value']['end']
                output_label = completion_result['value']['labels'][0]
                output_labels.append(output_label)
            #组成一条训练数据
            one_data = (input_text, input_aspect, start_idx, end_idx, output_label)
            data.append(one_data)
            #转换成id
            output_label_idx = label2idx[output_label]
            output_labels_idx.append(output_label_idx)
        # 检查标注的样本的label和我们配置的标签label是一致都，如果是配置文件中是{'积极', '消极', '中性'}， 那么标注也应该是 {'积极', '消极', '中性'}
        new_labels = set(output_labels)
        if len(new_labels) != len(self.labels):
            self.labels = list(sorted(new_labels))
            print('Label set has been changed:' + str(self.labels))
            label2idx = {l: i for i, l in enumerate(self.labels)}
            output_labels_idx = [label2idx[label] for label in output_labels]

        print(f"开始训练模型: 数据量{len(data)}")
        #构造请求，发送数据，让模型开始训练
        data = {'data': data}
        headers = {'content-type': 'application/json'}
        r = requests.post(self.train_url, headers=headers, data=json.dumps(data), timeout=600)
        print(f"训练结果{r.json()}")

        # eg: {'labels': ['是', '否',], 'model_file': 'my_ml_backend/text_classification_project1a43/1608621143/model.pkl'}
        train_output = {
            'labels': self.labels,
            'model_file': "model_file"
        }
        return train_output
