# [PSAT](http://www.yatenglg.cn/psat) - 点云分割标注工具
![psat.png](example/pic/标注.gif)

[中文](README.md) [English](README-en.md)

# 简介
深度学习点云分割标注工具

1. 实现十万级别点云流畅标注,百万级别点云流畅可视化
2. 支持同时标注语义分割与实例分割

# 安装

```shell
git clone https://github.com/yatengLG/PSAT.git
cd PSAT
conda create -n PSAT python==3.8
conda activate PSAT
pip install -r requests.txt
```

# 使用
1. 在设置中预先配置类别标签（通过导入或导出类别配置，快速在不同任务之间切换）
2. 打开点云文件，绘制多边形进行框选
3. 框选过程可以通过切换高程渲染或真彩渲染，提高点云辨识度，也可以隐藏部分类别，减少标注干扰
4. 标注文件保存为json格式，文件中保存了：原始点云路径、类别id与类别对应字典、类别id、实例id
5.打开点云时，若存在对应标注文件，会加载类别与实例信息（切换任务时，记得修改类别设置）
![psat.png](example/pic/展示.gif)

# 额外功能
## 地面提取
软件集成了[CSF布料滤波](https://github.com/jianboqi/CSF)算法，提供快速提取地面的功能。
软件默认关闭地面滤波功能，手动安装[CSF](https://github.com/jianboqi/CSF#how-to-use-csf-in-python)后，自动开启。
