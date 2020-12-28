import pickle
import os
import numpy as np

import requests
import json
from label_studio.ml import LabelStudioMLBase

class ABSATextClassifier(LabelStudioMLBase):

    def __init__(self, **kwargs):
        """
        当调用train或预测的时候会初始化, 需要调用train_model()接口的api
        :param kwargs:
        {'label_config': '<View>  <View style="flex: 30%; color:red">    <Header value="关键字" />    <Text name="keyword" value="$keyword"/>  </View>  <View style="flex: 30%">    <Header value="句子" />    <Text name="text" value="$text"/>    <Choices name="sentiment" toName="text" choice="single">      <Choice value="积极"/>      <Choice value="消极"/>      <Choice value="中性"/>    </Choices>  </View></View>', 'train_output': {'labels': ['中性', '积极'], 'model_file': '/Users/admin/git/label-studio/my_ml_backend/text_classification_project1a43/1608710349/model.pkl'}}
        """
        # don't forget to initialize base class...
        super(ABSATextClassifier, self).__init__(**kwargs)

        self.train_url = "http://127.0.0.1:5000/api/train_truncate"
        self.predict_url = "http://127.0.0.1:5000/api/predict_truncate"

        # 然后从配置中收集所有key，这些key将用于从任务中提取数据并形成预测
        # 解析的label配置仅包含一个<Choices>类型的输出
        assert len(self.parsed_label_config) == 1
        self.from_name, self.info = list(self.parsed_label_config.items())[0]
        assert self.info['type'] == 'Choices'

        # 模型的输入, 校验
        assert len(self.info['to_name']) == 1
        assert len(self.info['inputs']) == 1
        assert self.info['inputs'][0]['type'] == 'Text'
        # self.to_name: text
        self.to_name = self.info['to_name'][0]
        #self.value: text
        self.value = self.info['inputs'][0]['value']

        #判断模型时已经训练完成还是没有训练过
        if not self.train_output:
            # 如果没有训练，请定义冷启动的文本分类器, 初始化模型
            # 所有的labels, self.labels: ['积极', '消极', '中性']
            self.labels = self.info['labels']
            # 训练模型，这里是调用sklearn的fit函数
            print('初始化模型 from_name={from_name}, to_name={to_name}, labels={labels}'.format(
                from_name=self.from_name, to_name=self.to_name, labels=str(self.labels)
            ))
        else:
            # 否则，从最新的训练结果中加载模型, eg: '/Users/admin/git/label-studio/my_ml_backend/text_classification_project1a43/1608710764/model.pkl'
            self.model_file = self.train_output['model_file']
            # 获取labels,从训练的输出中获取, eg: ['积极', '消极', '中性']
            self.labels = self.train_output['labels']
            print('从训练结果中获取 from_name={from_name}, to_name={to_name}, labels={labels}'.format(
                from_name=self.from_name, to_name=self.to_name, labels=str(self.labels)
            ))

    def predict(self, tasks, **kwargs):
        """
        每次用户开始标注labeling的时候，进行一下预测,
        用户使用页面http://localhost:8080/进行标注的时候，进行一下预测
        :param tasks: 传入过来一条数据，被一条一条预测，有些奇怪
        :param kwargs:
        :return:
        """
        #预测数据格式是[(sentence, apspect_keyword),....]
        data = []
        for task in tasks:
            one_data = (task['data'][self.value], task['data']['keyword'])
            data.append(one_data)
        print(f"开始预测模型: 数据量{len(data)}")
        data = {'data': data}
        headers = {'content-type': 'application/json'}
        r = requests.post(self.predict_url, headers=headers, data=json.dumps(data), timeout=600)
        results = r.json()
        predictions = []
        for one_res in results:
            predicted_label, predict_score = one_res
            # 预测的label, eg: '中性'
            # prediction result for the single task
            result = [{
                'from_name': self.from_name,
                'to_name': self.to_name,
                'type': 'choices',
                'value': {'choices': [predicted_label]}
            }]

            # 把所有样本的预测结果和分数加到predictions后返回
            predictions.append({'result': result, 'score': predict_score})

        return predictions

    def fit(self, completions, workdir=None, **kwargs):
        """
        训练模型, 调用train的api接口时，进行训练，会获取所有已标注完成的数据，如果训练过模型，并且没有新的标注数据时，
        self.train_output会有数据，就不会走到这个训练接口了
        :param completions:
        :param workdir:
        :param kwargs:
        :return:
        """
        #训练数据格式是[(sentence, apspect_keyword,label),....]
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
            input_aspect = completion['data']['keyword']

            #获取标注的样本的label, eg: '中性'
            output_label = completion['completions'][0]['result'][0]['value']['choices'][0]
            output_labels.append(output_label)
            #组成一条训练数据
            one_data = (input_text, input_aspect, output_label)
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

        print("开始训练模型: 数据量{len(data)}")
        #构造请求，发送数据，让模型开始训练
        data = {'data': data}
        headers = {'content-type': 'application/json'}
        r = requests.post(self.train_url, headers=headers, data=json.dumps(data), timeout=600)
        print(f"训练结果{r.json()}")

        # eg: {'labels': ['积极', '消极', '中性'], 'model_file': 'my_ml_backend/text_classification_project1a43/1608621143/model.pkl'}
        train_output = {
            'labels': self.labels,
            'model_file': "model_file"
        }
        return train_output
