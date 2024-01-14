pyqt5的UI框架thinkQT

1.components 放置自定义的控件（使用paint绘制的组件） 
2.windows 放置用QtDesigner画的窗口(主窗口/子窗口) 
3.libs 存放一些业务逻辑会用到的公共库 
4.common 存放共用函数 
5.config 放置每个窗口的状态对象，用pickle持久化对象 
6.resource 放置资源文件 
7.log 放置日志文件 
8.Main.py 主窗口入口文件 
9.resource_rc.py 资源文件

Main文件：1.初始化参数2.加载主窗口MainWindow 
MainWindow文件：1.绘制主窗口2.加载子窗口subWindow 
subWindow文件：1.绘制子窗口2.加载控件与自定义控件components 
components文件：自定义子控件(使用paint绘制封装的控件)
