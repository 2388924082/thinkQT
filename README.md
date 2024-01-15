thinkQT是基于pyqt5的框架，能更好的前后端分离，变量与控件属性实现双向绑定

1.components     放置自定义的控件（使用paint绘制的组件）    
2.windows        放置用QtDesigner画的窗口(主窗口/子窗口)    
3.models         放置业务逻辑文件model
4.libs           存放一些业务逻辑会用到的公共库   
5.common         存放共用函数    
6.config         放置每个窗口的状态对象，用pickle持久化对象    
7.resource       放置资源文件   
8.log            放置日志文件   
9.Main.py        主窗口入口文件   
10.resource_rc.py 资源文件   
  
Main文件：1.初始化参数2.加载主窗口MainWindow  
MainWindow文件：1.绘制主窗口2.加载子窗口subWindow  
subWindow文件：1.绘制子窗口2.加载控件与自定义控件components  
components文件：自定义子控件(使用paint绘制封装的控件) 
models文件： 前端窗口调用后端的model文件实现业务功能
