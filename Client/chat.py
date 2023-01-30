import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from define import *
from loginclient import Client


# 채팅 창 신호 클래스
class MySignal(QtCore.QObject):

    listUser = QtCore.pyqtSignal(str)
    chatLabel = QtCore.pyqtSignal(str)

form_class = uic.loadUiType("main.ui")[0]


class MainWindow(QMainWindow, form_class):

    def __init__(self, username, address, port):

        super(QMainWindow, self).__init__()

        self.signal = MySignal()
        self.signal.listUser.connect(self.listUpdate)
        self.signal.chatLabel.connect(self.chatUpdate)

        self.client = Client(username, address, port, self)

        self.setupUi(self)
        self.msg_send_btn.clicked.connect(self.newmsg)
    
    def newmsg(self):

        msg = self.msg_lienEdit.text()
        if(msg):

            self.client.sendMsg(msg, NEW_MESSAGE)
            self.msg_lienEdit.setText('')
    
    def chatUpdate(self, str):
        self.chat.append(str)
    
    def listUpdate(self, str):

        if(str == ''):
            self.userList.clear()
        
        else:
            self.userList.append(str)

    def keyPressEvent(self, event):

        key = event.key()

        if key == QtCore.Qt.Key_Return:
            self.msg_send_btn.click()
    
    def closeEvent(self, event):

        if(self.client.online):
            self.client.disconnect()

        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow("User", ADDR, PORT)

    win.show()
    app.exec_()