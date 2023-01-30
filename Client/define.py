import socket

# 소켓 정의
HEADER = 64 # 기본 메세지 크기 (바이트)
FORMAT = "utf-8" # 인코딩 형식

SERVER = socket.gethostbyname(socket.gethostname()) # IP 주소 (로컬)
PORT = 5050 # 통신용 포트
ADDR = (SERVER, PORT)

# 시스템 통신용 번호
NEW_MESSAGE = '0'
NAME_LIST = '1'
CLEAR_LIST = '2'
DISCONNECT_MESSAGE = '3'
SAVE_LIST = '4'