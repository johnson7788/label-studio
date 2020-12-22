This [Machine Learning backend](https://labelstud.io/guide/ml.html) 允许您使用边框自动为图像加label. 
由 [OpenMMLab MMDetection library](https://github.com/open-mmlab/mmdetection)提供, 
这使您可以访问许多现有的最新模型，例如FasterRCNN，RetinaNet，YOLO等。 

# 图片目标检测算法的示例

查看此安装指南，然后进行操作，选择适合您当前数据集的最佳模型！

## Start using it

1. [Install the model locally](#Installation) or just copy paste this URL: `https://app.labelstud.io`

2. 运行Label Studio，然后转到 **Model** 页面。 粘贴所选的ML后端URL，然后单击 **Add Backend**.

3. Go to **Setup** page, use `COCO annotation` template or `Bbox object detection`.
   (可选)您可以使用`predicted_values`属性修改label配置。 
   它提供了以逗号分隔的COCOlabel列表。 
   如果对象检测器输出这些label中的任何一个，它们将从“value”属性转换为实际的label名称。
    For example:
    
    ```xml
    <Label value="Airplane" predicted_values="airplane"/>
    <Label value="Car" predicted_values="car,truck"/>
    ```
   
意思是: 
- 如果COCO对象检测器预测带有label`"airplane"`的bbox，您最终将看到label `"Airplane"`。 
- if it predicts `"car"` or `"truck"` - they will be squashed to `"Car"` label.

[Here is](#The-full-list-of-COCO-labels) 为了方便起见，COCOlabel的完整labels。 


## Installation

1. Setup MMDetection environment following [this installation guide](https://mmdetection.readthedocs.io/en/v1.2.0/INSTALL.html). Depending on your OS, some of the dependencies could be missed (gcc-c++, mesa-libGL) - install them using your package manager.

2. Create and initialize directory `./coco-detector`:

    ```bash
    label-studio-ml init coco-detector --from label_studio/ml/examples/mmdetection.py
    ```

3. Download `config_file` and `checkpoint_file` from MMDetection model zoo (use [recommended Faster RCNN for quickstarting](https://mmdetection.readthedocs.io/en/latest/1_exist_data_model.html#inference-with-existing-models)).

4. Launch ML backend server:

   ```bash
   label-studio-ml start coco-detector --with \
   config_file=/absolute/path/to/config_file \
   checkpoint_file=/absolute/path/to/checkpoint_file \
   score_threshold=0.5 \
   device=cpu
   ```

> Note: It's highly recommended to use device=gpu:0 if you have a GPU available - it will significantly speed up image prelabeling.

> Note: Feel free to tune `score_threshold` - lower values increase sensitivity but produce more noise.
     

### The full list of COCO labels
```text
airplane
apple
backpack
banana
baseball_bat
baseball_glove
bear
bed
bench
bicycle
bird
boat
book
bottle
bowl
broccoli
bus
cake
car
carrot
cat
cell_phone
chair
clock
couch
cow
cup
dining_table
dog
donut
elephant
fire_hydrant
fork
frisbee
giraffe
hair_drier
handbag
horse
hot_dog
keyboard
kite
knife
laptop
microwave
motorcycle
mouse
orange
oven
parking_meter
person
pizza
potted_plant
refrigerator
remote
sandwich
scissors
sheep
sink
skateboard
skis
snowboard
spoon
sports_ball
stop_sign
suitcase
surfboard
teddy_bear
tennis_racket
tie
toaster
toilet
toothbrush
traffic_light
train
truck
tv
umbrella
vase
wine_glass
zebra
```
