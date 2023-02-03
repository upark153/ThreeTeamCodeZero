import threading
import socket
from datetime import datetime
import win32api
import pymysql

HEADER = 64  # 기본 메세지 크기 (바이트)
FORMAT = "utf-8"  # 인코딩 형식

SERVER = socket.gethostbyname(socket.gethostname())  # IP 주소 (로컬)
PORT = 9058  # 통신용 포트
ADDR = (SERVER, PORT)
# 시스템 통신용 번호
NEW_MESSAGE = '0'
NAME_LIST = '1'
CLEAR_LIST = '2'
DISCONNECT_MESSAGE = '3'
SAVE_LIST = '4'
MEMBER_INVITE = '5'

con = pymysql.connect(host='localhost', user='root', password='0000', db='newschema', charset='utf8')  # 한글처리 (charset = 'utf8')
cur = con.cursor()


# 서버 메인 클래스
# 소켓 서버 연결 및 닫기
# 새로운 연결을 얻고, 연결 해제 관리
# 유저에게 보내는 메시지 관리

class Server():

    # 서버 초기화 및 종료 기능
    def __init__(self):
        # 연결 유형 정리
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 정의된 서버 및 포트에 대한 바인딩 연결
        self.server.bind(ADDR)

        # 연결된 사용자 목록 저장
        self.users = []

        # 서버 설정
        self.chat = True

        print("서버 초기화 중입니다.")

        # 새로운 연결 및 메세지를 수신하기 위해 서버를 연다.
        self.server.listen()

        print(f'Server is listening on {SERVER} port {PORT}')

        # 서버를 종료하기 위해 입력을 받는 스레드를 시작한다.
        # 예를 들어 서버를 연다.
        # 서버를 열고 클라이언트가 들어온다
        # 그런데 서버를 관리하는 사람이 자신이 원할 때
        # 서버를 종료할 수 있어야 한다. ( 엔터 입력시 종료 )
        exit = threading.Thread(target=self.closeServer, args=())
        exit.start()

        self.receiveUser()

    # 신규 유저 수신 및 새로운 연결 설정 함수
    def receiveUser(self):

        # 서버가 켜져있는 동안에 어떤 것이 발생할까?
        while self.chat:
            try:
                print('Server is opening')
                # 새로운 유저가 연결하고 소켓 정보를 저장하기를 기다린다.(받아들인다.)
                conn, addr = self.server.accept()
                print(addr[0])
                print(addr[1])

                # 유저 이름 얻기
                # 이름 길이 수신 및 디코딩
                username_length = int(conn.recv(HEADER).decode(FORMAT))
                print(username_length)
                # 수신 및 디코딩 이름
                username = conn.recv(username_length).decode(FORMAT)
                print(username)
                # 허용된 유저 인스턴스를 유저 목록에 추가
                u = User(self, username, conn, addr)  # 생성자에게 연결 데이터 보내기
                self.users.append(u)  # 연결된 유저 목록에 추가

                # 유저에게 업데이트된 사용자 목록 보내기
                self.userListUpdate()
                # 유저에게 들어오는 알림 보내기
                date_ = date()  # 날짜와 시간 얻기
                msg = f"{username}님이 채팅({date_})에 참여했습니다. 현재 활성화 된 연결 {len(self.users)}"
                self.serverMsg(msg)

            except:
                # 연결에 오류가 있으면 서버가 닫힙니다.
                print("Server is closing.")
                self.server.close()
                self.chat = False  # 서버 닫음
                return  # 함수 종료를 의미한다. return 반환값은 없다.

    # 유저 연결 취소
    def cancleConnection(self, user):

        # 연결된 유저 목록에서 제거
        self.users.remove(user)

        # 유저 소켓 닫기
        user.conn.close()

        # 연결된 유저에 출력 통신
        date_ = date()
        msg = (f"{NEW_MESSAGE} {user.username}님이 채팅을 나갔습니다 ({date_}).현재 활성화 연결 {len(self.users)}.")
        self.serverMsg(msg)

        # 유저 목록 업데이트
        self.userListUpdate()

    # 서버 기능 메세지
    def serverMsg(self, msg):

        # 송신을 위해 이미 인코딩 된 수신 변수
        message, send_length = encodeMsg(msg)

        # 연결된 모든 유저에게 메시지 보내기
        for user in self.users:
            user.conn.send(send_length)
            user.conn.send(message)

            # 사용자 기능 메세지

    def userMsg(self, msg, user):

        # 날짜와 시간 얻기
        date_ = date()

        # 사용자와 발신자에 대한 메시지 형성
        msgAll = (f"{user.username} ({date_}): {msg}")
        msgSelf = (f"(나) ({date_}) : {msg}")

        # 사용자에게 보낼 새 메시지 tag 삽입
        msgAll = (f"{NEW_MESSAGE}{msgAll}")
        msgSelf = (f"{NEW_MESSAGE}{msgSelf}")

        # 전송을 위해 이미 인코딩된 수신 변수
        message, send_length = encodeMsg(msgAll)
        messageSelf, send_lengthSelf = encodeMsg(msgSelf)

        # 연결된 모든 유저들에게 전송
        for u in self.users:
            # 자기 자신이 아닌 경우 사용자 이름과 함께 메세지를 보낸다.
            if (u.conn != user.conn):
                u.conn.send(send_length)
                u.conn.send(message)

            # 자기 자신인 경우
            # 그러니까 메세지를 누군가 서버에 보내는데 자기 자신인 경우.
            else:
                u.conn.send(send_lengthSelf)
                u.conn.send(messageSelf)

    # 연결된 유저 목록을 유저에게 보내기
    def userListUpdate(self):

        # 연결된 모든 유저 기능
        for u in self.users:
            # 연결 목록 지우기
            message, send_length = encodeMsg(f"{CLEAR_LIST}")
            u.conn.send(send_length)
            u.conn.send(message)

            # 새로운 유저 목록 보내기
            for user in self.users:
                # 유저가 메세지를 올바르게 처리하도록 tag를 추가한다.
                # 유저가 보내는 사람 이름을 받으려는 경우 메세지 끝에 you를 추가한다.
                if (u.conn == user.conn):
                    message, send_length = encodeMsg(f"{NAME_LIST}{user.username} (you)")
                else:  # 그렇지 않은 경우 Tag와 이름을 보낸다.
                    message, send_length = encodeMsg(f"{NAME_LIST}{user.username}")
                u.conn.send(send_length)
                u.conn.send(message)

    # 서버 종료 함수
    def closeServer(self):

        # 프로그램을 종료하려면 서버 터미널에서 입력을 기다린다.
        input("서버를 종료하려면 엔터를 누르세요 :\n")

        # 수신 시 오프라인 변수, 소켓을 닫고 프로그램 종료
        self.chat = False
        self.server.close()


# 반환 날짜 및 시간 함수
def date():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    chat_time = (f"{now.year}/{now.month}/{now.day} - {current_time}")

    return chat_time

def dateonly():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    chat_time = (f"{now.year}/{now.month}/{now.day}")

    return chat_time


# 소켓을 통해 보낼 메시지를 인코딩 하는 함수
def encodeMsg(msg):
    # 메세지 텍스트를 UTF-8 형식으로 인코딩
    message = str(msg).encode(FORMAT)
    print(message)
    # print(message)
    # 인코딩 된 메세지의 길이 저장
    msg_length = len(message)
    # print(msg_length)
    # 메세지 길이를 UTF-8 형식으로 인코딩
    send_length = str(msg_length).encode(FORMAT)
    # print(send_length)
    # 정의된 HEADER 와 같을 때까지 공백으로 길이 메시지를 완성한다.
    # 반환 메시지 = send_length
    send_length += b' ' * (HEADER - len(send_length))
    # print(send_length)

    return message, send_length


# 사용자
# 유저들로부터 메시지 수신
# 요청을 처리하고 메인 클래스와 통신한다.

class User():

    # 서버에서 유저 인스턴스 초기화
    def __init__(self, server, username, conn, addr):

        # 통신을 수행할 서버에 대한 참조를 저장 한다.
        self.server = server
        print(self.server)
        # 유저로부터 정보 얻기
        self.username = username  # 사용자로부터 사용자 이름 얻기
        self.conn = conn  # 사용자에서 소켓 수신
        self.addr = addr


        # 메인 루프를 위해 유저를 온라인으로 설정
        self.userOnline = True

        # 유저로부터 메시지를 받을 쓰레드 생성
        thread = threading.Thread(target=self.process, args=())
        thread.start()

    # 사용자로부터 메세지를 받을 때 까지 기다린다.
    def process(self):
        date_ = dateonly()

        # 사용자가 온라인 상태일 때 사용자로부터 메시지를 받는다.
        while self.userOnline and self.server.chat:
            try:
                print(f'{self.username}이 응답중입니다.')
                # 읽을 메세지의 크기를 얻는다.
                # 수신 메세지 길이
                msg_length = self.conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)  # 값을 인트형 저장
                    # 메세지 수신 및 디코딩
                    msg = self.conn.recv(msg_length).decode(FORMAT)
                    print(msg[1:], 'coconut')
                    self.dbmsg = msg[1:]
                    dbinput = f"insert into newschema.chatting1(user_id, message, ip_address, port_number, time) values('{self.username}', '{self.dbmsg}', '{self.addr[0]}', '{self.addr[1]}', '{date_}')"
                    # idon = f"select * from newschema.chatting1"
                    cur.execute(dbinput)

                    # avg = cur.fetchall()
                    con.commit()

                    # 메세지 처리를 위한 함수 호출
                    self.handleMsg(msg)
            except:
                # 오류 또는 연결 실패가 있는 경우
                self.server.cancleConnection(self)
                self.userOnline = False
                return  # 반환값 없이 함수 종료

    # 수신 메세지 처리 함수
    def handleMsg(self, msg):

        # 메세지 변수 저장 (번호 분리)
        re = msg[0]  # 첫 번째 문자 저장
        msg_list = list(msg)  # 리스트로 변환
        msg_list.pop(0)  # 번호 삭제
        msg = "".join(msg_list)  # 문자열에 저장

        # 수행할 작업
        if (re == NEW_MESSAGE):  # 새로운 메세지 번호인 경우
            self.server.userMsg(msg, self)  # 연결된 사용자에게 보내기

        elif (re == DISCONNECT_MESSAGE):

            self.userOnline = False  # 유저 오프라인으로 설정
            self.server.cancleConnection()  # 서버에 연결 해제 요청

        elif (re == MEMBER_INVITE):
            print(f"{msg}님을 채팅방에 초대하고있습니다...")
            self.invite(msg)
            print(self.invite(msg))

    def invite(self, msg):
        a = win32api.MessageBox(0, f"{self.username}님이 {msg}님께 채팅방 초대를 하였습니다. 응답하시겠습니까?", "초대알림", 65)
        print(a, 'thsis a')
        if a == 2:
            pass
        elif a == 1:
            return a


if __name__ == "__main__":
    s = Server()
