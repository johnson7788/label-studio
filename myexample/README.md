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
my_ml_backend/_wsgi.py --log-level DEBUG --debug
```

## 启动一个label-studio关联ml后端
label_studio/server.py start text_classification_project --init --template text_classification --ml-backends http://localhost:9090
