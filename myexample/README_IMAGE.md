# 图像的应用
## 目标检测 Image object detection
### 文档: https://labelstud.io/templates/image_bbox.html
### 初始化项目
```buildoutcfg
label-studio init --template=image_bbox image_object_detection
label-studio start image_object_detection
#或者
label_studio/server.py start image_object_detection -b
```
### 标注的配置, 注意设置标签的类别
```buildoutcfg
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="Airplane" background="green"/>
    <Label value="Car" background="blue"/>
  </RectangleLabels>
</View>
```
## 使用api
image_api.py

## 导入图片的方式
### 文档: https://labelstud.io/guide/tasks.html#Directory-with-image-files
#### 方法1， 通过目录导入，在初始化阶段目录就有图片
label-studio init -i /my/dataset/images --input-format image-dir
#### 方法2, 通过http或https导入,
Your JSON/CSV/TSV/TXT must contain http/https URLs to them.
* 进入一个图片的目录，启动一个简易的http, 例如： python3 -m http.server 9090
* 扫描每张图片，并通过api上传的格式如:
```buildoutcfg
    data = [{'image': 'http://127.0.0.1:9090/IMG_1505.JPG'},
            {'image': 'http://127.0.0.1:9090/IMG_1506.JPG'}]
    r = requests.post(host + "project/import", data=json.dumps(data), headers=headers)
    pp.pprint(r.json())
```

### 标注后导出为COCO格式
```buildoutcfg
pip install git+https://github.com/heartexlabs/label-studio-converter.git
# 导出的结果
2021-02-18-17-55-04-COCO/
├── images
│   ├── IMG_1505_2101.JPG     #图片名称+md5部分字段+后缀
│   └── IMG_1506_c2fe.JPG
└── result.json     #数据标注结果

```
如果导出YOLO格式, 待开发
```buildoutcfg
pip install git+https://github.com/johnson7788/label-studio-converter.git
```
