import os
import sys

import cv2
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog, QInputDialog, QMessageBox
from PyQt5 import QtGui

from apps.inter import Ui_MainWindow
import pyqtgraph as pg
from random import randint
from PIL import Image
import getpass

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Загрузите картинку с моржами'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.openFileNameDialog()
        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Images (*.jpg)", options=options)
        if fileName:
            print(fileName)


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.out = None
        self.setupUi(self)
        self.w = None
        self.h = None
        self.setup()

    def setup(self):
        self.setWindowTitle('Walrus Counter')
        self.setWindowIcon(QtGui.QIcon('apps/icon.png'))
        self.radioButton.clicked.connect(self.show_graph_walrus)
        self.radioButton_2.clicked.connect(self.draw_points_walrus)
        self.radioButton_3.clicked.connect(self.begin_img)
        self.btn_download.clicked.connect(self.download_img)
        self.btn_upload.clicked.connect(self.openFileNameDialog)
        # self.btn_upload.hide()

        self.radioButton.setEnabled(False)
        self.radioButton_2.setEnabled(False)
        self.radioButton_3.setEnabled(False)
        self.btn_download.setEnabled(False)

    def show_graph_walrus(self):
        self.graphicsView.show()
        self.l_image.hide()
        self.graphicsView.plot(self.x, [self.h - i for i in self.y], pen=None, symbol='o',
                               symbolPen=pg.mkPen('y', width=10), symbolBrush=0.2, name='g')

    def draw_points(self):
        img = cv2.imread(self.img)

        # Initialize blank mask image of same dimensions for drawing the shapes
        shapes = np.zeros_like(img, np.uint8)

        # Draw shapes
        for i in range(len(self.x)):
            # cv2.rectangle(shapes, (self.x[i], self.y[i]), (self.x[i] + 20, self.y[i] + 20), (8, 255, 245), cv2.FILLED)
            cv2.circle(shapes, (self.x[i], self.y[i]), 15, (8, 255, 255), cv2.FILLED)

        # Generate output by blending image with shapes image, using the shapes
        # images also as mask to limit the blending to those parts
        self.out = img.copy()
        alpha = 0.3
        mask = shapes.astype(bool)
        self.out[mask] = cv2.addWeighted(img, alpha, shapes, 1 - alpha, 0)[mask]

        # Visualization
        cv2.imwrite('Output.jpg', self.out)  # save image
        self.l_image.setPixmap(QtGui.QPixmap("Output.jpg"))  # show img in app

    def draw_points_walrus(self):
        self.graphicsView.hide()
        self.draw_points()
        self.l_image.show()

    def download_img(self):
        self.draw_points()
        picture = Image.open('Output.jpg')
        picture = picture.save(f"C:\\Users\\{getpass.getuser()}\\Downloads\\result.jpg")
        self.open_dialog()

    def begin_img(self):
        self.graphicsView.hide()
        self.l_image.show()
        self.l_image.setPixmap(QtGui.QPixmap(self.img))

    def openFileNameDialog(self):
        file_filter = 'Data File (*.jpg);; Image files(*.jpg)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a jpg file',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='JPG File (*.jpg)'
        )
        self.img = response[0]
        im = Image.open(self.img)
        self.w, self.h = im.size
        im.save('cur_img.jpg')
        self.img = 'cur_img.jpg'
        self.l_image.setPixmap(QtGui.QPixmap(self.img))
        self.btn_upload.hide()

        self.x = np.array([randint(0, self.w) for i in range(100)])
        self.y = np.array([randint(0, self.h) for i in range(100)])
        self.radioButton.setEnabled(True)
        self.radioButton_2.setEnabled(True)
        self.radioButton_3.setEnabled(True)
        self.btn_download.setEnabled(True)
        self.radioButton_3.setChecked(True)

    def open_dialog(self):
        msgBox = QMessageBox(
            QMessageBox.Information,
            "Фото скачалось",
            f"Фотография скачена и помещена в -> 'C:\\Users\\{getpass.getuser()}\\Downloads\\result.jpg'",
            buttons=QMessageBox.Cancel,
            parent=self,
        )
        msgBox.setDefaultButton(QMessageBox.No)
        msgBox.setStyleSheet("QLabel{ color: white}")
        msgBox.exec_()
        reply = msgBox.standardButton(msgBox.clickedButton())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    app.exec_()
    os.remove('Output.jpg')
    os.remove('cur_img.jpg')
