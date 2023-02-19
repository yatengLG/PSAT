# -*- coding: utf-8 -*-
# @Author  : LG

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QVector3D, QMatrix4x4, QQuaternion, QVector2D, QVector4D, QPolygonF
from PyQt5.QtCore import QPointF
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GL import *
import numpy as np
from camera import Camera
from transform import Transform
from math import pi, cos, sin
from enum import Enum
from collections import namedtuple
import imgviz
from configs import MODE, DISPLAY


CATEGORY = namedtuple('CATEGORY', ['id', 'name', 'color'])

class GLWidget(QGLWidget):
    def __init__(self, parent, mainwindow):
        super(GLWidget, self).__init__(parent)
        self.setMouseTracking(True)
        self.mainwindow = mainwindow
        self.pointcloud = None
        self.categorys:np.ndarray = None
        self.instances:np.ndarray = None

        self.mask:np.ndarray = None                 # 显示用掩码
        self.category_display_state_dict = {}
        self.instance_display_state_dict = {}

        self.current_vertices:np.ndarray = None       # doubel
        self.current_colors:np.ndarray = None       # doubel
        self.elevation_color:np.ndarray = None
        self.category_color:np.ndarray = None
        self.instance_color:np.ndarray = None


        self.mode:MODE = MODE.VIEW_MODE
        self.display:DISPLAY = DISPLAY.RGB

        self.point_size = 1
        self.pickpoint_radius = 1  # 点拾取半径
        self.show_size:int = 60
        self.show_circle = False
        self.ortho_change_scale = 1
        self.ortho_change_rate = 0.95
        self.center_vertex = QVector3D(0, 0, 0)

        self.vertex_transform = Transform()
        self.circle_transform = Transform()
        self.axes_transform = Transform()
        self.keep_transform = Transform()
        self.projection = QMatrix4x4()
        self.camera = Camera()

        self.color_map = np.array(imgviz.label_colormap(), dtype=np.float32) / 255
        self.color_map[0] = [1, 1, 1]
        self.mouse_left_button_pressed = False
        self.mouse_right_button_pressed = False
        self.lastX, self.lastY = None, None
        self.polygon_vertices:list = []

    def init_vertex_shader(self):
        vertex_src = """
        # version 330 core
        layout(location = 0) in vec3 a_pos;
        layout(location = 1) in vec3 a_color;
        out vec3 v_color;

        uniform mat4 model;
        uniform mat4 projection;
        uniform mat4 view;

        void main(){
            gl_Position = projection * view * model * vec4(a_pos, 1.0);
            v_color = a_color;
        }
        """
        fragment_src = """
        # version 330 core
        in vec3 v_color;
        out vec4 out_color;

        void main(){
            out_color = vec4(v_color, 1.0);
        }
        """
        self.vertex_shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        glUseProgram(self.vertex_shader)

        self.model_loc = glGetUniformLocation(self.vertex_shader, 'model')
        self.view_loc = glGetUniformLocation(self.vertex_shader, 'view')
        self.proj_loc = glGetUniformLocation(self.vertex_shader, 'projection')
        glUseProgram(0)

    def init_vertex_vao(self):
        self.vertex_vao = glGenVertexArrays(1)

        vbos = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, vbos[0])
        glBufferData(GL_ARRAY_BUFFER, self.current_vertices.nbytes, self.current_vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, vbos[1])
        glBufferData(GL_ARRAY_BUFFER, self.current_colors.nbytes, self.current_colors, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(self.vertex_vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbos[0])
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.current_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, vbos[1])
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.current_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)

    def init_axes_vao(self):
        def createcircle(center:QVector3D, radius, num_point):
            xs, ys, zs = [], [], []
            angle = pi * 2 / num_point
            cx, cy, cz = center.x(), center.y(), center.z()
            for i in range(num_point):
                xs.append(cx + radius * cos(angle * i))
                ys.append(cy + radius * sin(angle * i))
                zs.append(cz)
            return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.float32), np.array(zs, dtype=np.float32)

        num_point = 360
        radius = 1
        # 轴
        self.axes_x_vertices = np.array([0, 0, 0, radius, 0, 0], dtype=np.float32)
        self.axes_x_colors = np.array([1, 0, 0, 1, 0, 0], dtype=np.uint16)
        self.axes_y_vertices = np.array([0, 0, 0, 0, radius, 0], dtype=np.float32)
        self.axes_y_colors = np.array([0, 1, 0, 0, 1, 0], dtype=np.uint16)
        self.axes_z_vertices = np.array([0, 0, 0, 0, 0, radius], dtype=np.float32)
        self.axes_z_colors = np.array([0, 0, 1, 0, 0, 1], dtype=np.uint16)

        self.axes_vaos = glGenVertexArrays(3)   # xyz轴
        axes_vbos = glGenBuffers(6)

        glBindVertexArray(self.axes_vaos[0])  # x轴
        glBindBuffer(GL_ARRAY_BUFFER, axes_vbos[0])
        glBufferData(GL_ARRAY_BUFFER, self.axes_x_vertices.nbytes, self.axes_x_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.axes_x_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, axes_vbos[1])
        glBufferData(GL_ARRAY_BUFFER, self.axes_x_colors.nbytes, self.axes_x_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_SHORT, GL_FALSE, self.axes_x_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glBindVertexArray(self.axes_vaos[1])  # y轴
        glBindBuffer(GL_ARRAY_BUFFER, axes_vbos[2])
        glBufferData(GL_ARRAY_BUFFER, self.axes_y_vertices.nbytes, self.axes_y_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.axes_y_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, axes_vbos[3])
        glBufferData(GL_ARRAY_BUFFER, self.axes_y_colors.nbytes, self.axes_y_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_SHORT, GL_FALSE, self.axes_y_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glBindVertexArray(self.axes_vaos[2])  # z轴
        glBindBuffer(GL_ARRAY_BUFFER, axes_vbos[4])
        glBufferData(GL_ARRAY_BUFFER, self.axes_z_vertices.nbytes, self.axes_z_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.axes_z_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, axes_vbos[5])
        glBufferData(GL_ARRAY_BUFFER, self.axes_z_colors.nbytes, self.axes_z_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_SHORT, GL_FALSE, self.axes_z_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # 环
        xs, ys, zs = createcircle(QVector3D(0, 0, 0), radius, num_point)
        self.circle_x_vertices = np.dstack([zs, xs, ys])
        self.circle_x_colors = np.array([1, 0, 0] * num_point, dtype=np.uint16)
        self.circle_y_vertices = np.dstack([ys, zs, xs])
        self.circle_y_colors = np.array([0, 1, 0] * num_point, dtype=np.uint16)
        self.circle_z_vertices = np.dstack([xs, ys, zs])
        self.circle_z_colors = np.array([0, 0, 1] * num_point, dtype=np.uint16)

        self.circle_vaos = glGenVertexArrays(3)  # xyz环
        circle_vbos = glGenBuffers(6)

        glBindVertexArray(self.circle_vaos[0])  # x环
        glBindBuffer(GL_ARRAY_BUFFER, circle_vbos[0])
        glBufferData(GL_ARRAY_BUFFER, self.circle_x_vertices.nbytes, self.circle_x_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.circle_x_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, circle_vbos[1])
        glBufferData(GL_ARRAY_BUFFER, self.circle_x_colors.nbytes, self.circle_x_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_SHORT, GL_FALSE, self.circle_x_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glBindVertexArray(self.circle_vaos[1])  # y环
        glBindBuffer(GL_ARRAY_BUFFER, circle_vbos[2])
        glBufferData(GL_ARRAY_BUFFER, self.circle_y_vertices.nbytes, self.circle_y_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.circle_y_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, circle_vbos[3])
        glBufferData(GL_ARRAY_BUFFER, self.circle_y_colors.nbytes, self.circle_y_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_SHORT, GL_FALSE, self.circle_y_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glBindVertexArray(self.circle_vaos[2])  # z环
        glBindBuffer(GL_ARRAY_BUFFER, circle_vbos[4])
        glBufferData(GL_ARRAY_BUFFER, self.circle_z_vertices.nbytes, self.circle_z_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.circle_z_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, circle_vbos[5])
        glBufferData(GL_ARRAY_BUFFER, self.circle_z_colors.nbytes, self.circle_z_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_SHORT, GL_FALSE, self.circle_z_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def init_polygon_vao(self):
        #
        if self.polygon_vertices is None:
            return
        polygon_vertices = np.array(self.polygon_vertices, dtype=np.float32)
        self.polygon_colors = np.array([0.5, 0.5, 0.5] * polygon_vertices.shape[0], dtype=np.uint16)

        self.polygon_vaos = glGenVertexArrays(1)
        polygon_vbos = glGenBuffers(2)

        glBindVertexArray(self.polygon_vaos)
        glBindBuffer(GL_ARRAY_BUFFER, polygon_vbos[0])
        glBufferData(GL_ARRAY_BUFFER, polygon_vertices.nbytes, polygon_vertices, GL_STREAM_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, polygon_vertices.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ARRAY_BUFFER, polygon_vbos[1])
        glBufferData(GL_ARRAY_BUFFER, self.polygon_colors.nbytes, self.polygon_colors, GL_STREAM_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_UNSIGNED_SHORT, GL_FALSE, self.polygon_colors.itemsize * 3, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def initializeGL(self):
        self.init_vertex_shader()
        self.init_axes_vao()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.44, 0.62, 0.81, 1)

    def set_background_color(self, red, green, blue, alpha=1):
        glClearColor(red, green, blue, alpha)
        self.update()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.paintAxes()
        self.paintCircle()
        glPointSize(self.point_size)

        if self.pointcloud is not None:
            glUseProgram(self.vertex_shader)
            glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, self.vertex_transform.toMatrix().data())
            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.camera.toMatrix().data())
            glBindVertexArray(self.vertex_vao)
            glDrawArrays(GL_POINTS, 0, int(self.current_vertices.nbytes / self.current_vertices.itemsize/3))
            glUseProgram(0)

        if self.polygon_vertices is not None:
            glUseProgram(self.vertex_shader)
            glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, self.keep_transform.toMatrix().data())
            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.camera.toMatrix().data())

            self.init_polygon_vao()
            glBindVertexArray(self.polygon_vaos)
            polygon_vertices = np.array(self.polygon_vertices, dtype=np.float32)
            glDrawArrays(GL_LINE_STRIP, 0, int(polygon_vertices.nbytes / polygon_vertices.itemsize / 3))
            glUseProgram(0)

    def paintAxes(self):
        glUseProgram(self.vertex_shader)
        # 坐标固定位置
        self.axes_transform.setTranslation((self.width() / 2 - self.show_size - 20) * self.ortho_change_scale,
                                           (self.height() / 2 - self.show_size - 20) * self.ortho_change_scale,
                                           1000)
        self.axes_transform.setScale(self.show_size * self.ortho_change_scale,
                                     self.show_size * self.ortho_change_scale,
                                     self.show_size * self.ortho_change_scale)
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, self.axes_transform.toMatrix().data())
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.camera.toMatrix().data())
        glBindVertexArray(self.axes_vaos[0])  # x轴
        glDrawArrays(GL_LINE_STRIP, 0, int(self.axes_x_vertices.nbytes / self.axes_x_vertices.itemsize / 3))
        glBindVertexArray(self.axes_vaos[1])  # y轴
        glDrawArrays(GL_LINE_STRIP, 0, int(self.axes_y_vertices.nbytes / self.axes_y_vertices.itemsize / 3))
        glBindVertexArray(self.axes_vaos[2])  # z轴
        glDrawArrays(GL_LINE_STRIP, 0, int(self.axes_z_vertices.nbytes / self.axes_z_vertices.itemsize / 3))
        glUseProgram(0)

    def paintCircle(self):
        glUseProgram(self.vertex_shader)
        # 环固定大小
        scale = (self.height() / 2 * self.ortho_change_scale) / 5 * 4
        self.circle_transform.setScale(scale, scale, scale)
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, self.circle_transform.toMatrix().data())
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.camera.toMatrix().data())
        if self.show_circle == True:
            glBindVertexArray(self.axes_vaos[0])  # x轴
            glDrawArrays(GL_LINE_STRIP, 0, int(self.axes_x_vertices.nbytes / self.axes_x_vertices.itemsize / 3))
            glBindVertexArray(self.axes_vaos[1])  # y轴
            glDrawArrays(GL_LINE_STRIP, 0, int(self.axes_y_vertices.nbytes / self.axes_y_vertices.itemsize / 3))
            glBindVertexArray(self.axes_vaos[2])  # z轴
            glDrawArrays(GL_LINE_STRIP, 0, int(self.axes_z_vertices.nbytes / self.axes_z_vertices.itemsize / 3))
            glBindVertexArray(self.circle_vaos[0])  # x环
            glDrawArrays(GL_LINE_LOOP, 0, int(self.circle_x_vertices.nbytes / self.circle_x_vertices.itemsize / 3))
            glBindVertexArray(self.circle_vaos[1])  # y环
            glDrawArrays(GL_LINE_LOOP, 0, int(self.circle_y_vertices.nbytes / self.circle_y_vertices.itemsize / 3))
            glBindVertexArray(self.circle_vaos[2])  # z环
            glDrawArrays(GL_LINE_LOOP, 0, int(self.circle_z_vertices.nbytes / self.circle_z_vertices.itemsize / 3))
        glUseProgram(0)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        self.projection = QMatrix4x4()
        self.projection.setToIdentity()
        self.projection.ortho(-width / 2 * self.ortho_change_scale, width / 2 * self.ortho_change_scale,
                              -height / 2 * self.ortho_change_scale, height / 2 * self.ortho_change_scale,
                              -300000, 300000)
        glUseProgram(self.vertex_shader)
        glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, self.projection.data())
        glUseProgram(0)

    def pointsize_change(self, value:int):
        self.point_size += value
        if self.point_size < 1: self.point_size = 1
        if self.point_size > 10: self.point_size = 10
        self.update()

    def reset(self):
        self.pointcloud = None
        self.mask:np.ndarray = None
        self.current_vertices: np.ndarray = None
        self.current_colors:np.ndarray = None
        self.elevation_color:np.ndarray = None
        self.instance_color:np.ndarray = None
        self.category_color:np.ndarray = None
        self.categorys:np.ndarray = None
        self.instances:np.ndarray = None

        self.vertex_transform.__init__()
        self.circle_transform.__init__()
        self.camera.__init__()
        self.axes_transform.__init__()
        self.ortho_change_scale = 1

        self.resizeGL(self.width(), self.height())

    def load_vertices(self, pointcloud, categorys:np.ndarray=None, instances:np.ndarray=None):
        self.reset()

        self.pointcloud = pointcloud
        self.vertex_transform.setTranslation(-pointcloud.size[0]/2, -pointcloud.size[1]/2, -pointcloud.size[2]/2)
        self.mask = np.ones(pointcloud.num_point, dtype=bool)
        self.category_display_state_dict = {}
        self.instance_display_state_dict = {}

        self.categorys = categorys if categorys is not None else np.zeros(pointcloud.num_point, dtype=np.int16)
        self.instances = instances if categorys is not None else np.zeros(pointcloud.num_point, dtype=np.int16)
        self.ortho_change_scale = max(pointcloud.size[0] / (self.height() / 5 * 4),
                                      pointcloud.size[1] / (self.height() / 5 * 4))
        self.current_vertices = self.pointcloud.xyz
        self.current_colors = self.pointcloud.rgb
        self.init_vertex_vao()
        self.resizeGL(self.width(), self.height())
        self.update()

    def change_mode_to_pick(self):
        if self.mode == MODE.VIEW_MODE:
            self.mode = MODE.DRAW_MODE
            self.polygon_vertices = []

    def change_mode_to_view(self):
        if self.mode == MODE.DRAW_MODE:
            self.mode = MODE.VIEW_MODE
            self.polygon_vertices = []

    def change_color_to_rgb(self):
        if self.pointcloud is None:
            return
        self.current_vertices = self.pointcloud.xyz[self.mask]
        self.current_colors = self.pointcloud.rgb[self.mask]
        self.display = DISPLAY.RGB
        self.init_vertex_vao()
        self.update()
        self.mainwindow.update_dock()

    def change_color_to_category(self):
        if self.pointcloud is None:
            return
        self.category_color_update()
        self.current_vertices = self.pointcloud.xyz[self.mask]
        self.current_colors = self.category_color[self.mask]
        self.display = DISPLAY.CATEGORY

        self.init_vertex_vao()
        self.update()
        self.mainwindow.update_dock()

    def change_color_to_instance(self):
        if self.pointcloud is None:
            return
        # if self.instance_color is None:
        self.instance_color_update()
        self.current_vertices = self.pointcloud.xyz[self.mask]
        self.current_colors = self.instance_color[self.mask]
        self.display = DISPLAY.INSTANCE
        self.init_vertex_vao()
        self.update()
        self.mainwindow.update_dock()

    def change_color_to_elevation(self):
        if self.pointcloud is None:
            return
        if self.elevation_color is None:
            self.parent().elevation_color_thread_start()
            return
        self.current_vertices = self.pointcloud.xyz[self.mask]
        self.current_colors = self.elevation_color[self.mask]
        self.display = DISPLAY.ELEVATION
        self.init_vertex_vao()
        self.update()
        self.mainwindow.update_dock()

    def category_color_update(self):
        if self.categorys is None:
            return
        self.category_color = np.zeros(self.pointcloud.xyz.shape, dtype=np.float32)
        for id, (category, color) in enumerate(self.parent().category_color_dict.items()):
            color = QtGui.QColor(color)
            self.category_color[self.categorys==id] = (color.redF(), color.greenF(), color.blueF())

    def instance_color_update(self):
        if self.instances is None:
            return
        self.instance_color = np.zeros(self.pointcloud.xyz.shape, dtype=np.float32)
        self.instance_color = self.color_map[self.instances]

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.lastX, self.lastY = event.pos().x(), event.pos().y()

        if self.mode == MODE.DRAW_MODE:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                x, y = event.pos().x() - self.width() / 2, self.height() / 2 - event.pos().y()
                x = x * self.ortho_change_scale
                y = y * self.ortho_change_scale

                if not self.polygon_vertices:
                    self.polygon_vertices = [[x, y, 10000], [x, y, 10000], [x, y, 10000]]
                else:
                    self.polygon_vertices.insert(-1, [x, y, 10000])
            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                # 选择类别与group
                self.mainwindow.category_choice_dialog.load_cfg()
                self.mainwindow.category_choice_dialog.show()
        else:
            self.show_circle = True
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.mouse_left_button_pressed = True
            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                self.mouse_right_button_pressed = True
        self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.show_circle = False
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.mouse_left_button_pressed = False
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.mouse_right_button_pressed = False
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        xpos, ypos = event.pos().x(), event.pos().y()

        if self.mode == MODE.VIEW_MODE:
            if self.mouse_left_button_pressed or self.mouse_right_button_pressed:
                xoffset = xpos - self.lastX
                yoffset = ypos - self.lastY
                self.lastX = xpos
                self.lastY = ypos
                if self.mouse_left_button_pressed:
                    self.mouse_rotate(xoffset, yoffset)
                elif self.mouse_right_button_pressed:
                    self.mouse_move(xoffset, yoffset)
                else:
                    pass

        elif self.mode == MODE.DRAW_MODE:
            x, y = event.pos().x() - self.width() / 2, self.height() / 2 - event.pos().y()
            x = x * self.ortho_change_scale
            y = y * self.ortho_change_scale

            if len(self.polygon_vertices) > 2 :
                self.polygon_vertices[-2] = [x, y, 10000]   # 更新当前点

        self.update()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        x, y = event.pos().x(), self.height() - event.pos().y()
        if self.pointcloud is None:
            return
        point = self.pickpoint(x, y)
        # 双击点移动到坐标中心
        if point.size:
            self.vertex_transform.setTranslationwithRotate(-point[0], -point[1], -point[2])
        self.update()

    def cache_pick(self):
        self.change_mode_to_view()
        self.mask.fill(True)
        self.category_display_state_dict = {}
        self.instance_display_state_dict = {}

        self.mainwindow.save_state = False
        if self.display == DISPLAY.ELEVATION:
            self.change_color_to_elevation()
        elif self.display == DISPLAY.RGB:
            self.change_color_to_rgb()
        elif self.display == DISPLAY.CATEGORY:
            self.change_color_to_category()
        elif self.display == DISPLAY.INSTANCE:
            self.change_color_to_instance()

    def polygon_pick(self, category:int=None, instance:int=None):
        polygon_vertices = self.polygon_vertices
        """
        x, y = event.pos().x() - self.width() / 2, self.height() / 2 - event.pos().y()
                x = x * self.ortho_change_scale
                y = y * self.ortho_change_scale
        """
        for p in polygon_vertices:
            p[0] = p[0] / self.ortho_change_scale + self.width() / 2
            p[1] = self.height() / 2 - p[1] / self.ortho_change_scale
        polygon_vertices = [QPointF(p[0], p[1]) for p in polygon_vertices]
        polygon = QPolygonF(polygon_vertices)
        rect = polygon.boundingRect()

        vertices2D = self.vertices_to_2D()
        l, r, t, b = rect.x(), rect.x() + rect.width(), rect.y(), rect.y() + rect.height()

        mask1 = (l < vertices2D[:, 0]) & (vertices2D[:, 0] < r) & \
               (t < vertices2D[:, 1]) & (vertices2D[:, 1] < b)
        print('mask1: ', sum(mask1))
        mask2 = [polygon.containsPoint(QPointF(p[0], p[1]), QtCore.Qt.FillRule.WindingFill) for p in vertices2D[mask1]]

        print('mask2: ', sum(mask2))
        mask1[mask1 == True] = mask2
        mask = self.mask.copy()
        mask[mask==True] = mask1
        if instance is not None:
            self.instances[mask] = instance
        if category is not None:
            index = list(self.mainwindow.category_color_dict.keys()).index(category)
            self.categorys[mask] = index

        #
        self.mask.fill(True)
        self.category_display_state_dict = {}
        self.instance_display_state_dict = {}

        self.mainwindow.save_state = False
        if self.display == DISPLAY.ELEVATION:
            self.change_color_to_category()
        elif self.display == DISPLAY.RGB:
            self.change_color_to_category()
        elif self.display == DISPLAY.CATEGORY:
            self.change_color_to_category()
        elif self.display == DISPLAY.INSTANCE:
            self.change_color_to_category()

    def pickpoint(self, x, y):
        if self.pointcloud is None:return np.array([])

        point1 = QVector3D(x, y, 0).unproject(self.camera.toMatrix() * self.vertex_transform.toMatrix(),
                                              self.projection,
                                              QtCore.QRect(0, 0, self.width(), self.height()))
        point2 = QVector3D(x, y, 1).unproject(self.camera.toMatrix() * self.vertex_transform.toMatrix(),
                                              self.projection,
                                              QtCore.QRect(0, 0, self.width(), self.height()))
        vector = (point2 - point1)  # 直线向量
        vector.normalize()

        # 点到直线（点向式）的距离
        t = (vector.x() * (self.current_vertices[:, 0] - point1.x()) +
             vector.y() * (self.current_vertices[:, 1] - point1.y()) +
             vector.z() * (self.current_vertices[:, 2] - point1.z())) / (vector.x() ** 2 + vector.y() ** 2 + vector.z() ** 2)

        d = (self.current_vertices[:, 0] - (vector.x() * t + point1.x())) ** 2 + \
            (self.current_vertices[:, 1] - (vector.y() * t + point1.y())) ** 2 + \
            (self.current_vertices[:, 2] - (vector.z() * t + point1.z())) ** 2

        pickpoint_radius = self.pickpoint_radius * self.ortho_change_scale
        mask = d < pickpoint_radius**2

        if not any(mask):
            return np.array([])

        mask1 = self.mask.copy()
        mask1[mask1==True] = mask
        points = self.pointcloud.xyz[mask1]
        index = np.argmin(points[:, 0] * vector.x() + points[:, 1] * vector.y() + points[:, 2] * vector.z())
        point = points[index]   # 取最近的点
        return point

    def wheelEvent(self, event: QtGui.QWheelEvent):
        self.ortho_area_change(event)
        self.update()

    def mouse_rotate(self, xoffset, yoffset):
        # 点云旋转
        self.vertex_transform.rotate(self.vertex_transform.localup, xoffset * 0.5)
        self.vertex_transform.rotate(self.vertex_transform.localright, yoffset * 0.5)
        # 坐标旋转
        self.circle_transform.rotate_in_place(self.circle_transform.localup, xoffset * 0.5)
        self.circle_transform.rotate_in_place(self.circle_transform.localright, yoffset * 0.5)
        self.axes_transform.rotate_in_place(self.axes_transform.localup, xoffset * 0.5)
        self.axes_transform.rotate_in_place(self.axes_transform.localright, yoffset * 0.5)
        self.update()

    def mouse_move(self, xoffset, yoffset):
        self.vertex_transform.translate(xoffset * self.ortho_change_scale, -yoffset * self.ortho_change_scale, 0)
        self.update()

    def ortho_area_change(self, event: QtGui.QWheelEvent):
        angle = event.angleDelta().y()
        if angle < 0:
            self.ortho_change_scale /= self.ortho_change_rate
        elif angle > 0:
            self.ortho_change_scale *= self.ortho_change_rate
        else:
            return
        self.resizeGL(self.width(), self.height())

    def set_right_view(self):
        self.vertex_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.circle_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.axes_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))

        self.vertex_transform.rotate(QVector3D(0, 1, 0), -90)
        self.circle_transform.rotate(QVector3D(0, 1, 0), -90)
        self.axes_transform.rotate(QVector3D(0, 1, 0), -90)
        self.update()

    def set_back_view(self):
        self.vertex_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.circle_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.axes_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.vertex_transform.rotate(QVector3D(0, 1, 0), 180)
        self.circle_transform.rotate(QVector3D(0, 1, 0), 180)
        self.axes_transform.rotate(QVector3D(0, 1, 0), 180)
        self.update()

    def set_top_view(self):
        self.vertex_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), 0))
        self.circle_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), 0))
        self.axes_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), 0))
        self.update()

    def set_left_view(self):
        self.vertex_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.circle_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.axes_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.vertex_transform.rotate(QVector3D(0, 1, 0), 90)
        self.circle_transform.rotate(QVector3D(0, 1, 0), 90)
        self.axes_transform.rotate(QVector3D(0, 1, 0), 90)
        self.update()

    def set_front_view(self):
        self.vertex_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.circle_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.axes_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 270))
        self.update()

    def set_bottom_view(self):
        self.vertex_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), -180))
        self.circle_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), -180))
        self.axes_transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), -180))
        self.update()

    def vertices_to_2D(self):
        if self.pointcloud is None:
            return
        # 转numpy便于计算
        projection = np.array(self.projection.data()).reshape(4, 4)
        camera = np.array(self.camera.toMatrix().data()).reshape(4, 4)
        vertex_transform = np.array(self.vertex_transform.toMatrix().data()).reshape(4, 4)
        # 添加维度
        vertexs = np.hstack((self.current_vertices, np.ones(shape=(self.current_vertices.shape[0], 1))))
        vertexs2model = vertexs.dot(vertex_transform.dot(camera))
        vertexs2projection = vertexs2model.dot(projection)
        # 转换到屏幕坐标
        xys = vertexs2projection[:, :2]
        xys = xys + np.array((1, -1))
        xys = xys * np.array((self.width() / 2, self.height() / 2)) + 1.0
        xys = xys * np.array((1, -1))
        return xys
