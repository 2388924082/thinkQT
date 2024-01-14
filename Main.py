import sys
from PyQt5.QtWidgets import QApplication
from windows.mainWindow_mdi.window_main import window_main
from libs import logger
from logging import info

# 主函数
if __name__ == "__main__":
    # 初始化日志
    logger.clean_old_log()
    logger.init_log()
    # 初始化主窗口
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 让MDI子窗口的关闭按钮好看
    mainWindow = window_main()
    mainWindow.show()
    info("mainWindow start")
    sys.exit(app.exec_())
