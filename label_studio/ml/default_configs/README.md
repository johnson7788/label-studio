##  默认配置文件

## Quickstart

构建并启动机器学习后端  `http://localhost:9090`

```bash
docker-compose up
```

检查health:

```bash
$ curl http://localhost:9090/health
{"status":"UP"}
```

然后将运行中的后端连接到Label Studio :

```bash
label-studio start --init new_project --ml-backends http://localhost:9090 --template image_classification
```

## 编写自己的模型 
1.将用于模型训练和推理的脚本放在根目录中。 
请遵循下面介绍的[API guidelines](#api-guidelines) 
您可以将所有内容放在一个文件中，也可以创建2个单独的文件，例如`my_training_module.py` and `my_inference_module.py`

2. 写下您的python依赖项 `requirements.txt`

3. 打开`wsgi.py`并在 `init_model_server` 参数下进行配置 
    ```python
    from my_training_module import training_script
    from my_inference_module import InferenceModel
   
    init_model_server(
        create_model_func=InferenceModel,
        train_script=training_script,
        ...
    ```

4. 确保在系统上安装了docker＆docker-compose，然后运行 
    ```bash
    docker-compose up --build
    ```
   
## API guidelines


#### Inference module
为了创建推理模块，您必须声明以下类：

```python
from htx.base_model import BaseModel

# use BaseModel inheritance provided by pyheartex SDK 
class MyModel(BaseModel):
    
    # Describe input types (Label Studio object tags names)
    INPUT_TYPES = ('Image',)

    # Describe output types (Label Studio control tags names)
    INPUT_TYPES = ('Choices',)

    def load(self, resources, **kwargs):
        """Here you load the model into the memory. resources is a dict returned by training script"""
        self.model_path = resources["model_path"]
        self.labels = resources["labels"]

    def predict(self, tasks, **kwargs):
        """Here you create list of model results with Label Studio's prediction format, task by task"""
        predictions = []
        for task in tasks:
            # do inference...
            predictions.append(task_prediction)
        return predictions
```

#### Training module
训练可以在单独的环境中进行。 
唯一的约定是，将数据迭代器和工作目录指定为训练函数的输入参数，
训练函数将输出可序列化的JSON资源，稍后由推理模块中的load()函数使用。 

```python
def train(input_iterator, working_dir, **kwargs):
    """Here you gather input examples and output labels and train your model"""
    resources = {"model_path": "some/model/path", "labels": ["aaa", "bbb", "ccc"]}
    return resources
```
