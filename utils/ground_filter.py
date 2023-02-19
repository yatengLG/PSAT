# -*- coding: utf-8 -*-
# @Author  : LG

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import Pool
try:
    import CSF
    USE_CSF = True
except:
    print('To use ground filtering, please install CSF first: https://github.com/jianboqi/CSF')
    USE_CSF = False


class GroundFilterThread(QThread):
    message = pyqtSignal(str, int)
    tag = pyqtSignal(bool)

    def __init__(self):
        super(GroundFilterThread, self).__init__()
        self.vertices = None
        self.callback = None

    def run(self):
        self.message.emit("Ground filter | Filtering ...", 10000000) # 一直显示
        pool = Pool()
        p = pool.apply_async(func=self.filter, args=(self.vertices,), callback=self.callback)
        pool.close()
        pool.join()
        self.ground = p.get()
        self.message.emit("Ground filter | Filter finished.", 1000)
        self.tag.emit(True)

    @staticmethod
    def filter(vertices: np.ndarray):
        xs = vertices[:, 0]
        ys = vertices[:, 1]
        w , h = int(max(xs) - min(xs)), int(max(ys) - min(ys))
        print('w , h', w*h)
        if w*h > 10000:
            resolution = 0.5
        elif w*h > 100:
            resolution = 0.1
        else:
            resolution = 0.01

        csf = CSF.CSF()
        csf.params.bSloopSmooth = True  #
        csf.params.cloth_resolution = resolution  # 布料分辨率, 网格大小
        csf.params.rigidness = 3  # 布料硬度

        csf.params.time_step = 0.65
        csf.params.class_threshold = 1  # 基于原始点云与模拟地形直接的距离，将原始点云分类为地面和非地面部分的阈值。
        csf.params.interations = 500  # 最大迭代次数

        if vertices.dtype != np.float64:
            vertices = vertices.astype(np.float64)
        csf.setPointCloud(vertices)
        ground = CSF.VecInt()
        non_ground = CSF.VecInt()
        csf.do_filtering(ground, non_ground)
        return np.array(ground)

    def __del__(self):
        self.message.emit("Ground filter thread | Wait for thread to exit.")
        self.wait()
        self.message.emit("Ground filter thread | Thread exited.")

    def set_callback(self, callback):
        self.callback = callback