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

TL_X = 260
TL_Y = 270
BR_X = 1700
BR_Y = 910
MAX_X = 1920
MAX_Y = 1080


def f(x, y):
    return np.sin(x) ** 10 + np.cos(10 + y * x) * np.cos(x)

def return_Z(x,y):
    if x == None or y == None:
        return 0
    elif (x < TL_X or x > BR_X):
        return 0
    elif (y < TL_Y or y > BR_Y):
        return 0
    else:
        x_c = (x - TL_X)*MAX_X/(BR_X-TL_X)
        y_c = (y - TL_Y)*MAX_Y/(BR_Y-TL_Y)
        return f(x_c,y_c)

def read_Serial():
    try:
        ser.reset_input_buffer()
        ser_bytes = ser.readline()
        decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8")).split(",")
    except:
        decoded_bytes = 0
    return decoded_bytes

serialIn = ""

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Haptic stylus Demo")
        # set size to full screen
        frame_rect = app.desktop().frameGeometry()
        self.width, self.height = frame_rect.width(), frame_rect.height()
        self.resize(self.width, self.height)
        self.move(-9, 0)

        #handle tablet
        self.pen_is_down = False
        self.pen_x = 0
        self.pen_y = 0
        self.pen_pressure = 0
        self.text = ""
        self.pen_z = 0

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

        # self.topMLayout = QHBoxLayout()
        # self.textbox = QLineEdit(self)
        # # self.textbox.move(20, 20)
        # # self.textbox.resize(280,40)
        # label = QLabel("Serial Input")
        # self.topMLayout.addWidget(label)
        # self.topMLayout.addWidget(self.textbox)
        # self.textbox.setText("What the dog doin???")
        # self.topMLayout.addRow("Serial Input", QLineEdit())
        
        topLayout = QHBoxLayout()
        topLayout.addLayout(topLLayout)
        topLayout.addSpacing(int(self.width/2))

        self.stackedLayout = QStackedLayout()

        TestWidget = Tests()
        self.stackedLayout.addWidget(TestWidget)
        self.DemoWidget = Demos()
        self.stackedLayout.addWidget(self.DemoWidget)

        self.layout = QVBoxLayout()
        self.layout.addLayout(topLayout,1)
        self.layout.addLayout(self.stackedLayout,50)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(20)
        # self.timer.timeout.connect(self.TextUpdate)  

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
            self.pen_z = return_Z(self.pen_x, self.pen_y)
            self.DemoWidget.textadd(self.pen_z)
            #self.DemoWidget.textsend()
        else:
            self.text += " Stylus not touching"
        
        self.text += " \n z={0}".format(self.pen_z)
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
        self.text = ""
        self.output = 0
        self.x = 0
        self.y = 0
        self.z = 0

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.TextUpdate)  
        self.timer.start()

        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,40)

        #Demo 1
        self.sc = MplCanvas(self)
        self.generate_data()
        self.sc.axes.contourf(self.x, self.y, self.z, 60, cmap='jet')

        #Demo 2
        label2 = QLabel("Widget in Tab 2.")

        
        tabwidget = QTabWidget()
        tabwidget.addTab(self.sc, "Demo 1")
        tabwidget.addTab(label2, "Demo 2")

        layout.addWidget(self.textbox,0,0)
        layout.addWidget(tabwidget, 1, 0)

    def textsend(self):
        ser.write(self.output.encode())

    def textadd(self, text):
        self.output = ("Z:{:+.2f},".format(text))

    def generate_data(self):
        x = np.linspace(0, 5, 50)
        y = np.linspace(0, 5, 40)

        self.x, self.y = np.meshgrid(x, y)
        self.z = f(self.x, self.y)

    def TextUpdate(self):
        try:
            self.textbox.setText(read_Serial()[-1])
        except:
            print("Error while reading serial")

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

        self.measure_btn = QtWidgets.QPushButton(text="Measure with ToF?", clicked=self.send_measure)
        self.measure_btn.setCheckable(True)

        self.graph_sel = QComboBox()
        items = [i.split(':')[0] for i in self.input]
        self.graph_sel.addItems(items)
        self.graph_sel.currentIndexChanged.connect(self.graph_index_changed)
        self.graph_sel.objectNameChanged
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
        layout.addWidget(self.measure_btn, 1, 2, 1, 1)
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
            self.x = [0]*70
            self.y = [0]*70
            self.data_line.setData(self.x, self.y)  # Update the data
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
        self.x = [0]*100
        self.y = [0]*100
        self.data_line.setData(self.x, self.y)       

    def send(self):
        ser.write("stop".encode())
    
    def send_measure(self):
        if self.measure_btn.isChecked():
            # setting background color to light-blue
            self.measure_btn.setStyleSheet("background-color : lightblue")
            self.measure_btn.setText("Measuring with ToF")
            ser.write("measure".encode())
        # if it is unchecked
        else:
            ser.write("no_measure".encode())
            self.measure_btn.setText("Measure with ToF?")

        # refresh list of inputs
        self.graph_idx = 0
        self.x = [0]*100
        self.y = [0]*100
        self.data_line.setData(self.x, self.y) 
        self.graph_sel.clear()
        self.update()
        items = [i.split(':')[0] for i in self.input]
        self.graph_sel.addItems(items)


    def textsend(self):
        ser.write(self.output.encode())

    def textadd(self, text):
        self.output = (text)

ser = serial.Serial()
ser.baudrate = 9600
ser.port = PORT_LEFT 
try:
    ser.open()
except:
    print("There was an issue when opening the serial port")
app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()