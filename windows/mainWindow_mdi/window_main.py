from logging import info
from common.common import bind
from PyQt5.QtWidgets import QMainWindow
# (可选)作为一个窗口组件，需要对外发射信号
from PyQt5.QtCore import pyqtSignal

# 在controller导入view与model
if __name__ == "__main__":
    from ui_mainWindow import Ui_MainWindow
    from model_mainWindow import model_mainWindow
else:
    from .ui_mainWindow import Ui_MainWindow
    from .model_mainWindow import model_mainWindow

# 导入子窗口
from windows.subwindow1.window_tool import window_tool


class window_main(QMainWindow):
    # 4.发射信号
    view_signal = pyqtSignal(str)

    # 2.变量绑定(手动)
    v_lineEdit_num = bind("lineEdit_num", "text")
    v_label_num = bind("label_num", "text")
    v_silider_num = bind("slider_num", "value")

    def __init__(self, parent=None):
        # 父类初始化
        super().__init__(parent)
        # 1.UI初始化
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.mdiArea.setStyleSheet("QTabBar::tab { height: 30px;}")
        self.model = model_mainWindow()  # 绑定业务逻辑model

        # 2.变量绑定

        # 3.事件绑定
        self.ui.action1.triggered.connect(self.model.update_data)
        self.ui.action1.triggered.connect(self.action1)
        self.ui.action2.triggered.connect(self.action1)
        self.ui.action3.triggered.connect(self.action1)
        info("window_main初始化完毕")

    # UI逻辑在事件函数里写(JS部分)
    # 简单的业务逻辑也可以在controller里写，复杂的业务逻辑还是在model对象里面写
    # 事件函数1~n个
    def update_data(self):
        print('我是controller的clicked事件')

    def action1(self):
        print('我是controller的action1事件')
        info("window_main的action1事件")
        self.subwindow1 = window_tool()
        self.ui.mdiArea.addSubWindow(self.subwindow1)
        self.subwindow1.show()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # MDI子窗口的关闭按钮好看
    view = window_main()
    view.show()
    sys.exit(app.exec_())
