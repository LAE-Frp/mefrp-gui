from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import PyQt5


class Ui_Dialog(object):
    def setupUi(self, Dialog, label_text):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 180)
        Dialog.setWindowTitle(u"Mirror Edge Frp \u5ba2\u6237\u7aef - V1.7 Released")
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(300, 140, 75, 23))
        self.pushButton.setText(u"\u786e\u5b9a")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 30, 341, 71))
        font = QFont()
        font.setFamily(u"SimSun-ExtB")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setText(label_text)
        self.label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)

        self.pushButton.clicked.connect(Dialog.close)
        Dialog.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint | PyQt5.QtCore.Qt.WindowCloseButtonHint)

        QMetaObject.connectSlotsByName(Dialog)


class ShowInfoDialog(QWidget, Ui_Dialog):
    def __init__(self, label_text):
        super().__init__()
        self.setupUi(self, label_text)

    def show_dialog(self):
        self.show()
