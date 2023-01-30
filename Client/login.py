import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from define import *
form_class = uic.loadUiType("log.ui")[0]

def Log():
    app = QApplication(sys.argv)
    win = LogWindow()
    win.show()
    app.exec_()

    # 채팅을 시작하기 위해 사용자 매개변수를 반환한다.
    return (win.name, win.addr, win.prt)


class LogWindow(QMainWindow, form_class):

    def __init__(self):

        super(QMainWindow, self).__init__()

        self.setupUi(self)
        self.name = False
        self.addr = False
        self.prt = False
        self.entrance_btn.clicked.connect(self.login)
        

    def login(self):
            # 입력 받기 
            self.name = self.user_name.text()
            self.addr = str(self.user_ip.text())
            self.prt = self.user_port.text()

            # 입력 값 중 하나가 비어 있으면 기본값이 전송된다.

            if len(self.name) ==0:
                self.name = 'User'
            if len(self.addr) ==0:
                self.addr = SERVER
            if len(self.prt) ==0:
                self.prt = PORT
            self.close()
    # 키보드 입력 감지
    def keyPressEvent(self, event):

        # 키보드 입력 저장
        key = event.key()
        # 키보드 입력이 반환인 경우 (ENTER)
        if key == QtCore.Qt.Key_Return: 
            self.login()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LogWindow()
    win.show()
    app.exec_()
