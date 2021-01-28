import pickle
import os
import numpy as np

import requests
import json
from label_studio.ml import LabelStudioMLBase

class ComponentsTextClassifier(LabelStudioMLBase):

    def __init__(self, **kwargs):
        """
        当调用train或预测的时候会初始化, 需要调用train_model()接口的api
        :param kwargs:
        {'label_config': '<View>  <View style="flex: 30%; color:red">    <Header value="关键字" />    <Text name="keyword" value="$keyword"/>  </View>  <View style="flex: 30%">    <Header value="句子" />    <Text name="text" value="$text"/>    <Choices name="sentiment" toName="text" choice="single">      <Choice value="积极"/>      <Choice value="消极"/>      <Choice value="中性"/>    </Choices>  </View></View>', 'train_output': {'labels': ['中性', '积极'], 'model_file': '/Users/admin/git/label-studio/my_ml_backend/text_classification_project1a43/1608710349/model.pkl'}}
        """
        # don't forget to initialize base class...
        super(ComponentsTextClassifier, self).__init__(**kwargs)

        self.train_url = "http://192.168.50.139:5010/api/train_truncate"
        # self.train_url = "http://127.0.0.1:5000/api/train_truncate"
        self.predict_url = "http://192.168.50.139:5010/api/predict_truncate"
        # self.predict_url = "http://127.0.0.1:5000/api/predict_truncate"

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
        :param tasks: 传入过来一条数据，被一条一条预测，有些奇怪, [{'id': 16, 'data': {'text': '日本花王merit儿童宝宝泡沫洗发水 300ml同系列护发素 180g花王，日本洗护界的大佬这款merit系列的儿童洗发护发用品就是专为1-12岁年龄段孩子开发的，无硅油、无泪配方弱酸性，含水性植物精华，男孩女孩都可以用洗发水和护发素也有区分，挤出来就是丰富浓密的泡沫大点的孩子可以自己学习洗头非常适合对洗发护发有要求的宝贝使用！花王儿童洗发水 300ml日本花王merite儿童泡泡洗发水按一次按四次计算至少可使用75次左右日本宝宝的自理能力都非常强这款洗发水可以使小宝宝对自己洗头产生兴趣慢慢学会洗头，同时它是无硅弱酸性配方，安全不刺激宝宝们一个人也能快乐得洗头，按几下泵丰富泡沫立马出来，洗尽头发各个角落汗和污垢也能轻松去除弱酸性，无硅无泪配方、给宝宝安全的呵护温和洁净配方，去除头皮多余代谢，无硅油天然不刺激丰富细腻的泡泡，可以触碰到头部各个角落宝宝一个人也能轻松清洗非常容易冲洗，不残留强健发质，滋养护发，柔顺易打理花王儿童护发素 180g花王Merit儿童护发素，是无硅油弱酸性的，不会刺激皮肤可以使宝宝对自己的洗发护发产生兴趣用后头发非常柔顺，即使女孩子长头发也能很好梳理不会在打结啦！！白色膏体的护发素易清洗，清晰起来方便又快捷用后头发非常的顺滑小魔王美妆花王merit儿童泡沫洗发300ml/无硅弱酸护发素180g 收起全文d', 'channel': 'weibo', 'keyword': '污垢', 'wordtype': '功效', 'md5': '8d254376a88102e51b6c70f99db65128'}, 'predictions': []}]
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
        result = []
        for one_res in results:
            # eg: one_res: ['中性', 0.9977113604545593, ['宝一个人也能轻松清洗非常容易冲洗，不残留强健发质，滋养护发，柔顺易打理花王儿童护发素 180g花王Mer', '滋养'], [403, 405]]
            predicted_label, predict_score, resdata, locations = one_res
            # 预测的label, eg: '中性'
            # 这个result要和completions标注完成的格式一样
            res = {
                'from_name': self.from_name,
                'to_name': self.to_name,
                'type': 'labels',
                'value': {'labels': [predicted_label],
                          'text': resdata[1],
                          'start':locations[0],
                          'end': locations[1]}
            }
            result.append(res)

            # 把所有样本的预测结果和分数加到predictions后返回
        predictions.append({'result': result, 'score': predict_score})

        return predictions

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
