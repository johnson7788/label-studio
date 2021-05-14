<<<<<<< HEAD
# 概述
需要启动ML后端和 label_studio的服务端


# 如果存在redis，那么任务状态会存在redis中，否则存在本地目录下
```buildoutcfg
my_ml_backend/text_classification_project1a43/
├── 1608619078     #按时间排序生成
│   ├── job_result.json    模型的训练结果  eg:  {"status": "ok", "train_output": {"labels": ["\u79ef\u6781", "\u6d88\u6781", "\u4e2d\u6027"], "model_file": "my_ml_backend/text_classification_project1a43/1608621143/model.pkl"}, "project": "text_classification_project1a43", "workdir": "my_ml_backend/text_classification_project1a43/1608621143", "version": "1608621143", "job_id": null, "time": 807.088093996048}
│   ├── model.pkl          训练完成的模型
│   ├── train_data.json    训练数据, 是人工标注的数据集，从label-studio获取的的
│   └── train_data_info.json   训练数据信息   {"count": 4}
└── 1608621143
    ├── job_result.json
    ├── model.pkl
    ├── train_data.json
    └── train_data_info.json
```

# ML后端
使用label-studio-ml启动，调用label_studio/ml/server.py和 label_studio/ml/api.py, label_studio/ml/model.py 
实际启动的是(方便debug): python {项目名}/_wsgi.py 额外参数  eg: python my_ml_backend/_wsgi.py --log-level DEBUG --debug

# label_studio的服务端
使用label-studio启动，调用label_studio/server.py和label_studio/blueprint.py

## Quickstart
这是有关如何使用简单的文本分类器，运行ML后端的快速教程 

0. Clone repo
   ```bash
   git clone https://github.com/heartexlabs/label-studio  
   ```
   
1. Setup environment
   ```bash
   cd label-studio
   pip install -e .
   cd label_studio/ml/examples
   pip install -r requirements.txt
   ```
   
2. Create new ML backend,  你也可以修改simple_text_classifier.py，生成自己的脚本
   ```bash
   label-studio-ml init my_ml_backend --script label_studio/ml/examples/simple_text_classifier.py
   ```
   
3. 启动ML后端服务器
   ```bash
   label-studio-ml start my_ml_backend
   ```
   
4. 运行Label Studio，将其连接到正在运行的ML后端 :
    ```bash
    label-studio start text_classification_project --init --template text_classification --ml-backends http://localhost:9090
    ```

## 自定义的脚本
label-studio/ml/examples/simple_text_classifier.py
需要实现fit训练方法，和predict预测的方法

## 创建自己的ML后端 

Check examples in `label-studio/ml/examples` directory.
=======
# Warning

Since v1.0 this folder was moved to another repository Label Studio ML Backend :

https://github.com/heartexlabs/label-studio-ml-backend/tree/master/label_studio_ml
>>>>>>> upstream/master
