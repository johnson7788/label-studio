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
   label-studio-ml init my_ml_backend --script label-studio/ml/examples/simple_text_classifier.py
   ```
   
3. Start ML backend server
   ```bash
   label-studio-ml start my_ml_backend
   ```
   
4. Run Label Studio connecting it to the running ML backend:
    ```bash
    label-studio start text_classification_project --init --template text_sentiment --ml-backends http://localhost:9090
    ```

## 自定义的脚本
label-studio/ml/examples/simple_text_classifier.py
需要实现fit训练方法，和predict预测的方法

## 创建自己的ML后端 

Check examples in `label-studio/ml/examples` directory.
