# -*- coding: utf-8 -*-

import sys
from cell import *
from sudoku_cell_widget import *
from PyQt5 import QtCore, QtGui,  QtWidgets
from PyQt5.QtWidgets  import *  #QFrame, QMainWindow


class SudokuBoardWidget(QFrame):
    metrics = {"cellWidth": 72, "cLineWidth": 2, "font": "Noto Sans", "fontSize": 20, "centralFontSize": 40,
               "mLineWidth": 4}

    def __init__(self, parent):
        super().__init__(parent)

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
                sCell = SudokuCellWidget(cell() , self)
                sCell.setGeometry(x , y, cWidth, cWidth)
                row.append(sCell)

                x += cWidth
                if j % 3 == 0:
                    x += mlWidth

            self.cellWidgetArrary.append(row)
            y += cWidth
            if i % 3 == 0:
                y += mlWidth




        lineV1 = QFrame(self)
        lineV1.setFrameStyle(QFrame.Plain | QFrame.VLine)
        lineV1.setLineWidth(3)
        lineV1.setFixedSize(4, bWidth)
        x = mlWidth + 3*cWidth
        lineV1.setGeometry(x, 0, mlWidth, bWidth)

        #lineV2 = QFrame(self)
        #lineV2.setFrameStyle(QFrame.Plain | QFrame.VLine)
        #lineV2.setLineWidth(3)
        #lineV2.setFixedWidth(8)

        #grid.addWidget(lineV1, 1, 4, 11, 1)
        #grid.addWidget(lineV2, 1, 8, 11, 1)


    # return reference for cellWidget at grid knot i,j
    def at(self, i, j):
        return self.cellWidgetArrary[i-1][j-1]



# multiple inheritance
class MainWindow(QMainWindow):
    def __init__(self, desktop):

        super(MainWindow, self).__init__()
        #QtCore.QCoreApplication.addLibraryPath(".")
        #self.setupUi(self)

        self.setObjectName("MainWindow")
        self.setWindowTitle("Sudoku cell test")

        self.setMinimumSize(700, 700)
        self.setMaximumSize(800, 800)
        self.resize(750, 750)

        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

        #mcell = cell([1,3,4,7,8])
        #mcell2 = cell(5)
        self.centralwidget = SudokuBoardWidget(self)



# start and display application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    desktop = app.desktop()

    main = MainWindow(desktop)
    main.show()

    app.exec_()

sys.exit(0)

