
import serial
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

class Tabs(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        label1 = QLabel("Widget in Tab 1.")
        label2 = QLabel("Widget in Tab 2.")
        tabwidget = QTabWidget()
        tabwidget.addTab(label1, "ES")
        tabwidget.setTabEnabled(2,False)
        tabwidget.addTab(label1, "Tab 1")
        tabwidget.addTab(label2, "Tab 2")
        layout.addWidget(tabwidget, 0, 0)

app = QApplication(sys.argv)



# class TabletSampleWindow(QWidget):
#     def __init__(self, parent=None):
#         super(TabletSampleWindow, self).__init__(parent)
#         self.pen_is_down = False
#         self.pen_x = 0
#         self.pen_y = 0
#         self.pen_pressure = 0
#         self.text = ""
#         self.touched = False

#     def tabletEvent(self, tabletEvent):
#         self.pen_x = tabletEvent.globalX()
#         self.pen_y = tabletEvent.globalY()
#         self.pen_pressure = int(tabletEvent.pressure() * 100)
#         if tabletEvent.type() == QTabletEvent.TabletPress:
#             self.pen_is_down = True
#             self.text = "TabletPress event"
#             self.touched = True
#         elif tabletEvent.type() == QTabletEvent.TabletMove:
#             self.pen_is_down = True
#             self.text = "TabletMove event"
#             print(self.pen_x, self.pen_y)
#         elif tabletEvent.type() == QTabletEvent.TabletRelease:
#             self.pen_is_down = False
#             self.text = "TabletRelease event"
#         self.text += " at x={0}, y={1}, pressure={2}%,".format(self.pen_x, self.pen_y, self.pen_pressure)
#         if self.pen_is_down:
#             self.text += " Pen is down."
#         else:
#             self.text += " Pen is up."

#         tabletEvent.accept()
#         self.update()

#     def paintEvent(self, event):
#         text = self.text
#         i = text.find("\n\n")
#         if i >= 0:
#             text = text.left(i)
#         painter = QPainter(self)
#         # rect = QRect(QPoint(0, 0), self.size())
#         painter.setRenderHint(QPainter.TextAntialiasing)
#         painter.drawText(self.rect(), Qt.AlignTop | Qt.AlignLeft , text)
#         # painter.fillRect(rect, Qt.transparent)

#     def send_pos(self):
#         return  self.pen_x, self.pen_y
#     def test_touched(self):
#         return  self.touched

# # app = QApplication(sys.argv)
