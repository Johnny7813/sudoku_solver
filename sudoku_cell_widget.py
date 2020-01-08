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

__version__ = "0.6.5"


class SudokuCellWidget(QtWidgets.QFrame):
    metrics    = {"cellWidth": 72, "cLineWidth": 2, "font": "Noto Sans", "fontSize": 20, "centralFontSize": 40}
    textPoints = [QPoint(25,49), QPoint(11, 21), QPoint(30, 21), QPoint(49, 21), QPoint(11, 43),
                  QPoint(30, 43), QPoint(49, 43), QPoint(11, 65), QPoint(30, 65), QPoint(49, 65)]
    haloRects  = ([QPoint(8,4), QPoint(27,4), QPoint(46,4), QPoint(8,26), QPoint(27,26),
                   QPoint(46,26), QPoint(8,48), QPoint(27,48), QPoint(46,48)], QSize(16,19))
    Colors     = {"normal": QColor(255,255,255), "level1": QColor(196, 219, 255),
                  "level2": QColor(215, 158, 250), "frame": QColor(215, 158, 250),
                "innerRect": QColor(255, 0, 0), "black": QColor(0, 0, 0),
                "redHalo": QColor(255, 0, 0), "greenHalo": QColor(0, 230, 0)}

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

        # these numbers of the cell are printed in red
        self.redNumbers = set()

        # red number halo highlight
        self.redNumbersHalo = set()

        # green number halo highlight
        self.greenNumbersHalo = set()



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


    # values = set of candidates in the cell
    # mode = "red", "green", None
    # set Halo Values and color
    def setHaloValues(self,values, mode=None):
        if mode == "red":
            self.redNumbersHalo.clear()
            self.redNumbersHalo |= (self.myCell & values)
        elif mode == "green":
            self.greenNumbersHalo.clear()
            self.greenNumbersHalo |= (self.myCell & values)
        elif mode == None:
            self.redNumbersHalo.clear()
            self.greenNumbersHalo.clear()


    # main paint function
    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)

        # draw background
        painter = QPainter(self)
        bg = self.backgroundColor()
        painter.setBrush(QBrush(bg))
        painter.drawRect(event.rect())

        # draw Halo background colors
        redHalo    = SudokuCellWidget.Colors["redHalo"]
        greenHalo  = SudokuCellWidget.Colors["greenHalo"]
        haloPoints = SudokuCellWidget.haloRects[0]
        haloSize   = SudokuCellWidget.haloRects[1]
        if not self.myCell.isSolved():
            # green Halo
            for i in self.redNumbersHalo:
                point = haloPoints[i-1]
                rect  = QRect(point, haloSize)
                painter.setBrush(QBrush(redHalo))
                #painter.drawRect(rect)
                painter.drawRoundedRect(rect, 3,3)

            # red Halo
            if not self.myCell.isSolved():
                for i in self.greenNumbersHalo:
                    point = haloPoints[i - 1]
                    rect = QRect(point, haloSize)
                    painter.setBrush(QBrush(greenHalo))
                    # painter.drawRect(rect)
                    painter.drawRoundedRect(rect, 3, 3)


        fName     = SudokuCellWidget.metrics["font"]
        lineWidth = SudokuCellWidget.metrics["cLineWidth"]
        #fSize   = SudokuCellWidget.metrics["fontSize"]

        font         = QFont(fName)
        fgFocusColor = SudokuCellWidget.Colors["innerRect"]


        # draw red frame around square if it is in focus
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


        redPen = painter.pen()
        redPen.setColor(fgFocusColor)
        blackPen = painter.pen()

        # draw the numbers.
        # if cell is solved draw it big and centered
        if self.myCell.isSolved():
            val   = self.myCell.value()
            point = SudokuCellWidget.textPoints[0]
            fSize = SudokuCellWidget.metrics["centralFontSize"]
            if val in self.redNumbers:
                painter.setPen(redPen)
            font.setPixelSize(fSize)
            painter.setFont(font)
            painter.drawText(point, str(val))
        else:
            redNumbers   = self.myCell & self.redNumbers
            blackNumbers = self.myCell - self.redNumbers
            fSize = SudokuCellWidget.metrics["fontSize"]
            font.setPixelSize(fSize)
            painter.setFont(font)

            painter.setPen(blackPen)
            for i in blackNumbers:
                point = SudokuCellWidget.textPoints[i]
                painter.drawText(point, str(i))
            painter.setPen(redPen)
            for i in redNumbers:
                point = SudokuCellWidget.textPoints[i]
                painter.drawText(point, str(i))


    # This cell widget gets focus. We print the cell number
    def focusInEvent(self, event):
        super().focusInEvent(event)
        print(self.myIndex)