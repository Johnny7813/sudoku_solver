# -*- coding: utf-8 -*-

from cell import *
from collections import deque
from itertools import product
from termcolor import colored
import copy
import distutils.text_file
import sys
from PyQt5 import QtCore, QtGui,  QtWidgets
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets  import *  #QFrame, QMainWindow
from PyQt5.QtGui import *
from PyQt5.QtCore import *

__version__ = "0.5.1"


class SudokuCellWidget(QtWidgets.QFrame):
    metrics    = {"cellWidth": 72, "cLineWidth": 2, "font": "Noto Sans", "fontSize": 20, "centralFontSize": 40}
    textPoints = [QPoint(25,49), QPoint(11, 23), QPoint(30, 23), QPoint(49, 23), QPoint(11, 43),
                  QPoint(30, 43), QPoint(49, 43), QPoint(11, 63), QPoint(30, 63), QPoint(49, 63)]
    colors     = {"normal": QColor(255,255,255), "highlight1": QColor(196, 219, 255),
                  "highlight2": QColor(215, 158, 250)}

    def __init__(self, mcell, parent):
        super().__init__(parent)

        self.myCell = mcell
        # set frame style as plain and box
        self.setFrameStyle(QFrame.Plain | QFrame.Panel)  # QFrame.Plain | QFrame.Box == 17
        self.setBackground("normal")

        tWidth = SudokuCellWidget.metrics["cellWidth"]
        self.setFixedSize(tWidth, tWidth)

        lineWidth = SudokuCellWidget.metrics["cLineWidth"]
        self.setLineWidth(lineWidth)
        rect = QtCore.QRect(0, 0, tWidth, tWidth)   # x,y, with, height
        self.setFrameRect(rect)




    # try metric, fonts etc
    def experiment(self):
        db = QFontDatabase()
        fonts = db.families()
        #print(fonts)

        # important dimension
        print("Frame Width: ", self.frameWidth(), "Line Width: ", self.lineWidth(),
              "Mid Line Width: ", self.midLineWidth())

        painter = QPainter(self)



        fName = SudokuCellWidget.const["font"]
        fSize = SudokuCellWidget.const["fontSize"]

        font  = QFont(fName)
        font.setPixelSize(fSize)
        painter.setFont(font)
        print("Font ", font.family())

        # unit is always pixel
        metrics = QFontMetrics(font)
        print("Descent: ", metrics.descent(), "Height: ", metrics.height())

        for i in range(1,10):
            mRect = metrics.boundingRect(str(i))
            print("Number ", i, " , bounding Rect: ", mRect, " Width: ", mRect.width(), mRect.width()//2 )


    # set background
    def setBackground(self, name):
        pal    = self.palette()
        bColor = SudokuCellWidget.colors[name]
        pal.setColor(QPalette.Background, bColor)
        self.setAutoFillBackground(True)
        self.setPalette(pal)



    # main paint function
    def paintEvent(self, event: QtGui.QPaintEvent):

        super().paintEvent(event)

        painter = QPainter(self)
        fName   = SudokuCellWidget.metrics["font"]
        fSize   = SudokuCellWidget.metrics["fontSize"]

        font    = QFont(fName)


        #pen = painter.pen()


        #painter.drawLine(QPoint(0,0), QPoint(0,10))
        if self.myCell.isSolved():
            val   = self.myCell.value()
            point = SudokuCellWidget.textPoints[0]
            fSize = SudokuCellWidget.metrics["centralFontSize"]

            font.setPixelSize(fSize)
            painter.setFont(font)
            painter.drawText(point, str(val))
        else:
            fSize = SudokuCellWidget.metrics["fontSize"]
            font.setPixelSize(fSize)
            painter.setFont(font)
            for i in self.myCell:
                point = SudokuCellWidget.textPoints[i]
                painter.drawText(point, str(i))


