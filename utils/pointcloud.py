# -*- coding: utf-8 -*-
# @Author  : LG

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from multiprocessing import Pool
import laspy
from plyfile import PlyData


def las_read(file_path) -> (np.ndarray, np.ndarray, np.ndarray):
    data = laspy.read(file_path)
    vertices = np.vstack((data.x, data.y, data.z)).transpose()
    try:
        rgb = np.vstack((data.red, data.green, data.blue)).transpose()
        rgb = rgb >> 8
        rgb = rgb / 255
    except:
        rgb = np.zeros(vertices.shape)
        print('LasData object has no attribute [red, green, blue], {}'.format(data.point_format))
    vertices = vertices.astype(np.float32)
    rgb = rgb.astype(np.float32)
    xmin, ymin, zmin = min(vertices[:, 0]), min(vertices[:, 1]), min(vertices[:, 2])
    xmax, ymax, zmax = max(vertices[:, 0]), max(vertices[:, 1]), max(vertices[:, 2])
    vertices -= (xmin, ymin, zmin)

    offset = data.header.offset + np.array([xmin, ymin, zmin])
    size = np.array((xmax - xmin, ymax - ymin, zmax - zmin))
    return vertices, rgb, size, offset


def ply_read(file_path):
    ply_data = PlyData.read(file_path)
    if 'vertex' not in ply_data:
        return np.array([]), np.array([]), np.array([0, 0, 0]), np.array([0, 0, 0])

    vertices = np.vstack((ply_data['vertex']['x'],
                          ply_data['vertex']['y'],
                          ply_data['vertex']['z'])).transpose()
    if 'red' in ply_data['vertex']:
        colors = np.vstack((ply_data['vertex']['red'],
                            ply_data['vertex']['green'],
                            ply_data['vertex']['blue'])).transpose()
    else:
        colors = np.ones(vertices.shape)

    vertices = vertices.astype(np.float32)
    xmin, ymin, zmin = min(vertices[:, 0]), min(vertices[:, 1]), min(vertices[:, 2])
    xmax, ymax, zmax = max(vertices[:, 0]), max(vertices[:, 1]), max(vertices[:, 2])
    size = np.array((xmax - xmin, ymax - ymin, zmax - zmin))
    offset = np.array([xmin, ymin, zmin])
    vertices -= offset
    colors = colors.astype(np.float32)
    colors = colors / 255
    return vertices, colors, size, offset


def txt_read(file_path) -> (np.ndarray, np.ndarray, np.ndarray):
    '''
    txt格式存储的点云。
    每行代表一个点，共六列分别为x, y, z, r, g, b
    rgb值为0-255
    :param file_path:
    :return:
    '''
    datas = np.loadtxt(file_path)
    datas = datas.astype(np.float32)
    vertices = datas[:, :3]
    rgb = datas[:, 3:6]
    xmin, ymin, zmin = min(vertices[:, 0]), min(vertices[:, 1]), min(vertices[:, 2])
    xmax, ymax, zmax = max(vertices[:, 0]), max(vertices[:, 1]), max(vertices[:, 2])
    vertices -= (xmin, ymin, zmin)
    rgb = rgb / 255
    offset = np.array([xmin, ymin, zmin])
    size = np.array((xmax - xmin, ymax - ymin, zmax - zmin))
    return vertices, rgb, size, offset


class PointCloud:
    def __init__(self, file_path:str, xyz, rgb, size, offset):
        self.file_path:str = file_path
        self.xyz:np.ndarray = xyz if xyz.dtype == np.float32 else xyz.astype(np.float32)
        self.offset:np.ndarray = offset
        self.size:np.ndarray = size
        self.num_point = self.xyz.shape[0]
        self.rgb:np.ndarray = rgb if rgb.dtype == np.float32 else rgb.astype(np.float32)

    def __str__(self):
        return "<PointCloud num_point: {} | size: ({:.2f}, {:.2f}, {:.2f}) | offset: ({:.2f}, {:.2f}, {:.2f}) >".format(
            self.num_point, self.size[0], self.size[1], self.size[2], self.offset[0], self.offset[1], self.offset[2])


class PointCloudReadThread(QThread):
    message = pyqtSignal(str, int)
    tag = pyqtSignal(bool)

    def __init__(self):
        super(PointCloudReadThread, self).__init__()
        self.file_path = None
        self.callback = None
        self.pointcloud = None

    def run(self):
        self.message.emit("Open file | Loading ...", 10000000)    # 一直显示

        pool = Pool()
        p = pool.apply_async(func=self.read, args=(self.file_path,), callback=self.callback)
        pool.close()
        pool.join()

        self.pointcloud = p.get()
        self.message.emit("Open file | Load point cloud finished.", 1000)
        self.tag.emit(True)

    @staticmethod
    def read(file_path:str):
        if file_path.endswith('.las'):
            xyz, rgb, size, offset = las_read(file_path)
        elif file_path.endswith('.ply'):
            xyz, rgb, size, offset = ply_read(file_path)
        elif file_path.endswith('.txt'):
            xyz, rgb, size, offset = txt_read(file_path)
        else:
            return None
        pointcloud = PointCloud(file_path, xyz, rgb, size, offset)
        return pointcloud

    def __del__(self):
        self.wait()

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_callback(self, callback):
        self.callback = callback
