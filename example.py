# -*- coding: utf-8 -*-
"""
@Time ： 2021/4/9 12:00
@Auth ： by richWong 王日超
@File ： example.py
@Ide ： PyCharm
@Motto ： ABC(Always Be Coding)
@Introduction ： 猫狗检测器

"""

import sys
import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont, QPalette, QBrush, QKeySequence
import paddlex as pdx
import cv2 as cv
import time
import pynvml
from PyQt5.QtWidgets import QMessageBox, QShortcut
from gpuinfo import GPUInfo
import re


# ui界面设置
class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        # 定义一个计时器
        self.timer_video = QTimer()
        self.video_path = None
        self.cap = None
        self.all_images_list = []
        self.image_list_index = 0
        # 主窗口参数设置
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(848, 724)
        palette = QPalette()
        palette.setBrush(MainWindow.backgroundRole(), QBrush(QPixmap('./setup.jpg')))
        MainWindow.setPalette(palette)
        # MainWindow.setStyleSheet("#MainWindow{border-image:url(./setup.jpg);}")
        # 计算中间位置
        size_x = 280
        size_y = 45
        mid_x = int(848 / 2) - int(size_x / 2)
        mid_y = 500
        # 大窗口 centralwidget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 设置显示label
        self.show_label = QtWidgets.QLabel(mainWindow)
        self.show_label.setObjectName('show_label')
        self.show_label.setFrameShape(QtWidgets.QFrame.Box)
        self.show_label.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.show_label.setGeometry(20, 40, int(848 / 2) + 120, int(724 / 2) + 60)

        # 创建显示结果的label
        self.text1_label = QtWidgets.QLabel(mainWindow)
        self.text1_label.setObjectName('text1_label')
        self.text1_label.setGeometry(600, 50, 200, 30)

        self.score_label = QtWidgets.QLabel(mainWindow)
        self.score_label.setObjectName('score_label')
        self.score_label.setFrameShape(QtWidgets.QFrame.Box)
        self.score_label.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.score_label.setGeometry(600, 80, 200, 30)

        self.text2_label = QtWidgets.QLabel(mainWindow)
        self.text2_label.setObjectName('text2_label')
        self.text2_label.setGeometry(600, 120, 200, 30)

        self.category_label = QtWidgets.QLabel(mainWindow)
        self.category_label.setObjectName('category_label')
        self.category_label.setFrameShape(QtWidgets.QFrame.Box)
        self.category_label.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.category_label.setGeometry(600, 150, 200, 30)

        # 创建停止/开始按钮
        self.stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop_btn.setObjectName('stop')
        self.stop_btn.setGeometry(QtCore.QRect(650, 220, 100, 50))
        self.stop_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220 )}"  # 按键背景色
            "QPushButton:hover{color:white}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(255 ,250 ,240);border: None;}"  # 按下时的样式
        )
        # 初始状态下不可用
        self.stop_btn.setEnabled(False)

        self.star_btn = QtWidgets.QPushButton(self.centralwidget)
        self.star_btn.setObjectName('star')
        self.star_btn.setGeometry(QtCore.QRect(650, 300, 100, 50))
        self.star_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220 )}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(255 ,250 ,240);border: None;}"  # 按下时的样式
        )
        # 初始状态下不可用
        self.star_btn.setEnabled(False)

        # 上一张按钮
        self.up_btn = QtWidgets.QPushButton(self.centralwidget)
        self.up_btn.setObjectName('up')
        self.up_btn.setGeometry(QtCore.QRect(600, 380, 200, 70))
        self.up_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220 )}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:30px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(255 ,250 ,240);border: None;}"  # 按下时的样式
        )
        # 初始状态下不可用
        self.up_btn.setEnabled(False)

        # 下一张按钮
        self.next_btn = QtWidgets.QPushButton(self.centralwidget)
        self.next_btn.setObjectName('next')
        self.next_btn.setGeometry(QtCore.QRect(600, 480, 200, 70))
        self.next_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:30px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(255 ,250 ,240);border: None;}"  # 按下时的样式
        )
        # 初始状态下不可用
        self.next_btn.setEnabled(False)

        # 设置按键参数  第一个按钮，单张图片
        self.file = QtWidgets.QPushButton(self.centralwidget)
        # self.file.setGeometry(QtCore.QRect(57, 660, 175, 28))
        self.file.setGeometry(QtCore.QRect(mid_x, mid_y, size_x, size_y))
        self.file.setObjectName("img_detect")
        self.file.setStyleSheet(
            "QPushButton{background-color:rgb(127 ,255 ,212)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(240, 255, 255);border: None;}"  # 按下时的样式
        )

        # 设置第二个push_button，文件夹  255, 228, 181
        self.fileT = QtWidgets.QPushButton(self.centralwidget)
        self.fileT.setGeometry(QtCore.QRect(mid_x, mid_y + 75, size_x, size_y))
        self.fileT.setObjectName("path_detect")
        self.fileT.setStyleSheet(
            "QPushButton{background-color:rgb(255, 228, 181)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(240, 255, 255);border: None;}"  # 按下时的样式
        )

        # 设置第三个push_button，视频分析
        self.fileD = QtWidgets.QPushButton(self.centralwidget)
        self.fileD.setGeometry(QtCore.QRect(mid_x, mid_y + 75 * 2, size_x, size_y))
        self.fileD.setObjectName("video_detect")
        self.fileD.setStyleSheet(
            "QPushButton{background-color:rgb(255 ,193 ,193)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(240, 255, 255);border: None;}"  # 按下时的样式
        )

        # 主窗口及菜单栏标题栏设置
        MainWindow.setCentralWidget(self.centralwidget)  # 设置最大布局为主要窗口
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 848, 26))
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 80, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # 组件名字及翻译
        self.retranslateUi(MainWindow)
        # 通过名字连接槽
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        ################button按钮快捷键设置################
        if not self.star_btn.isEnabled():
            self.stop_btn.setShortcut('Space')
        if not self.stop_btn.isEnabled():
            self.star_btn.setShortcut('Space')
        self.up_btn.setShortcut('Up')
        self.next_btn.setShortcut('Down')

        ################button按钮点击事件回调函数################
        # 单图片检测槽函数
        self.file.clicked.connect(self.single_image_detect)
        # 文件夹检测槽函数
        self.fileT.clicked.connect(self.file_path_detect)
        # 视频流检测槽函数
        self.fileD.clicked.connect(self.video_stream_detect)
        # 停止按钮槽函数
        self.stop_btn.clicked.connect(self.stop_event)
        # 开始按钮
        self.star_btn.clicked.connect(self.star_event)
        # 下一张按钮
        self.next_btn.clicked.connect(self.next_event)
        # 上一张按钮
        self.up_btn.clicked.connect(self.up_event)

    def next_light(self):
        self.next_btn.setEnabled(True)
        self.next_btn.setStyleSheet(
            "QPushButton{background-color:rgb(205 ,192, 176)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:30px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def next_unlight(self):
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:30px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def up_light(self):
        self.up_btn.setEnabled(True)
        self.up_btn.setStyleSheet(
            "QPushButton{background-color:rgb(205 ,192, 176)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:30px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def up_unlight(self):
        self.up_btn.setEnabled(False)
        self.up_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:30px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def start_light(self):
        self.star_btn.setEnabled(True)
        self.star_btn.setStyleSheet(
            "QPushButton{background-color:rgb(205 ,192, 176)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def start_unlight(self):
        self.star_btn.setEnabled(False)
        self.star_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def stop_light(self):
        self.stop_btn.setEnabled(True)
        self.stop_btn.setStyleSheet(
            "QPushButton{background-color:rgb(205 ,192, 176)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def stop_unlight(self):
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(
            "QPushButton{background-color:rgb(220 ,220 ,220)}"  # 按键背景色
            "QPushButton:hover{color:rgb(238 ,106, 80)}"  # 光标移动到按钮上面后的前景色
            "QPushButton{border-radius:20px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(125,125,125);border: None;}"  # 按下时的样式
        )

    def retranslateUi(self, MainWindow):
        '主窗口标题和其他文本的设置'
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "尿子和十一"))
        MainWindow.setWindowIcon(QIcon('./icon.jpg'))  # 设置icon

        self.text1_label.setFont(QFont("Roman times", 11, QFont.Bold))
        self.text1_label.setText(_translate("MainWindow", "检测分数"))

        self.text2_label.setFont(QFont("Roman times", 11, QFont.Bold))
        self.text2_label.setText(_translate("MainWindow", "当前类别"))

        self.category_label.setToolTip('预测类别')
        self.score_label.setToolTip('预测结果分数')

        self.show_label.setToolTip('结果展示界面')

        self.file.setFont(QFont("Roman times", 12, QFont.Bold))
        self.file.setText(_translate("MainWindow", "请选择单张图片"))
        self.file.setToolTip('根据单张图片路径进行检测,目前支持.png , .jpg格式')

        self.fileT.setFont(QFont("Roman times", 12, QFont.Bold))
        self.fileT.setText(_translate("MainWindow", "请选择图片文件夹"))
        self.fileT.setToolTip('根据图片文件夹的路径进行检测')

        self.fileD.setFont(QFont("Roman times", 12, QFont.Bold))
        self.fileD.setText(_translate("MainWindow", "请选择视频文件"))
        self.fileD.setToolTip('根据视频流路径进行检测,目前仅支持.mp4格式')

        self.stop_btn.setFont(QFont("Roman times", 12, QFont.Bold))
        self.stop_btn.setText(_translate("MainWindow", "暂停"))
        self.stop_btn.setToolTip('仅存在视频流播放时暂停可用')

        self.star_btn.setFont(QFont("Roman times", 12, QFont.Bold))
        self.star_btn.setText(_translate("MainWindow", "继续"))
        self.star_btn.setToolTip('仅存在视频流暂停时可用')

        self.next_btn.setFont(QFont("Roman times", 15, QFont.Bold))
        self.next_btn.setText(_translate("MainWindow", "下一张"))
        self.next_btn.setToolTip('仅在文件夹检测下可用')

        self.up_btn.setFont(QFont("Roman times", 15, QFont.Bold))
        self.up_btn.setText(_translate("MainWindow", "上一张"))
        self.up_btn.setToolTip('仅在文件夹检测下可用')

    def auto_up_next_unlight(self):
        if self.next_btn.isEnabled():
            self.next_unlight()
        if self.up_btn.isEnabled():
            self.up_unlight()
        if self.star_btn.isEnabled():
            self.start_unlight()
        if self.stop_btn.isEnabled():
            self.stop_unlight()

    #########选择图片文件#########
    def single_image_detect(self, Filepath):
        print('==================点击了单图片检测按钮==================')
        image_path = QtWidgets.QFileDialog.getOpenFileName(None, "选取图片文件路径", "E://my_data",
                                                           filter="图片文件 (*.png);(*.jpg)")  # 起始路径
        _image_path = image_path[0]
        # self.fileT.
        if _image_path == '':
            print('未选择任何图片文件')
        else:
            print('选择的单张图片文件路径为 {}'.format(_image_path))
            self.all_images_list = []
            self.image_list_index = 0
            try:
                if self.cap.isOpened():
                    self.cap.release()
            except Exception as e:
                print(e)
            self.auto_up_next_unlight()
            file_size = os.path.getsize(_image_path)  # 大图片5269499 4957410  小图片14263
            img = cv.imread(_image_path)
            h, w, c = img.shape
            # 如果图像过大的话，进行一定缩放
            if file_size > 1050000:
                img = cv.resize(img, dsize=(int(w / 10), int(h / 10)), interpolation=cv.INTER_AREA)
                single_start1 = time.time()
                result = predictor.predict(img)
                print('单个大图片耗时 {} s'.format(time.time() - single_start1))
            else:
                single_start2 = time.time()
                result = predictor.predict(img)
                print('单个小图片耗时 {} s'.format(time.time() - single_start2))
            # 列表包裹字典类型  [{},{},{}]
            # [{'category_id': 1, 'bbox': [62.48440933227539, 14.901748657226562, 92.02807235717773, 104.64143371582031],
            # 'score': 0.15859021246433258, 'category': 'cat'},
            # {'category_id': 2, 'bbox': [61.94285583496094, 13.49465560913086, 91.66557312011719, 109.03857803344727],
            # 'score': 0.7236596345901489, 'category': 'dog'}]
            # 读取label w h
            label_w = self.show_label.width()
            label_h = self.show_label.height()
            score_list = []
            category_list = []
            category_cn_list = []
            id = 0
            for single_element in result:
                left_x, left_y, right_x, right_y = single_element['bbox']
                # id = single_element['category_id']
                score = single_element['score']
                category = single_element['category']
                # 设置分数阈值，大于这个阈值才认为这是个可靠的结果
                if score > 0.70:
                    score_list.append(round(score, 3))
                    category_list.append(category)
                    img = cv.rectangle(img, (int(left_x), int(left_y)), (int(left_x + right_x), int(left_y + right_y)),
                                       color=(255, 0, 255), thickness=2)
                    text = 'ID:[{}]'.format(id)
                    cv.putText(img, text, (int(left_x), int(left_y - 8)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255),
                               1)
                    id += 1
            for index, c in enumerate(category_list):
                if c == 'cat':
                    category_cn_list.append('{}:猫'.format(index))
                elif c == 'dog':
                    category_cn_list.append('{}:狗'.format(index))
            # 设置字体颜色
            self.category_label.setText(str(category_cn_list))
            self.score_label.setText(str(score_list))
            show_img = QImage(img[:], img.shape[1], img.shape[0], img.shape[1] * 3,
                              QImage.Format_RGB888).rgbSwapped()
            self.show_label.setScaledContents(True)
            self.show_label.setPixmap(QPixmap.fromImage(show_img).scaled(label_w, label_h))
            QtWidgets.QApplication.processEvents()

    #########选择文件夹#########
    def file_path_detect(self):
        print('==================点击了文件夹检测按钮==================')
        file_path = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹路径", "E://my_data")  # 起始路径
        # print(file_path)  # E:/my_data/JPEGImages
        if file_path == '':
            print('未选择任何文件夹')
            # mainWindow.show()
        else:
            print('选择的文件夹路径为 {}'.format(file_path))
            self.all_images_list = []
            self.image_list_index = 0
            try:
                if self.cap.isOpened():
                    self.cap.release()
            except Exception as e:
                print(e)
            if self.next_btn.isEnabled():
                self.next_unlight()
            if self.up_btn.isEnabled():
                self.up_unlight()
            if self.star_btn.isEnabled():
                self.start_unlight()
            if self.stop_btn.isEnabled():
                self.stop_unlight()
            # 打开路径下文件
            list_dirs = os.listdir(file_path)
            a = re.search(r'.jpg', str(list_dirs), )
            b = re.search(r'.png', str(list_dirs), )
            if a == None and b == None:
                QMessageBox.warning(None, '警告', '该路径下不存在可用于检测的图片文件！\r\n请重新选择正确的图片文件夹！')
            else:
                for file_name in list_dirs:
                    if '.jpg' in file_name or '.png' in file_name:
                        img_path = os.path.join(file_path, file_name)
                        self.all_images_list.append(img_path)
                _image_path = self.all_images_list[0]
                file_size = os.path.getsize(_image_path)  # 大图片5269499 4957410  小图片14263
                img = cv.imread(_image_path)
                h, w, c = img.shape
                # 如果图像过大的话，进行一定缩放
                if file_size > 1050000:
                    img = cv.resize(img, dsize=(int(w / 10), int(h / 10)), interpolation=cv.INTER_AREA)
                    s1 = time.time()
                    result = predictor.predict(img)
                    print('文件夹单个大图片耗时 {} s'.format(time.time() - s1))
                else:
                    s2 = time.time()
                    result = predictor.predict(img)
                    print('文件夹单个小图片耗时 {} s'.format(time.time() - s2))
                # 列表包裹字典类型  [{},{},{}]
                # [{'category_id': 1, 'bbox': [62.48440933227539, 14.901748657226562, 92.02807235717773, 104.64143371582031],
                # 'score': 0.15859021246433258, 'category': 'cat'},
                # {'category_id': 2, 'bbox': [61.94285583496094, 13.49465560913086, 91.66557312011719, 109.03857803344727],
                # 'score': 0.7236596345901489, 'category': 'dog'}]
                # 读取label w h
                label_w = self.show_label.width()
                label_h = self.show_label.height()
                score_list = []
                category_list = []
                category_cn_list = []
                id = 0
                for single_element in result:
                    left_x, left_y, right_x, right_y = single_element['bbox']
                    # id = single_element['category_id']
                    score = single_element['score']
                    category = single_element['category']
                    # 设置分数阈值，大于这个阈值才认为这是个可靠的结果
                    if score > 0.70:
                        score_list.append(round(score, 3))
                        category_list.append(category)
                        img = cv.rectangle(img, (int(left_x), int(left_y)),
                                           (int(left_x + right_x), int(left_y + right_y)),
                                           color=(255, 0, 255), thickness=2)
                        text = 'ID:[{}]'.format(id)
                        cv.putText(img, text, (int(left_x), int(left_y - 8)), cv.FONT_HERSHEY_SIMPLEX, 0.5,
                                   (255, 0, 255),
                                   1)
                        id += 1
                for index, c in enumerate(category_list):
                    if c == 'cat':
                        category_cn_list.append('{}:猫'.format(index))
                    elif c == 'dog':
                        category_cn_list.append('{}:狗'.format(index))
                # 设置字体颜色
                self.category_label.setText(str(category_cn_list))
                self.score_label.setText(str(score_list))
                show_img = QImage(img[:], img.shape[1], img.shape[0], img.shape[1] * 3,
                                  QImage.Format_RGB888).rgbSwapped()
                self.show_label.setScaledContents(True)
                self.show_label.setPixmap(QPixmap.fromImage(show_img).scaled(label_w, label_h))
                QtWidgets.QApplication.processEvents()
                # 完成后，下一站按钮可用，用于读取后续图片
                self.next_light()
                # self.up_light()

    def openFrame(self):
        if self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if ret:
                height, width, bytesPerComponent = self.frame.shape
                if height * width > 1080 * 1920:  # 2,073,600
                    self.frame = cv.resize(self.frame, (int(width / 4), int(height / 4)))
                # elif 100000 < height * width <= 1080 * 1920:
                #     self.frame = cv.resize(self.frame, (int(width / 3), int(height / 3)))
                st = time.time()
                result = predictor.predict(self.frame)
                print('视频检测每一帧耗时 {} s'.format(time.time()-st))
                score_list = []
                category_list = []
                category_cn_list = []
                for single_element in result:
                    left_x, left_y, right_x, right_y = single_element['bbox']
                    score = single_element['score']
                    category = single_element['category']
                    id = single_element['category_id']
                    # 设置分数阈值，大于这个阈值才认为这是个可靠的结果
                    if score > 0.70:
                        score_list.append(round(score, 3))
                        category_list.append(category)
                        self.frame = cv.rectangle(self.frame, (int(left_x), int(left_y)),
                                                  (int(left_x + right_x), int(left_y + right_y)),
                                                  color=(255, 0, 255), thickness=2)
                        if id == 1:
                            text = 'Category:[{}]'.format('cat')
                        elif id == 2:
                            text = 'Category:[{}]'.format('dog')
                        cv.putText(self.frame, text, (int(left_x), int(left_y - 8)), cv.FONT_HERSHEY_SIMPLEX, 0.8,
                                   (255, 0, 255),
                                   2)
                for index, c in enumerate(category_list):
                    if c == 'cat':
                        category_cn_list.append('{}:猫'.format(index))
                    elif c == 'dog':
                        category_cn_list.append('{}:狗'.format(index))
                # 设置字体颜色
                self.category_label.setText(str(category_cn_list))
                self.score_label.setText(str(score_list))

                show_img = QImage(self.frame[:], self.frame.shape[1], self.frame.shape[0], self.frame.shape[1] * 3,
                                  QImage.Format_RGB888).rgbSwapped()
                self.show_label.setScaledContents(True)
                self.show_label.setPixmap(
                    QPixmap.fromImage(show_img).scaled(self.show_label.width(), self.show_label.height()))
            else:
                self.cap.release()
                self.timer_video.stop()  # 停止计时器
                self.score_label.clear()
                self.category_label.clear()
                self.start_unlight()
                self.stop_unlight()
                QMessageBox.information(None, '通知', '视频流播放已完成！')

    #########选择视频流#########
    def video_stream_detect(self):
        print('==================点击了视频流检测按钮==================')

        image_path = QtWidgets.QFileDialog.getOpenFileName(None, "选取视频文件路径", "E://photos",
                                                           filter="视频文件 (*.mp4)")
        _image_path = image_path[0]
        # self.fileT.
        if _image_path == '':
            print('未选择任何视频文件')
        else:
            print('选择的视频文件路径为 {}'.format(_image_path))
            self.all_images_list = []
            self.image_list_index = 0
            self.auto_up_next_unlight()
            self.stop_light()
            self.video_path = _image_path
            self.cap = cv.VideoCapture(self.video_path)
            # 计算fps
            fps = self.cap.get(cv.CAP_PROP_FPS)
            print("视频帧数:{}".format(int(fps)))  # 1s 30p
            self.timer_video.start(int(fps))
            self.timer_video.timeout.connect(self.openFrame)

    def stop_event(self):
        print('==================点击了停止按钮==================')
        self.timer_video.stop()
        self.start_light()
        self.stop_unlight()

    def up_event(self):
        print('==================点击了上一张按钮==================')
        self.image_list_index -= 1
        print('当前图片索引 {}'.format(self.image_list_index))
        if self.image_list_index == 0:
            self.up_unlight()
            _image_path = self.all_images_list[0]
            file_size = os.path.getsize(_image_path)  # 大图片5269499 4957410  小图片14263
            img = cv.imread(_image_path)
            h, w, c = img.shape
            # 如果图像过大的话，进行一定缩放
            if file_size > 1050000:
                img = cv.resize(img, dsize=(int(w / 6), int(h / 6)), interpolation=cv.INTER_AREA)
                s1 = time.time()
                result = predictor.predict(img)
                print('up键大图片耗时 {} s'.format(time.time() - s1))
            else:
                s2 = time.time()
                result = predictor.predict(img)
                print('up键小图片耗时 {} s'.format(time.time() - s2))
            # 列表包裹字典类型  [{},{},{}]
            # [{'category_id': 1, 'bbox': [62.48440933227539, 14.901748657226562, 92.02807235717773, 104.64143371582031],
            # 'score': 0.15859021246433258, 'category': 'cat'},
            # {'category_id': 2, 'bbox': [61.94285583496094, 13.49465560913086, 91.66557312011719, 109.03857803344727],
            # 'score': 0.7236596345901489, 'category': 'dog'}]
            # 读取label w h
            label_w = self.show_label.width()
            label_h = self.show_label.height()
            score_list = []
            category_list = []
            category_cn_list = []
            id = 0
            for single_element in result:
                left_x, left_y, right_x, right_y = single_element['bbox']
                # id = single_element['category_id']
                score = single_element['score']
                category = single_element['category']
                # 设置分数阈值，大于这个阈值才认为这是个可靠的结果
                if score > 0.70:
                    score_list.append(round(score, 3))
                    category_list.append(category)
                    img = cv.rectangle(img, (int(left_x), int(left_y)), (int(left_x + right_x), int(left_y + right_y)),
                                       color=(255, 0, 255), thickness=2)
                    text = 'ID:[{}]'.format(id)
                    cv.putText(img, text, (int(left_x), int(left_y - 8)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255),
                               1)
                    id += 1
            for index, c in enumerate(category_list):
                if c == 'cat':
                    category_cn_list.append('{}:猫'.format(index))
                elif c == 'dog':
                    category_cn_list.append('{}:狗'.format(index))
            # 设置字体颜色
            self.category_label.setText(str(category_cn_list))
            self.score_label.setText(str(score_list))
            show_img = QImage(img[:], img.shape[1], img.shape[0], img.shape[1] * 3,
                              QImage.Format_RGB888).rgbSwapped()
            self.show_label.setScaledContents(True)
            self.show_label.setPixmap(QPixmap.fromImage(show_img).scaled(label_w, label_h))
            QtWidgets.QApplication.processEvents()
        else:
            _image_path = self.all_images_list[self.image_list_index]
            file_size = os.path.getsize(_image_path)  # 大图片5269499 4957410  小图片14263
            img = cv.imread(_image_path)
            h, w, c = img.shape
            # 如果图像过大的话，进行一定缩放
            if file_size > 1050000:
                img = cv.resize(img, dsize=(int(w / 6), int(h / 6)), interpolation=cv.INTER_AREA)
                result = predictor.predict(img)
            else:
                result = predictor.predict(img)
            # 列表包裹字典类型  [{},{},{}]
            # [{'category_id': 1, 'bbox': [62.48440933227539, 14.901748657226562, 92.02807235717773, 104.64143371582031],
            # 'score': 0.15859021246433258, 'category': 'cat'},
            # {'category_id': 2, 'bbox': [61.94285583496094, 13.49465560913086, 91.66557312011719, 109.03857803344727],
            # 'score': 0.7236596345901489, 'category': 'dog'}]
            # 读取label w h
            label_w = self.show_label.width()
            label_h = self.show_label.height()
            score_list = []
            category_list = []
            category_cn_list = []
            id = 0
            for single_element in result:
                left_x, left_y, right_x, right_y = single_element['bbox']
                # id = single_element['category_id']
                score = single_element['score']
                category = single_element['category']
                # 设置分数阈值，大于这个阈值才认为这是个可靠的结果
                if score > 0.70:
                    score_list.append(round(score, 3))
                    category_list.append(category)
                    img = cv.rectangle(img, (int(left_x), int(left_y)), (int(left_x + right_x), int(left_y + right_y)),
                                       color=(255, 0, 255), thickness=2)
                    text = 'ID:[{}]'.format(id)
                    cv.putText(img, text, (int(left_x), int(left_y - 8)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255),
                               1)
                    id += 1
            for index, c in enumerate(category_list):
                if c == 'cat':
                    category_cn_list.append('{}:猫'.format(index))
                elif c == 'dog':
                    category_cn_list.append('{}:狗'.format(index))
            # 设置字体颜色
            self.category_label.setText(str(category_cn_list))
            self.score_label.setText(str(score_list))
            show_img = QImage(img[:], img.shape[1], img.shape[0], img.shape[1] * 3,
                              QImage.Format_RGB888).rgbSwapped()
            self.show_label.setScaledContents(True)
            self.show_label.setPixmap(QPixmap.fromImage(show_img).scaled(label_w, label_h))
            QtWidgets.QApplication.processEvents()

    def next_event(self):
        print('==================点击了下一张按钮==================')
        self.up_light()
        nums = len(self.all_images_list)
        self.image_list_index += 1
        print('当前图片索引 {}'.format(self.image_list_index))
        if self.image_list_index == nums:
            QMessageBox.warning(None, '警告', '当前文件夹下所有图片已检测完毕！')
            self.next_unlight()
            self.up_unlight()
        else:
            _image_path = self.all_images_list[self.image_list_index]
            file_size = os.path.getsize(_image_path)  # 大图片5269499 4957410  小图片14263
            img = cv.imread(_image_path)
            h, w, c = img.shape
            # 如果图像过大的话，进行一定缩放
            if file_size > 1050000:
                img = cv.resize(img, dsize=(int(w / 6), int(h / 6)), interpolation=cv.INTER_AREA)
                s1 = time.time()
                result = predictor.predict(img)
                print('down键大图片耗时 {} s'.format(time.time() - s1))
            else:
                s2 = time.time()
                result = predictor.predict(img)
                print('down键小图片耗时 {} s'.format(time.time() - s2))
            # 列表包裹字典类型  [{},{},{}]
            # [{'category_id': 1, 'bbox': [62.48440933227539, 14.901748657226562, 92.02807235717773, 104.64143371582031],
            # 'score': 0.15859021246433258, 'category': 'cat'},
            # {'category_id': 2, 'bbox': [61.94285583496094, 13.49465560913086, 91.66557312011719, 109.03857803344727],
            # 'score': 0.7236596345901489, 'category': 'dog'}]
            # 读取label w h
            label_w = self.show_label.width()
            label_h = self.show_label.height()
            score_list = []
            category_list = []
            category_cn_list = []
            id = 0
            for single_element in result:
                left_x, left_y, right_x, right_y = single_element['bbox']
                # id = single_element['category_id']
                score = single_element['score']
                category = single_element['category']
                # 设置分数阈值，大于这个阈值才认为这是个可靠的结果
                if score > 0.70:
                    score_list.append(round(score, 3))
                    category_list.append(category)
                    img = cv.rectangle(img, (int(left_x), int(left_y)), (int(left_x + right_x), int(left_y + right_y)),
                                       color=(255, 0, 255), thickness=2)
                    text = 'ID:[{}]'.format(id)
                    cv.putText(img, text, (int(left_x), int(left_y - 8)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255),
                               1)
                    id += 1
            for index, c in enumerate(category_list):
                if c == 'cat':
                    category_cn_list.append('{}:猫'.format(index))
                elif c == 'dog':
                    category_cn_list.append('{}:狗'.format(index))
            # 设置字体颜色
            self.category_label.setText(str(category_cn_list))
            self.score_label.setText(str(score_list))
            show_img = QImage(img[:], img.shape[1], img.shape[0], img.shape[1] * 3,
                              QImage.Format_RGB888).rgbSwapped()
            self.show_label.setScaledContents(True)
            self.show_label.setPixmap(QPixmap.fromImage(show_img).scaled(label_w, label_h))
            QtWidgets.QApplication.processEvents()

    def star_event(self):
        print('==================点击了继续按钮==================')
        self.timer_video.start()
        self.stop_light()
        self.start_unlight()


def get_gpu_id(num_gpu=1):
    """get ID of GPUS
    :param num_gpu:  num of GPUs to use
    :return: gpu_id: ID of allocated GPUs
    """
    available_device = GPUInfo.check_empty()
    if len(available_device) >= num_gpu:
        gpu_id = available_device[:num_gpu]
    else:
        raise Exception('Only {} GPUs to use!'.format(len(available_device)))
    if num_gpu == 1:
        gpu_id = gpu_id[0]
    return gpu_id


if __name__ == '__main__':
    '1s = 1000ms'
    pynvml.nvmlInit()
    print("Device version: {} ".format(pynvml.nvmlSystemGetDriverVersion()))
    device_count = pynvml.nvmlDeviceGetCount()
    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        # 查看具体哪块显卡
        print('Device {} : {}'.format(i, pynvml.nvmlDeviceGetName(handle)))
    # gpu id
    gpu_id = get_gpu_id(1)
    # 初始化检测器
    predictor_start_time = time.time()
    predictor = pdx.deploy.Predictor('./inference_model_cat_dog', use_gpu=True, gpu_id=gpu_id)
    print('检测器开启成功，耗时 {} s'.format(time.time() - predictor_start_time))

    print('==================快捷键说明==================')
    print('|<1>上下键:文件夹中上一张/下一张图片选择         |')
    print('|<2>空格键:视频播放暂停/开始                   |')
    print('=============================================')

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
