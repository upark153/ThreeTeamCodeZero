import sys
import socket
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import threading
import pymysql

# 소켓 정의
HEADER = 64  # 기본 메세지 크기 (바이트)
FORMAT = "utf-8"  # 인코딩 형식

SERVER = socket.gethostbyname(socket.gethostname())  # IP 주소 (로컬)
PORT = 5456  # 통신용 포트
ADDR = (SERVER, PORT)

# 시스템 통신용 번호
NEW_MESSAGE = '0'
NAME_LIST = '1'
CLEAR_LIST = '2'
DISCONNECT_MESSAGE = '3'
SAVE_LIST = '4'

form_class = uic.loadUiType("chatroom.ui")[0]
con = pymysql.connect(host='localhost', user='root', password='0000', db='newschema', charset='utf8')  # 한글처리 (charset = 'utf8')
cur = con.cursor()


class MySignal(QtCore.QObject):
    listUser = QtCore.pyqtSignal(str)
    chatLabel = QtCore.pyqtSignal(str)


class LogWindow(QMainWindow, form_class):

    def __init__(self):

        super(QMainWindow, self).__init__()

        self.setupUi(self)
        self.tabWidget.setCurrentIndex(0)

        self.name = False
        self.addr = False
        self.prt = False

        self.entrance_btn.clicked.connect(self.login)
        self.onechat_btn.clicked.connect(self.chatting)
        self.twochat_btn.clicked.connect(self.chatting)
        self.threechat_btn.clicked.connect(self.chatting)



        self.chat_exit_btn.clicked.connect(self.waitroom)
        self.msg_history_btn.clicked.connect(self.viewhistory)
        self.history_table.cellClicked.connect(self.history_show)
        self.history_table.cellDoubleClicked.connect(self.history_show)

    def history_show(self, row, col):
        data = self.history_table.item(row, col)
        print("셀 클릭 셀 값 : ", data.text())
        print(data.text())
        # sql1 = f"update restaurant.inquiries set reply = '{reply1}' where customer_id = '{self.clicked_inquiry}' or inquiry = '{self.clicked_inquiry}'"
        sql = f"select user_id, message, time from newschema.chatting1 where time = '{data.text()}' or user_id = '{data.text()}'"
        # sql = f"select * from newschema.chatting1 where time like 'str(2023)'"

        cur.execute(sql)

        message = cur.fetchall()
        print(message)
        con.commit()

        message_list = []
        for i in message:
            message_list.append(i)

        self.message_table.setRowCount(len(message))  # 테이블의 행 갯수를 rows의 길이로 정함
        self.message_table.setColumnCount(len(message[0]))

        for i in range(len(message_list)):
            for j in range(len(message_list[i])):
                self.message_table.setItem(i, j, QTableWidgetItem(str(message_list[i][j])))


    def viewhistory(self):
        self.tabWidget.setCurrentIndex(3)

        # sql1 = f"update restaurant.inquiries set reply = '{reply1}' where customer_id = '{self.clicked_inquiry}' or inquiry = '{self.clicked_inquiry}'"
        sql = f"select distinct user_id, time from newschema.chatting1"
        cur.execute(sql)

        history = cur.fetchall()
        con.commit()

        history_list = []
        for i in history:
            history_list.append(i)

        #tableWidget setting

        self.history_table.setColumnWidth(0, round(self.width() * 1 / 2))
        self.history_table.setColumnWidth(1, round(self.width() * 1 / 2))

        self.message_table.setColumnWidth(0, round(self.width() * 1 / 10))
        self.message_table.setColumnWidth(1, round(self.width() * 3 / 10))
        self.message_table.setColumnWidth(2, round(self.width() * 6 / 10))

        # table.setColumnWidth(2, self.width() * 5 / 10)

        self.history_table.setRowCount(len(history))  # 테이블의 행 갯수를 rows의 길이로 정함
        self.history_table.setColumnCount(len(history[0]))

        for i in range(len(history_list)):
            for j in range(len(history_list[i])):
                self.history_table.setItem(i, j, QTableWidgetItem(str(history_list[i][j])))


    def waitroom(self):
        reply = QMessageBox.question(self, '메세지', '채팅방에서 나가시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.prt = PORT
            QMessageBox.information(self, 'Quit', f'채팅방에서 나갑니다.')
            self.tabWidget.setCurrentIndex(1)
            self.closeEvent()
            # Client.disconnect(self)
        else:
            pass

    def chatting(self):
        reply = QMessageBox.question(self, '메세지', '채팅방에 접속하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.prt = PORT
            QMessageBox.information(self, '접속', f'{self.prt}포트 채팅방에 접속하였습니다.')
            self.tabWidget.setCurrentIndex(2)
            self.Chat(self.name, self.addr, self.prt)
        else:
            pass

    def login(self):
        # 입력 받기
        self.name = self.user_name.text()
        self.addr = str(self.user_ip.text())
        # self.prt = self.user_port.text()

        # 입력 값 중 하나가 비어 있으면 기본값이 전송된다.

        if len(self.name) == 0:
            self.name = 'User'
        if len(self.addr) == 0:
            self.addr = SERVER
        # if len(self.prt) ==0:
        #     self.prt = PORT
        self.tabWidget.setCurrentIndex(1)

    # 키보드 입력 감지
    def keyPressEvent(self, event):
        # 키보드 입력 저장
        key = event.key()
        # 키보드 입력이 반환인 경우 (ENTER)
        if key == QtCore.Qt.Key_Return:
            self.entrance_btn.click()

    def Chat(self, username, address, port):

        self.signal = MySignal()
        self.signal.listUser.connect(self.listUpdate)
        self.signal.chatLabel.connect(self.chatUpdate)

        self.client = Client(username, address, port, self)

        self.msg_send_btn.clicked.connect(self.newmsg)

    def newmsg(self):

        msg = self.msg_lienEdit.text()
        if (msg):
            self.client.sendMsg(msg, NEW_MESSAGE)
            self.msg_lienEdit.setText('')

    def chatUpdate(self, str):
        self.chat.append(str)

    def listUpdate(self, str):

        if (str == ''):
            self.userList.clear()

        else:
            self.userList.append(str)

    def keyPressEvent(self, event):

        key = event.key()

        if key == QtCore.Qt.Key_Return:
            self.msg_send_btn.click()

    def closeEvent(self):

        if (self.client.online):
            self.client.disconnect()

            # self.close()


# 클라이언트 작업자 클래스
# 소켓 연결 관리
# 메세지 수신 및 처리
# 메세지 전송 처리

class Client():

    # 소켓 클라이언트 초기화
    def __init__(self, username, address, port, win):
        # 연결 유형 정리
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 소켓 서버와 연결
        ADDR = (address, int(port))
        self.client.connect(ADDR)

        # 매개변수 수신
        self.username = username  # 인스턴스 사용자 이름 설정
        self.win = win  # 통신창 참조 저장
        self.online = True  # 클라이언트를 온라인으로 설정

        # 사용자 이름을 서버로 보내기

        message, send_length = encodeMsg(self.username)
        self.client.send(send_length)  # 메세지 크기
        self.client.send(message)  # 메세지

        # 메세지를 받을 쓰레드 생성
        self.thread_recv = threading.Thread(target=self.recvMsg, args=())
        self.thread_recv.start()

    # 메세지 수신
    def recvMsg(self):

        while self.online:  # 온라인 상태일 동안만
            try:
                # 서버에서 메세지 받기 위해 대기 중
                msg_length = self.client.recv(HEADER).decode(FORMAT)

                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.client.recv(msg_length).decode(FORMAT)
                    # 메세지 처리를 위한 함수 호출
                    self.handleMsg(msg)

            except:  # 오류 또는 연결 실패가 있는 경우
                self.online = False

    # 메세지 처리
    def handleMsg(self, msg):

        # 메세지에서 태그 분리
        re = msg[0]  # 첫 번째 문자 저장
        msg_list = list(msg)  # 목록으로 변환
        msg_list.pop(0)  # 태그 삭제
        msg = "".join(msg_list)  # 문자열에 저장

        # 수행할 작업 정의
        if (re == NEW_MESSAGE):  # 새로운 메세지 TAG인 경우
            self.win.signal.chatLabel.emit(msg)  # 메세지를 나타내기 위해 인터페이스에 신호 보내기

        elif (re == CLEAR_LIST):  # 목록을 지우는 TAG인 경우
            self.win.signal.listUser.emit('')  # 연결된 사용자 목록을 지우는 창에 빈 신호를 보낸다.

        elif (re == NAME_LIST):  # 이름 목록인 경우
            self.win.signal.listUser.emit(msg)  # 창에 이름 보내기, 연결된 사용자 목록에 추가

    # 메세지 전송
    def sendMsg(self, msg, re):

        if (self.online):  # 사용자가 온라인 상태인 경우
            try:
                msg = re + msg  # 메세지에 태그 추가
                message, send_length = encodeMsg(msg)
                self.client.send(send_length)
                self.client.send(message)
                print('msgmsg: ', message)



            except:  # 통신이 실패할 경우
                self.disconnect()  # 연결 해제

    # 연결 해제
    def disconnect(self):

        if (self.online):
            # 연결 해제 메시지와 함께 신호를 보낸다
            self.win.signal.chatLabel.emit("연결을 끊는 중입니다...")

            # 서버에 연결 해제 메세지 보내기
            message, send_length = encodeMsg(DISCONNECT_MESSAGE)
            self.client.send(send_length)
            self.client.send(message)

            # 클라이언트를 오프라인으로 설정하고 연결을 닫고 신호를 보낸다.
            self.online = False
            self.client.close()
            self.win.signal.chatLabel.emit("연결이 종료 되었습니다.")


# 소켓을 통해 보낼 메세지를 인코드 하는 함수
def encodeMsg(msg):
    message = str(msg).encode(FORMAT)  # UTF-8 형식으로 인코드
    msg_length = len(message)  # 인코딩된 메세지 크기 저장
    send_length = str(msg_length).encode(FORMAT)
    # 정의된 HEADER와 같을 때까지 공백으로 길이 메세지를 완성한다.
    send_length += b' ' * (HEADER - len(send_length))

    return message, send_length


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LogWindow()
    win.show()
    app.exec_()
