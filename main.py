# -*- coding: utf-8 -*-
# @Author  : LG

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor
from ui.mainwindow import Ui_MainWindow
from opengl_widget import GLWidget
from functools import partial
import sys
from utils.pointcloud import PointCloudReadThread
from utils.ground_filter import USE_CSF, GroundFilterThread
from utils.elevation import ElevationColorThread
from widgets.category_choice_dialog import CategoryChoiceDialog
from widgets.setting_dialog import SettingDialog
from widgets.about_dialog import AboutDialog
from widgets.shortcut_doalog import ShortCutDialog
from collections import OrderedDict
from configs import load_config, save_config, DEFAULT_CONFIG_FILE, MODE, DISPLAY
from json import load, dump
import functools
import numpy as np
import os


class Mainwindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Mainwindow, self).__init__()
        self.setupUi(self)
        self.openGLWidget=GLWidget(self, self)
        self.setCentralWidget(self.openGLWidget)

        self.actionPick.setEnabled(False)
        self.actionCachePick.setEnabled(False)
        self.dockWidget_files.setVisible(False)
        #
        self.actionClassify.setVisible(False)
        self.actionGround_filter.setVisible(False)
        #

        self.config_file = DEFAULT_CONFIG_FILE
        self.current_file = None
        self.current_root = None
        self.save_state = True
        self.category_choice_dialog = CategoryChoiceDialog(self, self)
        self.setting_dialog = SettingDialog(self, self)
        self.shortcut_dialog = ShortCutDialog(self)
        self.about_dialog = AboutDialog(self)

        self.message = QtWidgets.QLabel('')
        self.statusbar.addPermanentWidget(self.message)

        self.point_cloud_read_thread = PointCloudReadThread()
        self.point_cloud_read_thread.tag.connect(self.point_cloud_read_thread_finished)
        self.point_cloud_read_thread.message.connect(self.show_message)

        if USE_CSF:
            self.actionGround_filter.setVisible(True)
            self.ground_filter_thread = GroundFilterThread()
            self.ground_filter_thread.tag.connect(self.ground_filter_thread_finished)
            self.ground_filter_thread.message.connect(self.show_message)

        self.elevation_color_thread = ElevationColorThread()
        self.elevation_color_thread.tag.connect(self.elevation_color_thread_finished)
        self.elevation_color_thread.message.connect(self.show_message)

        self.category_color_dict:OrderedDict = None

        self.trans = QtCore.QTranslator()

        # 初始化界面
        self.info_widget.setVisible(True)
        self.label_widget.setVisible(False)

        self.init_connect()
        self.reload_cfg()

    def open_file(self):
        self.dockWidget_files.setVisible(False)
        self.listWidget_files.clear()
        file, suffix = QtWidgets.QFileDialog.getOpenFileName(self, caption='point cloud file',
                                                             filter="point cloud (*.las *.ply *.txt)")
        if file:
            if not self.close_point_cloud():
                return
            self.current_root = os.path.split(file)[0]
            self.current_file = file
            self.point_cloud_read_thread_start(file)

    def open_folder(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self)
        if dir:
            self.close_point_cloud()

            self.dockWidget_files.setVisible(True)
            self.listWidget_files.clear()

            self.current_root = dir
            file_list = [file for file in os.listdir(dir) if not file.endswith('.json')]
            for file in file_list:
                item = QtWidgets.QListWidgetItem()
                item.setSizeHint(QtCore.QSize(200, 30))
                item.setText(file)
                self.listWidget_files.addItem(item)

    def double_click_files_widget(self, item:QtWidgets.QListWidgetItem):
        file_path = os.path.join(self.current_root, item.text())
        self.current_file = file_path
        self.point_cloud_read_thread_start(file_path)

    def point_cloud_read_thread_start(self, file_path):
        if file_path.endswith('.las') or file_path.endswith('.ply') or file_path.endswith('.txt'):
            self.point_cloud_read_thread.set_file_path(file_path)   # 传递文件名
            self.point_cloud_read_thread.start()                    # 线程读取文件
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Only support file endwith '.txt', '.ply', '.las'")

    def point_cloud_read_thread_finished(self, tag:bool):
        if tag:
            pointcloud = self.point_cloud_read_thread.pointcloud
            if pointcloud is None:
                return
            #
            label_file = '.'.join(self.current_file.split('.')[:-1]) + '.json'
            categorys = None
            instances = None
            if os.path.exists(label_file):
                with open(label_file, 'r') as f:
                    datas = load(f)
                    info = datas.get('info', '')
                    if info == 'PSAT label file.':
                        categorys = datas.get('categorys', [])
                        instances = datas.get('instances', [])
                        categorys = np.array(categorys, dtype=np.int16)
                        instances = np.array(instances, dtype=np.int16)

                        if categorys.shape[0] != pointcloud.xyz.shape[0] or instances.shape[0] != pointcloud.xyz.shape[0]:
                            QtWidgets.QMessageBox.warning(self, 'Warning', 'Point cloud size does not match label size!')
                            if categorys.shape[0] != pointcloud.xyz.shape[0]:
                                categorys = None
                            if instances.shape[0] != pointcloud.xyz.shape[0]:
                                instances = None
            if pointcloud.num_point < 1:
                return

            self.openGLWidget.load_vertices(pointcloud, categorys, instances)
            #
            self.label_num_point.setText('{}'.format(pointcloud.num_point))
            self.label_size_x.setText('{:.2f}'.format(pointcloud.size[0]))
            self.label_size_y.setText('{:.2f}'.format(pointcloud.size[1]))
            self.label_size_z.setText('{:.2f}'.format(pointcloud.size[2]))
            self.label_offset_x.setText('{:.2f}'.format(pointcloud.offset[0]))
            self.label_offset_y.setText('{:.2f}'.format(pointcloud.offset[1]))
            self.label_offset_z.setText('{:.2f}'.format(pointcloud.offset[2]))

            self.setWindowTitle(pointcloud.file_path)
            self.actionPick.setEnabled(True)
            self.actionCachePick.setEnabled(True)

    def ground_filter_thread_start(self):
        if self.openGLWidget.pointcloud is None:
            return
        if self.openGLWidget.category_color is None:
            self.openGLWidget.category_color_update()

        self.ground_filter_thread.vertices = self.openGLWidget.pointcloud.xyz
        self.ground_filter_thread.start()

    def ground_filter_thread_finished(self, tag:bool):
        if tag:
            ground_index = self.ground_filter_thread.ground
            self.openGLWidget.categorys[ground_index] = 1
            self.openGLWidget.change_color_to_category()
            self.save_state = False

    def elevation_color_thread_start(self):
        if self.openGLWidget.pointcloud is None:
            return
        self.elevation_color_thread.vertices = self.openGLWidget.pointcloud.xyz
        self.elevation_color_thread.start()

    def elevation_color_thread_finished(self, tag):
        if tag:
            self.openGLWidget.elevation_color = self.elevation_color_thread.elevation_color
            self.openGLWidget.change_color_to_elevation()

    def classify_thread_start(self):
        if self.openGLWidget.pointcloud is None:
            return

        self.classify_thread.vertices = self.openGLWidget.pointcloud.xyz[self.openGLWidget.categorys!=1]    # 非地面点
        self.classify_thread.start()

    def classify_thread_finished(self, tag):
        if tag:
            seg, ins = self.classify_thread.seg, self.classify_thread.ins
            self.show_message("Classifier | Up sampling ...", 10000000)
            mask = self.openGLWidget.categorys!=1
            self.openGLWidget.categorys[mask] = seg
            self.openGLWidget.instances[mask] = ins
            self.openGLWidget.category_color_update()
            self.openGLWidget.instance_color_update()
            self.openGLWidget.change_color_to_category()
            self.save_state = False

    def close_point_cloud(self):
        if not self.save_state:
            result = QtWidgets.QMessageBox.question(self, 'Warning', 'Proceed without saved?', QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No)
            if result == QtWidgets.QMessageBox.StandardButton.No:
                return False
        self.current_file = None
        self.openGLWidget.reset()
        self.openGLWidget.update()
        self.message.clear()
        self.save_state = True

        self.setWindowTitle("PSAT - Point Cloud Segmentation Annotation Tool")
        self.info_widget.setVisible(True)
        self.label_num_point.setText('None')
        self.label_size_x.setText('None')
        self.label_size_y.setText('None')
        self.label_size_z.setText('None')
        self.label_offset_x.setText('None')
        self.label_offset_y.setText('None')
        self.label_offset_z.setText('None')
        self.label_widget.setVisible(False)

        self.actionPick.setEnabled(False)
        self.actionCachePick.setEnabled(False)
        return True

    def open_backgrpund_color_dialog(self):
        color = QtWidgets.QColorDialog.getColor(parent=self)
        if color.isValid():
            self.openGLWidget.set_background_color(color.redF(), color.greenF(), color.blueF())

    def show_message(self, message:str, msecs:int=5000):
        self.statusbar.showMessage(message, msecs)

    def reload_cfg(self):
        self.cfg = load_config(self.config_file)
        label_dict_list = self.cfg.get('label', [])
        d = OrderedDict()
        for index, label_dict in enumerate(label_dict_list):
            category = label_dict.get('name', '__unclassified__')
            color = label_dict.get('color', '#ffffff')
            d[category] = color
        self.category_color_dict = d

    def save_cfg(self, config_file):
        save_config(self.cfg, config_file)

    def save_category_and_instance(self):
        if self.openGLWidget.pointcloud is not None:
            if self.openGLWidget.categorys is not None and self.openGLWidget.instances is not None:
                if self.current_file is None:
                    return
                label_file = '.'.join(self.current_file.split('.')[:-1])+'.json'

                datas = {}
                datas['info'] = 'PSAT label file.'
                datas['point cloud file'] = self.current_file
                datas['index_category_dict'] = {index: category for index, (category, color) in enumerate(self.category_color_dict.items())}

                datas['categorys'] = self.openGLWidget.categorys.tolist()
                datas['instances'] = self.openGLWidget.instances.tolist()

                with open(label_file, 'w') as f:
                    dump(datas, f, indent=4)

                self.show_message('{} have saved!'.format(label_file))
                self.save_state = True

    def update_dock(self):
        if self.openGLWidget.display == DISPLAY.ELEVATION:
            self.info_widget.setVisible(True)
            self.label_widget.setVisible(False)
            self.dockWidget.setWindowTitle('Elevation')

            self.label_num_point.setText('{}'.format(self.openGLWidget.pointcloud.num_point))
            self.label_size_x.setText('{:.2f}'.format(self.openGLWidget.pointcloud.size[0]))
            self.label_size_y.setText('{:.2f}'.format(self.openGLWidget.pointcloud.size[1]))
            self.label_size_z.setText('{:.2f}'.format(self.openGLWidget.pointcloud.size[2]))
            self.label_offset_x.setText('{:.2f}'.format(self.openGLWidget.pointcloud.offset[0]))
            self.label_offset_y.setText('{:.2f}'.format(self.openGLWidget.pointcloud.offset[1]))
            self.label_offset_z.setText('{:.2f}'.format(self.openGLWidget.pointcloud.offset[2]))
        if self.openGLWidget.display == DISPLAY.RGB:
            self.info_widget.setVisible(True)
            self.label_widget.setVisible(False)
            self.dockWidget.setWindowTitle('RGB')

            self.label_num_point.setText('{}'.format(self.openGLWidget.pointcloud.num_point))
            self.label_size_x.setText('{:.2f}'.format(self.openGLWidget.pointcloud.size[0]))
            self.label_size_y.setText('{:.2f}'.format(self.openGLWidget.pointcloud.size[1]))
            self.label_size_z.setText('{:.2f}'.format(self.openGLWidget.pointcloud.size[2]))
            self.label_offset_x.setText('{:.2f}'.format(self.openGLWidget.pointcloud.offset[0]))
            self.label_offset_y.setText('{:.2f}'.format(self.openGLWidget.pointcloud.offset[1]))
            self.label_offset_z.setText('{:.2f}'.format(self.openGLWidget.pointcloud.offset[2]))

        if self.openGLWidget.display == DISPLAY.CATEGORY:
            self.info_widget.setVisible(False)
            self.label_widget.setVisible(True)
            self.dockWidget.setWindowTitle('Category')

            self.label_listWidget.clear()
            for index, (category, color) in enumerate(self.category_color_dict.items()):
                item = QtWidgets.QListWidgetItem()
                item.setSizeHint(QtCore.QSize(200, 30))
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout()
                layout.setContentsMargins(9, 1, 9, 1)

                check_box = QtWidgets.QCheckBox()
                check_box.setFixedWidth(20)
                check_box.setChecked(self.openGLWidget.category_display_state_dict.get(index, True))
                check_box.setObjectName('check_box')
                check_box.stateChanged.connect(functools.partial(self.point_cloud_visible))

                label_category = QtWidgets.QLabel()
                label_category.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                label_category.setText(category)
                label_category.setObjectName('label_category')

                label_color = QtWidgets.QLabel()
                label_color.setFixedWidth(10)
                label_color.setStyleSheet("background-color: {};".format(color))
                label_color.setObjectName('label_color')

                layout.addWidget(check_box)
                layout.addWidget(label_color)
                layout.addWidget(label_category)
                widget.setLayout(layout)

                self.label_listWidget.addItem(item)
                self.label_listWidget.setItemWidget(item, widget)

        if self.openGLWidget.display == DISPLAY.INSTANCE:
            self.info_widget.setVisible(False)
            self.label_widget.setVisible(True)
            self.dockWidget.setWindowTitle('Instance')

            self.label_listWidget.clear()
            instances_set = list(set(self.openGLWidget.instances.tolist()))
            instances_set.sort()
            color_map = self.openGLWidget.color_map * 255
            for index in instances_set:
                item = QtWidgets.QListWidgetItem()
                item.setSizeHint(QtCore.QSize(200, 30))
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout()
                layout.setContentsMargins(9, 1, 9, 1)

                check_box = QtWidgets.QCheckBox()
                check_box.setFixedWidth(20)
                check_box.setChecked(self.openGLWidget.instance_display_state_dict.get(index, True))
                check_box.setObjectName('check_box')
                check_box.stateChanged.connect(functools.partial(self.point_cloud_visible))

                label_instance = QtWidgets.QLabel()
                label_instance.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                label_instance.setText('{}'.format(index))
                label_instance.setObjectName('label_instance')

                color = color_map[index]
                color = QColor(color[0], color[1], color[2])
                label_color = QtWidgets.QLabel()
                label_color.setFixedWidth(10)
                label_color.setStyleSheet("background-color: {};".format(color.name()))
                label_color.setObjectName('label_color')

                layout.addWidget(check_box)
                layout.addWidget(label_color)
                layout.addWidget(label_instance)
                widget.setLayout(layout)

                self.label_listWidget.addItem(item)
                self.label_listWidget.setItemWidget(item, widget)

    def point_cloud_visible(self):
        if self.openGLWidget.display == DISPLAY.CATEGORY:
            mask = np.ones(self.openGLWidget.categorys.shape, dtype=bool)
            for index in range(self.label_listWidget.count()):
                item = self.label_listWidget.item(index)
                widget = self.label_listWidget.itemWidget(item)
                check_box = widget.findChild(QtWidgets.QCheckBox, 'check_box')
                if not check_box.isChecked():
                    mask[self.openGLWidget.categorys==index] = False
                    self.openGLWidget.category_display_state_dict[index] = False
                else:
                    self.openGLWidget.category_display_state_dict[index] = True

            self.openGLWidget.mask = mask
            self.openGLWidget.current_vertices = self.openGLWidget.pointcloud.xyz[self.openGLWidget.mask]
            self.openGLWidget.current_colors = self.openGLWidget.category_color[self.openGLWidget.mask]

        elif self.openGLWidget.display == DISPLAY.INSTANCE:
            mask = np.ones(self.openGLWidget.instances.shape, dtype=bool)
            for index in range(self.label_listWidget.count()):
                item = self.label_listWidget.item(index)
                widget = self.label_listWidget.itemWidget(item)
                label_instance = widget.findChild(QtWidgets.QLabel, 'label_instance')
                label_instance = int(label_instance.text())
                check_box = widget.findChild(QtWidgets.QCheckBox, 'check_box')
                if not check_box.isChecked():
                    mask[self.openGLWidget.instances==label_instance] = False
                    self.openGLWidget.instance_display_state_dict[label_instance] = False
                else:
                    self.openGLWidget.instance_display_state_dict[label_instance] = True

            self.openGLWidget.mask = mask
            self.openGLWidget.current_vertices = self.openGLWidget.pointcloud.xyz[self.openGLWidget.mask]
            self.openGLWidget.current_colors = self.openGLWidget.instance_color[self.openGLWidget.mask]
        self.openGLWidget.init_vertex_vao()
        self.openGLWidget.update()

    def check_show_all(self):
        for index in range(self.label_listWidget.count()):
            item = self.label_listWidget.item(index)
            widget = self.label_listWidget.itemWidget(item)
            check_box = widget.findChild(QtWidgets.QCheckBox, 'check_box')
            check_box.setChecked(self.checkBox_showall.isChecked())

            self.openGLWidget.mask.fill(self.checkBox_showall.isChecked())
            self.openGLWidget.init_vertex_vao()
            self.openGLWidget.update()

    def setting(self):
        self.setting_dialog.load_cfg()
        self.setting_dialog.show()

    def translate(self, language='zh'):
        if language == 'zh':
            self.trans.load('ui/zh_CN')
        else:
            self.trans.load('ui/en')
        self.actionChinese.setChecked(language=='zh')
        self.actionEnglish.setChecked(language=='en')
        _app = QtWidgets.QApplication.instance()
        _app.installTranslator(self.trans)
        self.retranslateUi(self)
        self.category_choice_dialog.retranslateUi(self.category_choice_dialog)
        self.setting_dialog.retranslateUi(self.setting_dialog)
        self.about_dialog.retranslateUi(self.about_dialog)
        self.shortcut_dialog.retranslateUi(self.shortcut_dialog)

    def translate_to_chinese(self):
        self.translate('zh')
        self.cfg['language'] = 'zh'

    def translate_to_english(self):
        self.translate('en')
        self.cfg['language'] = 'en'

    def shortcut(self):
        self.shortcut_dialog.show()

    def about(self):
        self.about_dialog.show()

    def init_connect(self):
        self.actionOpen.triggered.connect(self.open_file)
        self.actionOpenFolder.triggered.connect(self.open_folder)
        self.listWidget_files.itemDoubleClicked.connect(self.double_click_files_widget)
        self.actionClose.triggered.connect(self.close_point_cloud)
        self.actionSave.triggered.connect(self.save_category_and_instance)
        self.actionExit.triggered.connect(self.close)

        self.actionPoint_size.triggered.connect(partial(self.openGLWidget.pointsize_change, 1))
        self.actionPoint_size_2.triggered.connect(partial(self.openGLWidget.pointsize_change, -1))
        self.actionTop_view.triggered.connect(self.openGLWidget.set_top_view)
        self.actionBottom_view.triggered.connect(self.openGLWidget.set_bottom_view)
        self.actionFront_view.triggered.connect(self.openGLWidget.set_front_view)
        self.actionBack_view.triggered.connect(self.openGLWidget.set_back_view)
        self.actionLeft_view.triggered.connect(self.openGLWidget.set_left_view)
        self.actionRight_view.triggered.connect(self.openGLWidget.set_right_view)

        self.actionBackground_color.triggered.connect(self.open_backgrpund_color_dialog)
        self.actionElevation.triggered.connect(self.openGLWidget.change_color_to_elevation)
        self.actionRgb.triggered.connect(self.openGLWidget.change_color_to_rgb)
        self.actionCategory.triggered.connect(self.openGLWidget.change_color_to_category)
        self.actionInstance.triggered.connect(self.openGLWidget.change_color_to_instance)
        self.actionGround_filter.triggered.connect(self.ground_filter_thread_start)
        self.actionClassify.triggered.connect(self.classify_thread_start)

        self.actionPick.triggered.connect(self.openGLWidget.change_mode_to_pick)
        self.actionCachePick.triggered.connect(self.openGLWidget.cache_pick)

        self.actionSetting.triggered.connect(self.setting)
        self.actionChinese.triggered.connect(self.translate_to_chinese)
        self.actionEnglish.triggered.connect(self.translate_to_english)
        self.actionShortcut.triggered.connect(self.shortcut)
        self.actionAbout.triggered.connect(self.about)

        self.checkBox_showall.stateChanged.connect(self.check_show_all)

if __name__ == '__main__':
    app = QtWidgets.QApplication([''])
    mainwindow = Mainwindow()
    mainwindow.show()
    sys.exit(app.exec_())

