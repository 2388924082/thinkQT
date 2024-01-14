from logging import info
from common.common import bind
from PyQt5.QtWidgets import QMainWindow
# (可选)作为一个窗口组件，需要对外发射信号
from PyQt5.QtCore import pyqtSignal

# 在controller导入view与model
if __name__ == "__main__":
    from ui_tool import Ui_MainWindow
    from model_tool import model_tool
else:
    from .ui_tool import Ui_MainWindow
    from .model_tool import model_tool


class window_tool(QMainWindow):
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
        self.model = model_tool()  # 绑定业务逻辑model

        # 2.变量绑定

        # 3.事件绑定
        self.ui.Button_reset.clicked.connect(self.model.update_data)  # 按钮事件绑定，可以绑定model里的方法
        self.ui.Button_reset.clicked.connect(self.update_data)  # 按钮事件绑定
        self.ui.slider_num.valueChanged.connect(self.slider_vchanged)  # 滑块事件绑定
        self.ui.lineEdit_num.textChanged.connect(self.lineEdit_num_changed)  # 文本框事件绑定

    # UI逻辑在事件函数里写(JS部分)
    # 简单的业务逻辑也可以在controller里写，复杂的业务逻辑还是在model对象里面写
    # 事件函数1~n个
    def update_data(self):
        print('我是controller的clicked事件')

    def lineEdit_num_changed(self, value):
        self.v_silider_num = value

    def slider_vchanged(self, value):
        info(f"slider_vchanged:{value}")
        self.v_label_num = value
        self.v_lineEdit_num = value


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    view = window_tool()
    view.show()
    sys.exit(app.exec_())
