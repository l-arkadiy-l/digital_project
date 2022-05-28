
import sys


import cv2
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtGui

from apps.inter import Ui_MainWindow
import pyqtgraph as pg


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setup()

    def setup(self):
        self.x = np.array([500, 600, 700, 800, 900])
        self.y = np.array([900, 1000, 900, 400, 500])
        self.img_height = 1200 # TODO: get height img
        self.radioButton.clicked.connect(self.show_graph_walrus)
        self.radioButton_2.clicked.connect(self.draw_points_walrus)
        self.setFixedSize(1250, 800)


    def show_graph_walrus(self):
        self.graphicsView.show()
        self.l_image.hide()
        self.graphicsView.plot(self.x, [self.img_height - i for i in self.y], pen=None, symbol='t3',
                               symbolPen=pg.mkPen('y', width=10), symbolBrush=0.2, name='g')

    def draw_points_walrus(self):
        self.graphicsView.hide()
        img = cv2.imread('11.jpg')

        # Initialize blank mask image of same dimensions for drawing the shapes
        shapes = np.zeros_like(img, np.uint8)

        # Draw shapes
        for i in range(len(self.x)):
            cv2.rectangle(shapes, (self.x[i], self.y[i]), (self.x[i] + 20, self.y[i] + 20), (8, 255, 245), cv2.FILLED)

        # Generate output by blending image with shapes image, using the shapes
        # images also as mask to limit the blending to those parts
        out = img.copy()
        alpha = 0.5
        mask = shapes.astype(bool)
        out[mask] = cv2.addWeighted(img, alpha, shapes, 1 - alpha, 0)[mask]

        # Visualization
        cv2.imwrite('Output.jpg', out) # save image
        self.l_image.setPixmap(QtGui.QPixmap("Output.jpg")) # show img in app
        self.l_image.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    app.exec_()
