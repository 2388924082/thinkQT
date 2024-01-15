from PyQt5.QtCore import QObject, pyqtSignal
from logging import info


class model_mainWindow():
    def __init__(self):
        pass

    def update_data(self):
        print('我是models文件夹下的model对象里的update_data函数')
        info(('我是models文件夹下的model对象里的update_data函数'))
