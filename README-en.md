# [PSAT](http://www.yatenglg.cn/psat) - Point cloud segmentation annotation tools
[中文](README.md) [English](README-en.md)

![psat.png](example/pic/psat.png)

## Annotate

Select the point cloud through the polygon box, and select the category.
![标注.png](example/pic/标注.png)
## Results
Semantic segmentation
![类别.png](example/pic/类别.png)
Instance segmentation
![实例.png](example/pic/实例.png)

## Install

```shell
git clone https://github.com/yatengLG/PSAT.git
cd PSAT
conda create -n PSAT python==3.8
conda activate PSAT
pip install -r requests.txt
```

## Ground filter
Software integrated with [CSF](https://github.com/jianboqi/CSF)，and provide the function of quickly extracting the ground 。
The software turns off the ground filtering function by default. 
Manually install the [CSF](https://github.com/jianboqi/CSF#how-to-use-csf-in-python), and then automatically turn on the ground filtering function.


