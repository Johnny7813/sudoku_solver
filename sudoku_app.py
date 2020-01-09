# -*- coding: utf-8 -*-


from sudoku_board_widget import *
from PyQt5 import QtCore, QtGui,  QtWidgets
from board import *
#from PyQt5.QtWidgets import QMainWindow, QWidget
#from ui_sudoku_app   import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, desktop):
        super(MainWindow, self).__init__()
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.sudokuModel = sudokuModelBoard("sudoku_data.csv", "easy1")
        self.setWindowTitle("Sudoku Application Test")
        self.setMinimumSize(950, 780)
        self.resize(960, 780)
        self.setObjectName("sudokuMainWindow")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 950, 700))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sudokuWidget = SudokuBoardWidget(self.sudokuModel, self)
        self.horizontalLayout.addWidget(self.sudokuWidget)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label1 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label1.setObjectName("label")
        self.label1.setText("Elimination ")
        font = self.label1.font()
        font.setPointSize(14)
        self.label1.setFont(font)
        self.label2 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label2.setObjectName("label")
        self.label2.setText("Hidden Singles ")
        font = self.label2.font()
        font.setPointSize(14)
        self.label2.setFont(font)
        self.label3 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label3.setObjectName("label")
        self.label3.setText("Hidden  ")
        font = self.label3.font()
        font.setPointSize(14)
        self.label3.setFont(font)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label1)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label2)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label3)
        self.pushButton1 = QtWidgets.QPushButton("Step", self.horizontalLayoutWidget)
        self.pushButton1.setObjectName("pushButton1")
        self.pushButton2 = QtWidgets.QPushButton("Step", self.horizontalLayoutWidget)
        self.pushButton2.setObjectName("pushButton2")
        self.pushButton3 = QtWidgets.QPushButton("find", self.horizontalLayoutWidget)
        self.pushButton3.setObjectName("pushButton3")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pushButton1)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.pushButton2)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.pushButton3)
        self.horizontalLayout.addSpacing(20)
        self.horizontalLayout.addLayout(self.formLayout)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setFont(font)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 850, 42))
        self.menubar.setObjectName("menubar")
        font = self.menubar.font()
        font.setWeight(50)
        font.setPointSize(14)
        self.menubar.setFont(font)
        self.menuFile = QtWidgets.QMenu("File", self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")
        self.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.insertToolBarBreak(self.toolBar)
        self.actionOpen_sudoku = QtWidgets.QAction(self)
        self.actionOpen_sudoku.setObjectName("actionOpen_sudoku")
        self.menuFile.addAction(self.actionOpen_sudoku)
        self.menubar.addAction(self.menuFile.menuAction())

        # add quit action
        self.actionQuit = QtWidgets.QAction(self)
        quitIcon = QtGui.QIcon()
        quitIcon.addPixmap(QtGui.QPixmap("./icons/application-exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        quitIcon.addPixmap(QtGui.QPixmap("./icons/application-exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionQuit.setIcon(quitIcon)
        self.actionQuit.setObjectName("actionQuit")
        self.actionQuit.setText("Quit")
        self.actionQuit.setShortcut("Ctrl+Q")
        self.menuFile.addAction(self.actionQuit)
        self.toolBar.addAction(self.actionQuit)

        #self.actionMaking_Backups.toggled.connect(self.backup.run)
        self.pushButton1.clicked.connect(self.sudokuWidget.eliminate_with_centre)
        self.pushButton2.clicked.connect(self.sudokuWidget.hiddenSingelsNext)
        self.pushButton3.clicked.connect(self.sudokuWidget.findNextHiddenPairs)
        self.actionQuit.triggered.connect(self.close)


        



# start and display application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    desktop = app.desktop()

    main = MainWindow(desktop)
    main.show()

    app.exec_()

sys.exit(0)

