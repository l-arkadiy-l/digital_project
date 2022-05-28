import csv
import getpass
import os
import sys
from random import randint

import cv2
import numpy as np
import pyqtgraph as pg
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtGui import QPainterPath
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog, QMessageBox
from inference import take_res
from apps.inter import Ui_MainWindow


def delete_files(folder_name):
    import os, shutil
    folder = folder_name
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


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
        self.scatter = None
        self.setup()

    def setup(self):
        self.setWindowTitle('Walrus Counter')
        self.setWindowIcon(QtGui.QIcon('apps/icon.png'))
        self.radioButton.clicked.connect(self.show_graph_walrus)
        self.radioButton_2.clicked.connect(self.draw_points_walrus)
        self.radioButton_3.clicked.connect(self.begin_img)
        self.btn_download.clicked.connect(self.download_img)
        self.btn_upload.clicked.connect(self.openFileNameDialog)
        self.btn_new.clicked.connect(self.openFileNameDialog)
        self.btn_download_csv.clicked.connect(self.download_csv_file)
        # self.btn_upload.hide()

        self.radioButton.setEnabled(False)
        self.radioButton_2.setEnabled(False)
        self.radioButton_3.setEnabled(False)
        self.btn_download.setEnabled(False)
        self.btn_new.hide()
        self.btn_download.hide()
        self.btn_download_csv.hide()

    def show_graph_walrus(self):

        self.l_image.hide()

        # create pyqt5graph bar graph item
        # with width = 0.6
        # with bar colors = green
        if self.scatter:
            self.graphicsView.removeItem(self.scatter)
        self.scatter = pg.ScatterPlotItem(
            size=18, brush=pg.mkBrush(0, 251, 0, 120))

        # creating spots using the random position

        # adding points to the scatter plot
        self.scatter.setData(self.x, [self.h - i for i in self.y])
        # self.graphicsView.plot(self.x, [self.h - i for i in self.y], pen=None, symbol='o',
        #                        symbolPen=pg.mkPen('y', width=10), symbolBrush=0.2, name='g')
        # self.clear_view()
        self.graphicsView.addItem(self.scatter)
        self.graphicsView.show()

        print(self.graphicsView.currentItem)

    def clear_view(self):
        self.path = QPainterPath()
        self.item.setPath(self.path)

    def draw_points(self):
        img = cv2.imread(self.img)

        # Initialize blank mask image of same dimensions for drawing the shapes
        shapes = np.zeros_like(img, np.uint8)

        # Draw shapes
        for i in range(len(self.x)):
            # cv2.rectangle(shapes, (self.x[i], self.y[i]), (self.x[i] + 20, self.y[i] + 20), (8, 255, 245), cv2.FILLED)
            cv2.circle(shapes, (self.x[i], self.y[i]), 15, (0, 251, 0), cv2.FILLED)

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
        picture = picture.save(f"C:\\Users\\{getpass.getuser()}\\Downloads\\{self.filename}_result.jpg")
        self.open_dialog()

    def begin_img(self):
        self.graphicsView.hide()
        self.l_image.show()
        self.l_image.setPixmap(QtGui.QPixmap(self.img))

    def openFileNameDialog(self):
        delete_files('test_images')
        delete_files('coords_center')
        delete_files('yolov5/runs/detect')
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
        self.filename = ''.join(self.img.split('/')[-1].split('.')[:-1])
        print('-->', self.filename)
        im.save(f'test_images/cur_{self.filename}.jpg')
        self.img = f'test_images/cur_{self.filename}.jpg'
        self.l_image.setPixmap(QtGui.QPixmap(self.img))
        self.btn_upload.hide()
        # upload to test_images
        take_res()
        import csv
        self.x = []
        self.y = []
        with open(f'coords_center/cur_{self.filename}.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in list(spamreader)[1:]:
                print(row)
                x, y = row[0].split(',')
                self.x.append(int(x))
                self.y.append(int(y))

        self.radioButton.setEnabled(True)
        self.radioButton_2.setEnabled(True)
        self.radioButton_3.setEnabled(True)
        self.btn_download.setEnabled(True)
        self.radioButton_3.setChecked(True)

        self.label.setText(str(len(self.x)))
        self.btn_new.show()
        self.btn_download.show()
        self.btn_download_csv.show()
        self.graphicsView.hide()
        self.l_image.show()

    def open_dialog(self):
        msgBox = QMessageBox(
            QMessageBox.Information,
            "Фото скачалось",
            f"Фотография cкачена и помещена в -> 'C:\\Users\\{getpass.getuser()}\\Downloads\\{self.filename}_result.jpg'",
            buttons=QMessageBox.Cancel,
            parent=self,
        )
        msgBox.setDefaultButton(QMessageBox.No)
        msgBox.setStyleSheet("QLabel{ color: white}")
        msgBox.exec_()
        reply = msgBox.standardButton(msgBox.clickedButton())

    def download_csv_file(self):
        with open(f'coords_center/cur_{self.filename}.csv', newline='') as csvfile:
            spamreader = csv.writer(csvfile, delimiter=' ', quotechar='|')

if __name__ == '__main__':
    delete_files('test_images')
    delete_files('coords_center')
    delete_files('yolov5/runs/detect')
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    app.exec_()
