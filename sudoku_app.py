# -*- coding: utf-8 -*-

#import sys
#from cell import *
#from board import *
from sudoku_board_widget import *
from PyQt5 import QtCore, QtGui,  QtWidgets
#from PyQt5.QtWidgets import QMainWindow, QWidget
from ui_sudoku_app   import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, desktop):
        super(MainWindow, self).__init__()
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

        self.sudokuModel = modelBoard("sudoku_data.csv", "easy1")
        #QtCore.QCoreApplication.addLibraryPath(".")
        #self.setupUi(self)
        self.setWindowTitle("Sudoku cell test")
        self.setMinimumSize(880, 780)
        self.resize(900, 780)
        self.setObjectName("sudokuMainWindow")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 900, 700))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sudokuWidget = SudokuBoardWidget(self.sudokuModel, self)
        self.horizontalLayout.addWidget(self.sudokuWidget)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName("label")
        self.label.setText("Elimination ")
        font = self.label.font()
        font.setPointSize(14)
        self.label.setFont(font)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.pushButton = QtWidgets.QPushButton("Step", self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pushButton)
        self.horizontalLayout.addLayout(self.formLayout)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 850, 42))
        self.menubar.setObjectName("menubar")
        font = self.label.font()
        font.setPointSize(14)
        self.menubar.setFont(font)
        self.menuFile = QtWidgets.QMenu("File", self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.insertToolBarBreak(self.toolBar)
        self.actionOpen_sudoku = QtWidgets.QAction(self)
        self.actionOpen_sudoku.setObjectName("actionOpen_sudoku")
        self.menuFile.addAction(self.actionOpen_sudoku)
        self.menubar.addAction(self.menuFile.menuAction())





        #self.centralwidget.setHighlightCol(3, row=8, on=True)
        #self.centralwidget.setHighlightSquare(4, 1, extra=True)
        #time.sleep(5)
        #self.centralwidget.setHighlightRow(5, set=False, centre=None)





# start and display application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    desktop = app.desktop()

    main = MainWindow(desktop)
    main.show()

    app.exec_()

sys.exit(0)

