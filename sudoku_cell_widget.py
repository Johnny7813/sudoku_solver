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

__version__ = "0.6.1"


class SudokuCellWidget(QtWidgets.QFrame):
    metrics    = {"cellWidth": 72, "cLineWidth": 2, "font": "Noto Sans", "fontSize": 20, "centralFontSize": 40}
    textPoints = [QPoint(25,49), QPoint(11, 23), QPoint(30, 23), QPoint(49, 23), QPoint(11, 43),
                  QPoint(30, 43), QPoint(49, 43), QPoint(11, 63), QPoint(30, 63), QPoint(49, 63)]
    Colors   = {"normal": QColor(255,255,255), "level1": QColor(196, 219, 255),
                  "level2": QColor(215, 158, 250), "frame": QColor(215, 158, 250),
                "innerRect": QColor(255, 0, 0), "black": QColor(0, 0, 0)}

    def __init__(self, mcell, parent, index=None):
        super().__init__(parent)

        self.myCell  = mcell
        self.myIndex = index

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        # set frame style as plain and box
        self.setFrameStyle(QFrame.Plain | QFrame.Panel)  # QFrame.Plain | QFrame.Box == 17
        self.bgHighlight     = "normal"
        self.frameHightlight = False

        tWidth = SudokuCellWidget.metrics["cellWidth"]
        self.setFixedSize(tWidth, tWidth)

        lineWidth = SudokuCellWidget.metrics["cLineWidth"]
        self.setLineWidth(lineWidth)
        rect = QtCore.QRect(0, 0, tWidth, tWidth)   # x,y, with, height
        self.setFrameRect(rect)

        # inner rectangel for marking square
        iWidth = tWidth-2*lineWidth
        self.innerRect = QtCore.QRect(lineWidth, lineWidth, iWidth, iWidth)
        #print("Inner rect = ", self.innerRect)



    # function not needed just used for trying stuff
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


    # set level of background highlight
    # possible values are: normal, level1, level2
    def setBgHighlight(self, word):
        self.bgHighlight = word


    # retrieve background color depending on state of the widget
    # TODO: this can be expanded
    def backgroundColor(self):
        bgColor = self.__class__.Colors[self.bgHighlight]
        return bgColor


    # main paint function
    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)

        painter = QPainter(self)
        # draw background
        bg = self.backgroundColor();
        painter.setBrush(QBrush(bg));
        painter.drawRect(event.rect())

        fName     = SudokuCellWidget.metrics["font"]
        lineWidth = SudokuCellWidget.metrics["cLineWidth"]
        #fSize   = SudokuCellWidget.metrics["fontSize"]

        font         = QFont(fName)
        fgFocusColor = SudokuCellWidget.Colors["innerRect"]


        if self.hasFocus():
            painter.save()
            pen   = painter.pen()
            pen.setWidth(lineWidth+1)
            pen.setColor(fgFocusColor)
            pen.setJoinStyle(Qt.MiterJoin)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush)) # leaves rect empty
            painter.drawRect(self.innerRect)
            painter.restore()



        if self.myCell.isSolved():
            val   = self.myCell.value()
            point = SudokuCellWidget.textPoints[0]
            fSize = SudokuCellWidget.metrics["centralFontSize"]

            if self.hasFocus():
                pen   = painter.pen()
                pen.setColor(fgFocusColor)
                painter.setPen(pen)
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


    # This cell widget gets focus. We print the cell number
    def focusInEvent(self, event):
        super().focusInEvent(event)
        print(self.myIndex)