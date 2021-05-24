# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path

from label_studio.ml import LabelStudioMLBase
from label_studio.ml.utils import get_image_local_path, get_image_size, get_single_tag_keys
from label_studio.utils.io import json_load
import requests
import json

logger = logging.getLogger(__name__)


class YOLODetection(LabelStudioMLBase):
    """Object detector based on https://github.com/open-mmlab/mmdetection"""

    def __init__(self, labels_file=None, score_threshold=0.3, device='cpu', **kwargs):
        """
        Load MMDetection model from config and checkpoint into memory.
        (Check https://mmdetection.readthedocs.io/en/v1.2.0/GETTING_STARTED.html#high-level-apis-for-testing-images)

        Optionally set mappings from COCO classes to target labels
        :param labels_file: file with mappings from COCO labels to custom labels {"airplane": "Boeing"}
        :param score_threshold: score threshold to wipe out noisy results
        :param device: device (cpu, cuda:0, cuda:1, ...)
        :param kwargs:
        """
        super(YOLODetection, self).__init__(**kwargs)
        #训练功能暂未实现
        self.train_url = "http://127.0.0.1:5000/api/train"
        # self.predict_url = "http://127.0.0.1:5000/api/predict"
        #图片的临时保存路径
        self.save_dir = '/tmp'
        self.from_name, self.to_name, self.value, self.labels_in_config = get_single_tag_keys(
            self.parsed_label_config, 'RectangleLabels', 'Image')
        schema = list(self.parsed_label_config.values())[0]
        #eg:  {'公式', '表格', '图像'}
        self.labels_in_config = set(self.labels_in_config)

        # eg: {'表格': {'value': '表格', 'background': 'green'}, '图像': {'value': '图像', 'background': 'blue'}, '公式': {'value': '公式', 'background': 'red'}}
        self.labels_attrs = schema.get('labels_attrs')
        if self.labels_in_config == {'段落', '标题'}:
            self.predict_url = "http://127.0.0.1:5001/api/predict"
        elif self.labels_in_config == {'段落'}:
            self.predict_url = "http://127.0.0.1:5001/api/predict"
        else:
            self.predict_url = "http://127.0.0.1:5000/api/predict"
    def download_file(sefl, url, save_dir):
        """
        我们返回绝对路径
        :param url: eg: http://127.0.0.1:9090/2007.158710001-01.jpg
        :param save_dir: eg: /tmp/
        :return:  /tmp/2007.158710001-01.jpg
        """
        local_filename = url.split('/')[-1]
        save_dir_abs = Path(save_dir).absolute()
        save_file = os.path.join(save_dir_abs, local_filename)
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(save_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return save_file

    def predict(self, tasks, **kwargs):
        #一次预测一张图片
        assert len(tasks) == 1
        task = tasks[0]
        # eg: 是一个url路径 'http://192.168.50.86:9090/Chinese_Grammatical_Correction_Using_BERT-based_Pre-trained_Model0001-1.jpg'
        image_path = task['data']['image']
        #api可以接收多张图片
        image_data = [image_path]
        print(f"开始预测模型: 数据量{len(task)}")
        data = {'data': image_data}
        headers = {'content-type': 'application/json'}
        r = requests.post(self.predict_url, headers=headers, data=json.dumps(data), timeout=600)
        model_results = r.json()
        # 如果图片没有检测到目标，那么返回为空
        results = []
        all_scores = []
        # image_path 是url，需要下载后获取图片的尺寸
        image_local_path = self.download_file(url=image_path, save_dir=self.save_dir)
        img_width, img_height = get_image_size(image_local_path)
        # 获取到之后就可以删掉图片了
        print(f'图片的尺寸为高度宽度{img_height}x{img_width}')
        os.remove(image_local_path)
        for res in model_results:
            # 每张图片, 这里是一张图片, res包含4个元素，每个元素的内容如下, 循环每个bboxes
            images, bboxes, confidences, labels, image_size = res
            for bbox, score, output_label in zip(bboxes, confidences, labels):
                # 这里处理每个bbox， 一个bbox对应的标签，
                if output_label not in self.labels_in_config:
                    print(output_label + ' label不在配置文件中，请检查')
                    continue
                bbox = list(bbox)
                # 有的图片是没有检测到目标的，那么bbox就是空列表，我们就会过滤掉
                if not bbox:
                    continue
                #获取左上角和右下角的坐标
                x, y, xmax, ymax = bbox
                #下面转换成百分比的形式, 注意用float，否则会丧失部分精度
                results.append({
                    'from_name': self.from_name,
                    'to_name': self.to_name,
                    'type': 'rectanglelabels',
                    'value': {
                        'rectanglelabels': [output_label],
                        'x': float(x / img_width * 100),
                        'y': float(y / img_height * 100),
                        'width': float((xmax - x) / img_width * 100),
                        'height': float((ymax - y) / img_height * 100)
                    },
                    'score': score
                })
                all_scores.append(score)
        if all_scores:
            #如果没有bbox，那么score也是0
            avg_score = sum(all_scores) / len(all_scores)
        else:
            avg_score = 0.0
        return [{
            'result': results,
            'score': avg_score
        }]

    def fit(self, completions, workdir=None, **kwargs):
        project_path = kwargs.get('project_full_path')
        if os.path.exists(project_path):
            logger.info('Found project in local path ' + project_path)
        else:
            logger.error('Project not found in local path ' + project_path + '. Serving uploaded data will fail.')
        return {'project_path': project_path}
