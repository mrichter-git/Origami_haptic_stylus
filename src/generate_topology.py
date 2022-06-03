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

import pyqtgraph as pg
from pyqtgraph.ptime import time

PORT_LEFT = "COM6"


def f(x, y):
    return np.sin(x) ** 10 + np.cos(10 + y * x) * np.cos(x)

def generate_data():
    x = np.linspace(0, 5, 50)
    y = np.linspace(0, 5, 40)

    X, Y = np.meshgrid(x, y)
    Z = f(X, Y)

    return X, Y, Z

def return_Z(x,y):
    if x == None or y == None:
        return 0
    else:
        return f(x,y)

def read_Serial():
    ser_bytes = ser.readline()
    decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8")).split(",")
    return decoded_bytes


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Haptic stylus Demo")
        # set size to full screen
        frame_rect = app.desktop().frameGeometry()
        self.width, self.height = frame_rect.width(), frame_rect.height()
        self.resize(self.width, self.height)
        self.move(-9, 0)

        #plot the topo map

        #handle tablet
        self.pen_is_down = False
        self.pen_x = 0
        self.pen_y = 0
        self.pen_pressure = 0
        self.text = ""

        self.inDemos = False

        topLLayout = QHBoxLayout()
        button_widget = QWidget()
        self.button1 = QPushButton(button_widget)
        self.button1.setText("Switch to Demos")
        self.button1.setCheckable(True)
        self.button1.setStyleSheet("background-color : lightgrey")
        topLLayout.addWidget(self.button1)
        self.button1.clicked.connect(self.switch1)

        self.button2 = QPushButton(button_widget)
        self.button2.setText("Calibrate corners")
        self.button2.setCheckable(True)
        self.button2.setStyleSheet("background-color : lightgrey")
        topLLayout.addWidget(self.button1)
        #self.button1.clicked.connect(self.switch2)

        topMLayout = QFormLayout()
        topMLayout.addRow("hoo", QLineEdit())
        
        topLayout = QHBoxLayout()
        topLayout.addLayout(topLLayout)
        topLayout.addLayout(topMLayout)
        topLayout.addSpacing(int(self.width/4))

        self.stackedLayout = QStackedLayout()

        TestWidget = Tests()
        self.stackedLayout.addWidget(TestWidget)
        DemoWidget = Demos()
        self.stackedLayout.addWidget(DemoWidget)


        self.layout = QVBoxLayout()
        self.layout.addLayout(topLayout,1)
        self.layout.addLayout(self.stackedLayout,50)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.showMaximized()

    def tabletEvent(self, tabletEvent):
        self.pen_x = tabletEvent.globalX()
        self.pen_y = tabletEvent.globalY()
        self.pen_pressure = int(tabletEvent.pressure() * 100)
        if tabletEvent.type() == QTabletEvent.TabletPress:
            self.pen_is_down = True
            self.text = "TabletPress event"
        elif tabletEvent.type() == QTabletEvent.TabletMove:
            self.pen_is_down = True
            self.text = "TabletMove event"
            #print(self.pen_x, self.pen_y)
        elif tabletEvent.type() == QTabletEvent.TabletRelease:
            self.pen_is_down = False
           
            self.text = "TabletRelease event"
        self.text += "x={0}, y={1}, pressure={2}%,".format(self.pen_x, self.pen_y, self.pen_pressure)
        
        if self.pen_is_down:
            self.text += " Stylus  is touching"
        else:
            self.text += " Stylus not touching"
        
        self.sc.test

        tabletEvent.accept()
        self.update()

    def paintEvent(self, event):
        text = self.text
        i = text.find("\n\n")
        if i >= 0:
            text = text.left(i)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.drawText(self.rect(), Qt.AlignTop | Qt.AlignRight , text)

    def switch1(self):
        # if button is checked
        if self.button1.isChecked():
            # setting background color to light-blue
            self.button1.setStyleSheet("background-color : lightblue")
            self.button1.setText("Switch to Tests")
            self.stackedLayout.setCurrentIndex(1)
            self.inDemos = True
        # if it is unchecked
        else:
            # set background color back to light-grey
            self.button1.setStyleSheet("background-color : lightgrey")
            self.button1.setText("Switch to Demos")
            self.stackedLayout.setCurrentIndex(0)
            self.inDemos = False

class MplCanvas(FigureCanvasQTAgg):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, frameon=False)
        self.axes = self.fig.add_subplot(111)
        self.axes.axis('off')
        super(MplCanvas, self).__init__(self.fig)

class Demos(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)

        #Demo 1
        self.sc = MplCanvas(self)
        X,Y,Z = generate_data()
        self.sc.axes.contourf(X,Y,Z, 60, cmap='jet')

        #Demo 2
        label2 = QLabel("Widget in Tab 2.")

        tabwidget = QTabWidget()
        tabwidget.addTab(self.sc, "Demo 1")
        tabwidget.addTab(label2, "Demo 2")
        layout.addWidget(tabwidget, 0, 0)

class Tests(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.input = read_Serial()
        self.output = ""

        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,40)

        self.textbox2 = QLineEdit(self)
        self.textbox2.move(20, 20)
        self.textbox2.resize(280,40)

        self.textbox3 = QLineEdit(self)
        self.textbox3.resize(280,40)

        self.stop_btn = QtWidgets.QPushButton(text="Stop", clicked=self.send )

        self.Labeltb4 = QLabel(self)
        self.Labeltb4.setText('Test input')
        self.Labeltb4.move(20, 20)
        self.textbox4 = QLineEdit(self)
        self.textbox4.resize(280,40)
        self.textbox4.move(80, 20)
        self.textbox4.textChanged.connect(self.textadd)
        self.textbox4.editingFinished.connect(self.textsend)

        self.graph_sel = QComboBox()
        items = [i.split(':')[0] for i in self.input]
        self.graph_sel.addItems(items)
        self.graph_sel.currentIndexChanged.connect(self.graph_index_changed)
        self.graph_idx = 0

        self.graphWidget = pg.PlotWidget()
        self.x = list(range(70))
        self.y = list(range(70))

        self.graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        # styles = {'color':'r', 'font-size':'20px'}
        # self.graphWidget.setLabel('left', 'Temperature (°C)', **styles)
        # self.graphWidget.setLabel('bottom', 'Hour (H)', **styles)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update)
        self.timer.timeout.connect(self.update_plot)
        self.timer.timeout.connect(self.update_text)
        self.timer.start()

        #Demo 2
        layout.addWidget(self.stop_btn, 0, 0, 1, 1)
        layout.addWidget(self.textbox, 0, 1, 1, 1)
        layout.addWidget(self.textbox2, 0, 2, 1, 1)
        layout.addWidget(self.textbox3, 0, 3, 1, 1)
        layout.addWidget(self.graph_sel, 0, 4, 1, 1)
        layout.addWidget(self.Labeltb4, 1, 0, 1, 1)
        layout.addWidget(self.textbox4, 1, 1, 1, 1)
        layout.addWidget(self.graphWidget, 2,0,1,5 )

    def update(self):
        self.input = read_Serial()

    def update_plot(self):
        try:
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
    
            self.y = self.y[1:]  # Remove the first 
            self.y.append(float(self.input[self.graph_idx].split(":")[1]))
            self.data_line.setData(self.x, self.y)  # Update the data
        except:
            print("Error updating plot")

    def update_text(self):
        try:
            self.textbox.setText(self.input[0])
            self.textbox2.setText(self.input[self.graph_idx])
            self.textbox3.setText(self.input[-1])

        except: 
            print("Error while updating text")
    
    def graph_index_changed(self, index):
        #print("Shrubbery")
        self.graph_idx = index
        self.x = [0]*70
        self.y = [0]*70
        self.data_line.setData(self.x, self.y)
        

    def send(self):
        ser.write("stop".encode())

    def textsend(self):
        ser.write(self.output.encode())

    def textadd(self, text):
        self.output = (text)

ser = serial.Serial()
ser.baudrate = 57600
ser.port = PORT_LEFT 
try:
    ser.open()
except:
    print("There was an issue when opening the serial port")
app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()