视频教程：https://www.bilibili.com/video/BV1LHUkYzEwY/?vd_source=a5cc056412c15f2af87af6c95f56941d
![UI Components Overview/UI组件界面](https://github.com/kuieless/Aids-for-X-anylabeling/blob/master/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20241118173717.png)
# 创建环境
conda create --name x4 python==3.10
conda activate x4
# 克隆镜像
1、git clone https://github.com/CVHub520/X-AnyLabeling.git
2、git clone https://github.com/kuieless/Aids-for-X-anylabeling.git
3、cd X-AnyLabeling
4、pip install -r requirements-gpu.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

（5）、pip install pyqt5-tools -i https://pypi.tuna.tsinghua.edu.cn/simple
            python.exe -m pip install --upgrade pip

5、python anylabeling/app.py
出现错误： 'utf-8' codec can't decode byte 0xcc in position 198: invalid continuation byte

### 使用我的aid目录的文件。
6、将model-manager.py 替换放到X-AnyLabeling\anylabeling\services\auto_labeling\model_manager.py
7、python anylabeling/app.py


### 然后开始自己拉框，比如你有1k张图片，可以先做100张，然后去跑yolov8或者v11的模型，100个轮次，之后将pt文件转化为onnx，使用export.py（v11自带，v8不确定，去csdn上有教程）

8、yaml同级文件夹中放你训练好的v8或者v11等的转换成onnx的模型。
9、在使用自动标注的时候，加载的是yaml文件，按照我给的module文件夹里，修改yaml文件中的参数来指定onnx模型。

### 然后开始自动标注，置信率可以低一点设置0.3左右，交并比设置为0.3-0.7左右，自动标注完成后手动检查一遍。自动标注后得到的是json格式文件，按需转化成yolo格式。

### 10、rectangle-json2yolo.py是我自己做的json转yolo的脚本





















