from login import Log
from chat import *
def start():

    name, addr, port = Log()

    if (name and addr and port):
        app = QApplication(sys.argv)
        win = MainWindow(name, addr, port)

        win.show()
        app.exec_()

if __name__ == "__main__":
    
    start()