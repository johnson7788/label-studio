# 使用示例
所有 label_studio/server.py 都等价于 label-studio命令

# 使用纯文本初始化
label_studio/server.py start labeling_project --template text_classification --input-path=myexample/mytext.txt --input-format=text --init --force --debug -b

# 普通模式

## 初始化一个文本分类的project
label_studio/server.py start labeling_project --template text_classification --init --force --debug -b

## 启动一个已有的project，如果已经初始化
label_studio/server.py start labeling_project --debug -b

# 使用机器学习的后端的模式: Label_studio 加上 ML后端

## 初始化一个ml的后端
label-studio-ml init my_ml_backend --script label_studio/ml/examples/simple_text_classifier.py

## 启动一个ml
方法1：
```buildoutcfg
label-studio-ml start my_ml_backend
```
或方法2：
```buildoutcfg
python my_ml_backend/_wsgi.py --log-level DEBUG --debug
```

## 启动一个label-studio关联ml后端
```
label_studio/server.py start text_classification_project --init --template text_classification --ml-backends http://localhost:9090
```
或者启动一个已有的project
label_studio/server.py  start text_classification_project -b

# 使用多个模型
如果使用2个模型，需要更改config.json配置, 添加一个新，例如ELECTRA，那么需要选择不同的接口,如下
```buildoutcfg
  "ml_backends": [
    {
      "url": "http://localhost:9090",
      "name": "bert_sentiment"
    },
    {
      "url": "http://localhost:9091",
      "name": "electra_sentiment"
    }
  ],
```
然后复制一个my_ml_backend 成一个新的文件夹，启动一个新的
python _wsgi.py --log-level DEBUG --debug --port 9091

# 细粒度情感分析的branch是absa
git checkout absa

1. 启动label-studio --->LS网页端
label_studio/server.py  start text_classification_project -b

2. 启动的ml后端 --->请求自定义的api
label-studio-ml start my_ml_backend

3. 启动自定义的Textbrewer api
python main_api.py
