import socket
import threading
from define import *

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
        self.username = username # 인스턴스 사용자 이름 설정
        self.win = win # 통신창 참조 저장
        self.online = True # 클라이언트를 온라인으로 설정

        # 사용자 이름을 서버로 보내기
        message, send_length = encodeMsg(self.username)
        self.client.send(send_length) # 메세지 크기
        self.client.send(message) # 메세지

        # 메세지를 받을 쓰레드 생성
        self.thread_recv = threading.Thread(target=self.recvMsg, args=())
        self.thread_recv.start()
    
    # 메세지 수신
    def recvMsg(self):

        while self.online: # 온라인 상태일 동안만
            try:
                # 서버에서 메세지 받기 위해 대기 중
                msg_length = self.client.recv(HEADER).decode(FORMAT) 
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.client.recv(msg_length).decode(FORMAT)
                    # 메세지 처리를 위한 함수 호출
                    self.handleMsg(msg)
            
            except: # 오류 또는 연결 실패가 있는 경우
                self.online = False
        
    # 메세지 처리
    def handleMsg(self, msg):

        # 메세지에서 태그 분리
        re = msg[0] # 첫 번째 문자 저장
        msg_list = list(msg) # 목록으로 변환
        msg_list.pop(0) # 태그 삭제
        msg = "".join(msg_list)  # 문자열에 저장

        # 수행할 작업 정의
        if (re == NEW_MESSAGE): # 새로운 메세지 TAG인 경우
            self.win.signal.chatLabel.emit(msg) # 메세지를 나타내기 위해 인터페이스에 신호 보내기

        elif (re == CLEAR_LIST): # 목록을 지우는 TAG인 경우
            self.win.signal.listUser.emit('') # 연결된 사용자 목록을 지우는 창에 빈 신호를 보낸다.
        
        elif (re == NAME_LIST): # 이름 목록인 경우
            self.win.signal.listUser.emit(msg) # 창에 이름 보내기, 연결된 사용자 목록에 추가

    # 메세지 전송
    def sendMsg(self, msg, re):

        if (self.online): # 사용자가 온라인 상태인 경우
            try:
                msg = re + msg # 메세지에 태그 추가
                message, send_length = encodeMsg(msg)
                self.client.send(send_length) 
                self.client.send(message)
            
            except: # 통신이 실패할 경우
                self.disconnect() # 연결 해제

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
            self.clinet.close()
            self.win.signal.chatLabel.emit("연결이 종료 되었습니다.")

# 소켓을 통해 보낼 메세지를 인코드 하는 함수
def encodeMsg(msg):
    message = str(msg).encode(FORMAT) # UTF-8 형식으로 인코드
    msg_length = len(message) # 인코딩된 메세지 크기 저장
    send_length = str(msg_length).encode(FORMAT)
    # 정의된 HEADER와 같을 때까지 공백으로 길이 메세지를 완성한다.
    send_length += b' ' * (HEADER - len(send_length))  

    return message, send_length