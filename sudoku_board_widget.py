# -*- coding: utf-8 -*-

import sys
from cell import *
from sudoku_cell_widget import *
from PyQt5 import QtCore, QtGui,  QtWidgets
from PyQt5.QtWidgets  import *  #QFrame, QMainWindow


class SudokuBoardWidget(QFrame):
    pass



# multiple inheritance
class MainWindow(QMainWindow):
    def __init__(self, desktop):

        super(MainWindow, self).__init__()
        #QtCore.QCoreApplication.addLibraryPath(".")
        #self.setupUi(self)

        self.setObjectName("MainWindow")
        self.setWindowTitle("Sudoku cell test")

        self.setMinimumSize(140, 140)
        self.setMaximumSize(240, 240)
        self.resize(210, 210)

        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

        mcell = cell([1,3,4,7,8])
        mcell2 = cell(5)
        self.centralwidget = SudokuCellWidget(mcell, self)



# start and display application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    desktop = app.desktop()

    main = MainWindow(desktop)
    main.show()

    app.exec_()

sys.exit(0)

