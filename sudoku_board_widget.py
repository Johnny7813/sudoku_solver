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
                sCell = SudokuCellWidget(bCell , self, (i,j))
                sCell.setGeometry(x , y, cWidth, cWidth)
                row.append(sCell)

                x += cWidth
                if j % 3 == 0:
                    x += mlWidth

            self.cellWidgetArrary.append(row)
            y += cWidth
            if i % 3 == 0:
                y += mlWidth

        # update delay when updating the widget
        self.update_delay = 0.5



    # return reference for cellWidget at grid knot i,j
    def at(self, i, j):
        return self.cellWidgetArrary[i-1][j-1]



    # level = "normal", "level1", "level2"
    def _setHightlightIndices(self, indices, level = "normal"):
        for i,j in indices:
            wCell = self.at(i,j)
            wCell.setBgHighlight(level)


    # rowLevel/centreLevel is the highlight level: normal, level1, level2
    # row, col is an optional centre cell widget on that row that can be highlighted
    # if not centre is needed just specify any col index
    def setRowHighlight(self, row, col, rowLevel="normal", centreLevel=None):
        indices = self.model._row_indices(row, col, False)
        self._setHightlightIndices(indices, rowLevel)
        if centreLevel:
            self._setHightlightIndices([(row, col)], centreLevel)


    # colLevel/centreLevel is the highlight level: normal, level1, level2
    # centreRow is an optional centre cell widget on that col that can be highlighted
    def setColHighlight(self, row, col, colLevel="normal", centreLevel=None):
        indices = self.model._col_indices(row, col, False)
        self._setHightlightIndices(indices, colLevel)
        if centreLevel:
            self._setHightlightIndices([(row, col)], centreLevel)


    # colLevel/centreLevel is the highlight level: normal, level1, level2
    # centreRow is an optional centre cell widget on that col that can be highlighted
    def setSquareHighlight(self, row, col, squareLevel="normal", centreLevel=None):
        indices = self.model._square_indices(row, col, False)
        self._setHightlightIndices(indices, squareLevel)
        if centreLevel:
            self._setHightlightIndices([(row, col)], centreLevel)

    # colLevel/centreLevel is the highlight level: normal, level1, level2
    # centreRow is an optional centre cell widget on that col that can be highlighted
    def setSquareHighlightUnique(self, num, squareLevel="normal"):
        indices = self.model._square_indices_unique(num)
        self._setHightlightIndices(indices, squareLevel)



    # eliminate stuff from solved cell given by index
    def eliminate_with_centre(self):
        if not self.model.unexploited_cells:
            print("eliminate_with_centre: unexploited_cells emptry!")
            return
        row, col = self.model.unexploited_cells.popleft()

        ret1 = self.model.eliminateFromRow(row, col, repeat=-1)
        print("eliminate_with_centre ret=",ret1, "row=", row, "col=", col )
        if ret1[0] == 1: #stuff can be eliminated
            self.setRowHighlight(row, col, rowLevel="level1", centreLevel="level2")
            self.repaint()
            time.sleep(self.update_delay)
            self.model.eliminateFromRow(row, col, repeat=2)
            self.repaint()
            time.sleep(self.update_delay)
            self.setRowHighlight(row, col, rowLevel="normal")
            self.repaint()
            self.model.dump3()

        ret1 = self.model.eliminateFromCol(row, col, repeat=-1)
        print("eliminate_with_centre ret=", ret1, "row=", row, "col=", col)
        if ret1[0] == 1:  # stuff can be eliminated
            self.setColHighlight(row, col, colLevel="level1", centreLevel="level2")
            self.repaint()
            time.sleep(self.update_delay)
            self.model.eliminateFromCol(row, col, repeat=2)
            self.repaint()
            time.sleep(self.update_delay)
            self.setColHighlight(row, col, colLevel="normal")
            self.repaint()
            #self.model.dump3()

        ret1 = self.model.eliminateFromSquare(row, col, repeat=-1)
        print("eliminate_with_centre ret=", ret1, "row=", row, "col=", col)
        if ret1[0] == 1:  # stuff can be eliminated
            self.setSquareHighlight(row, col, squareLevel="level1", centreLevel="level2")
            self.repaint()
            time.sleep(self.update_delay)
            self.model.eliminateFromSquare(row, col, repeat=2)
            self.repaint()
            time.sleep(self.update_delay)
            self.setSquareHighlight(row, col, squareLevel="normal")
            self.repaint()
            #self.model.dump3()

        self.model.dump3()


    # eliminate stuff from solved cell given by index
    def hiddenSingelsNext(self):
        for num in range(1,10):
            ret1 = self.model.findHiddenSinglesInRow(num, repeat=-1)
            print("hiddenSinglesNext ret=", ret1, "index=", num )
            if ret1[0] == 1:  # cells can be solved in that row
                self.setRowHighlight(num, 1, rowLevel="level1")
                self.repaint()
                time.sleep(self.update_delay)
                self.model.findHiddenSinglesInRow(num, repeat=2)
                self.repaint()
                time.sleep(self.update_delay)
                self.setRowHighlight(num, 1, rowLevel="normal")
                self.repaint()
                self.model.dump3()
                return True

            ret2 = self.model.findHiddenSinglesInCol(num, repeat=-1)
            if ret2[0] == 1:  # stuff can be eliminated
                self.setColHighlight(1, num, colLevel="level1")
                self.repaint()
                time.sleep(self.update_delay)
                self.model.findHiddenSinglesInCol(num, repeat=2)
                self.repaint()
                time.sleep(self.update_delay)
                self.setColHighlight(1, num, colLevel="normal")
                self.repaint()
                # self.model.dump3()
                return True

            ret3 = self.model.findHiddenSinglesInSquare(num, repeat=-1)
            if ret3[0] == 1:  # stuff can be eliminated
                self.setSquareHighlightUnique(num, squareLevel="level1")
                self.repaint()
                time.sleep(self.update_delay)
                self.model.findHiddenSinglesInSquare(num, repeat=2)
                self.repaint()
                time.sleep(self.update_delay)
                #self.setColHighlight(1, num, colLevel="normal")
                self.setSquareHighlightUnique(num, squareLevel="normal")
                self.repaint()
                # self.model.dump3()
                return True


        self.model.dump3()
        return False






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



