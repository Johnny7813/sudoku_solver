# -*- coding: utf-8 -*-


import sys
from cell import *
from board import *
from sudoku_cell_widget import *
from PyQt5 import QtCore, QtGui,  QtWidgets
from PyQt5.QtWidgets  import *  #QFrame, QMainWindow
import time


class SudokuBoardWidget(QFrame):
    metrics = {"cellWidth": 72, "cLineWidth": 2, "font": "Noto Sans", "fontSize": 20, "centralFontSize": 40,
               "mLineWidth": 4}

    def __init__(self, model,  parent):
        super().__init__(parent)

        self.model = model
        self.cellWidgetArrary = []

        mlWidth = SudokuBoardWidget.metrics["mLineWidth"]
        clWidth = SudokuBoardWidget.metrics["cLineWidth"]
        cWidth  = SudokuBoardWidget.metrics["cellWidth"]
        bWidth  = SudokuBoardWidget.metrics["cellWidth"]*9 + mlWidth*4

        self.setFixedSize(bWidth, bWidth)
        self.setFrameStyle(QFrame.Plain | QFrame.Panel)  # QFrame.Plain | QFrame.Box == 17
        self.setLineWidth(mlWidth)
        rect = QtCore.QRect(0, 0, bWidth, bWidth)  # x,y, with, height
        self.setFrameRect(rect)

        x = mlWidth
        y = mlWidth
        for i in range(1,10):
            x   = mlWidth
            row = []
            for j in range(1,10):
                bCell = self.model.at(i,j)
                sCell = SudokuCellWidget(bCell , self)
                sCell.setGeometry(x , y, cWidth, cWidth)
                row.append(sCell)

                x += cWidth
                if j % 3 == 0:
                    x += mlWidth

            self.cellWidgetArrary.append(row)
            y += cWidth
            if i % 3 == 0:
                y += mlWidth




    # return reference for cellWidget at grid knot i,j
    def at(self, i, j):
        return self.cellWidgetArrary[i-1][j-1]


    def _setHightlightUnit(self, indices, on=True, centre=None):
        if on:
            name = "highlight1"
        else:
            name = "normal"

        for i,j in indices:
            wCell = self.at(i,j)
            wCell.setBackground(name)

        if centre and on:
            wCell = self.at(*centre)
            wCell.setBackground("highlight2")


    # level = "normal", "highlight1", "highlight2"
    def _setHightlightIndices(self, indices, level = "normal"):
        for i,j in indices:
            wCell = self.at(i,j)
            wCell.setBackground(level)


    # centre is a column index in row
    def setHighlightRow(self, row, col=-1, on=True):
        levelA = "highlight1"
        levelB = "highlight2"
        remove = False
        extra  = None

        if on:
            if col > 0:
                extra = [(row, col)]
                remove = True
            else:
                col    = 1
        else:
            levelA = "normal"
            levelB = "normal"

        indices = self.model._row_indices(row, col, remove)
        self._setHightlightIndices(indices, levelA)
        if extra:
            self._setHightlightIndices(extra, levelB)


    # centre is a column index in row
    def setHighlightCol(self, col, row=-1, on=True):
        levelA = "highlight1"
        levelB = "highlight2"
        remove = False
        extra  = None

        if on:
            if row > 0:
                extra = [(row, col)]
                remove = True
            else:
                row = 1
        else:
            levelA = "normal"
            levelB = "normal"

        indices = self.model._col_indices(row, col, remove)
        self._setHightlightIndices(indices, levelA)
        if extra:
            self._setHightlightIndices(extra, levelB)



    # centre is a column index in row
    def setHighlightSquare(self, row, col, centre=False, on=True):
        levelA = "highlight1"
        levelB = "highlight2"
        remove = False
        index  = None

        if on:
            if centre:
                index = [(row, col)]
                remove = True
        else:
            levelA = "normal"
            levelB = "normal"

        indices = self.model._square_indices(row, col, remove)
        self._setHightlightIndices(indices, levelA)
        if index:
            self._setHightlightIndices(index, levelB)


    # eliminate stuff from solved cell given by index
    def eliminate_with_centre(self):
        if not self.model.unexploited_cells:
            print("eliminate_with_centre: unexploited_cells emptry!")
            return
        row, col = self.model.unexploited_cells.popleft()
        delay    = 0.5

        ret1 = self.model.eliminateFromRow(row, col, repeat=-1)
        print("eliminate_with_centre ret=",ret1, "row=", row, "col=", col )
        if ret1[0] == 1: #stuff can be eliminated
            self.setHighlightRow(row, col=col, on=True)
            self.repaint()
            time.sleep(delay)
            self.model.eliminateFromRow(row, col, repeat=2)
            self.repaint()
            time.sleep(delay)
            self.setHighlightRow(row, col=col, on=False)
            #self.model.dump3()

        ret1 = self.model.eliminateFromCol(row, col, repeat=-1)
        print("eliminate_with_centre ret=", ret1, "row=", row, "col=", col)
        if ret1[0] == 1:  # stuff can be eliminated
            self.setHighlightCol(col, row=row, on=True)
            self.repaint()
            time.sleep(delay)
            self.model.eliminateFromCol(row, col, repeat=2)
            self.repaint()
            time.sleep(delay)
            self.setHighlightCol(col, row=row, on=False)
            #self.model.dump3()

        ret1 = self.model.eliminateFromSquare(row, col, repeat=-1)
        print("eliminate_with_centre ret=", ret1, "row=", row, "col=", col)
        if ret1[0] == 1:  # stuff can be eliminated
            self.setHighlightSquare(row, col, centre=True, on=True)
            self.repaint()
            time.sleep(delay)
            self.model.eliminateFromSquare(row, col, repeat=2)
            self.repaint()
            time.sleep(delay)
            self.setHighlightSquare(row, col, centre=True, on=False)
            #self.model.dump3()

        self.model.dump3()


    def paintEvent(self, event):
        super().paintEvent(event)

        mlWidth = SudokuBoardWidget.metrics["mLineWidth"]
        clWidth = SudokuBoardWidget.metrics["cLineWidth"]
        cWidth = SudokuBoardWidget.metrics["cellWidth"]
        bWidth = SudokuBoardWidget.metrics["cellWidth"] * 9 + mlWidth * 4


        painter = QPainter(self)
        pen     = painter.pen()
        brush   = painter.brush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        x = mlWidth+3*cWidth
        y = 0
        painter.drawRect(x, y, mlWidth, bWidth)
        x += mlWidth+3*cWidth
        painter.drawRect(x, y, mlWidth, bWidth)

        x = 0
        y = mlWidth + 3 * cWidth
        painter.drawRect(x, y, bWidth, mlWidth)
        y += mlWidth + 3 * cWidth
        painter.drawRect(x, y, bWidth, mlWidth)



