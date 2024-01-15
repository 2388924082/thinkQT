from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import (QPainter, QPen, QBrush, QFont, QImage, QPainterPath, QPixmap, QColor)
import numpy as np
from time import time


def timeis(func):
    debug = True
    # debug = False

    def wrapper(*args, **kwargs):
        if debug:
            start = time()
            result = func(*args, **kwargs)
            end = time()
            print(f"{func.__name__} run in {end - start} seconds")
        else:
            result = func(*args, **kwargs)
        return result

    return wrapper


#############################################################################
# nodes types:
# line(start_point,end_point,pen),
# circle(center_pos,radius,pen),
# rect(left_up_point,right_down_point,pen)
# img(Qpixmap,img_crop_rect(left_up_point,right_down_point),left_up_point,right_down_point)
#############################################################################
# 坐标系组件
class Qplotlib(QWidget):
    def __init__(self, parent=None, extent=None):
        super().__init__(parent)
        # self.resize(500, 500)
        self.w = self.width()
        self.h = self.height()
        # 坐标轴的坐标范围
        if extent is not None:
            self._extent = extent
        else:
            self._extent = [0, 100, 0, 100]
        # 逻辑长度转物理长度的比例
        self.x_ratio = None  # x轴的缩放比例
        self.y_ratio = None  # y轴的缩放比例
        # 坐标背景图裁剪前
        self._back_ground_img_old = None
        # 坐标背景图裁剪后
        self._back_ground_img_crop = None
        # 背景图裁剪区域
        self._bg_area_rect = None
        # 背景图总的坐标范围
        self._extent_img = [-128, 128, -128, 128]
        # XY轴是否保持比例相等
        self.is_axes_equal = True
        # 是否绘制坐标轴
        self.is_draw_axes = True
        # 坐标轴样式
        self.axes_style = {'color': 'grey', 'lineWidth': 1.2, 'lineStyle': '--', 'fontSize': 8}
        # 保存绘图时的对象
        self.node_list = []
        self.circle_list = []
        self.line_list = []
        self.rect_list = []
        self.img_list = []
        self.text_list = []
        # self.back_function = {'button_press_event': self.on_press,
        #                       'motion_notify_event': self.on_move,
        #                       'button_release_event': self.on_release,
        #                       'pick_event': self.on_pick,
        #                       'key_press_event': self.on_key_press,
        #                       'key_release_event': self.on_key_release,
        #                       'double_click_event': self.on_double_click}
        # 记录当前笔的样式style
        self.brush = QBrush(QColor('#ff2200'), Qt.SolidPattern)
        self.painter = None
        self.pen = QPen(Qt.black, 1, Qt.SolidLine)
        self.textFont = QFont('Arial', 10)
        # 将 QFont 对象应用到当前控件上
        # 注意：setFont应用后，会触发paintEvent，请不要在paintEvent里使用，会陷入死循环
        self.setFont(self.textFont)

    # 快速初始化
    def _imshow(self, img, extent=None, extent_img=None, area_rect=None):
        self._set_extent(extent)
        self._set_back_ground(img, extent_img, area_rect)

    # 设置逻辑坐标系XY的范围
    def _set_extent(self, extent):
        self._extent = extent

    # 设置背景,输入的是图片路径或者numpy矩阵，图片的xy坐标范围，裁剪的区域
    # 如果area_rect为空,则不裁剪
    # 如果extent_img为空,extent_img为空
    def _set_back_ground(self, img, extent_img=None, area_rect=None):
        # 如果extent_img为空,则用self._extent的值
        if extent_img is None:
            extent_img = self._extent_img
        pixmap = self.img2pixmap(img)
        self._extent_img = extent_img
        self._back_ground_img_old = pixmap
        self._back_ground_img_crop = pixmap
        if area_rect is not None:
            x0, y0, x1, y1 = area_rect
            self._back_ground_img_crop = self._extent_to_crop_area(pixmap, extent_img, [x0, x1, y0, y1])

    # 清空画布
    def cla(self):
        self.node_list = []

    # 重新刷新绘图
    def _show(self):
        self.repaint()

    # ######################################开始绘制当前组件########################################
    # 绘制背景图（将背景图缩放到窗口大小）
    def draw_back_ground(self, painter):
        W, H = self.width(), self.height()
        point = QPoint(0, 0)
        back_ground_img_crop = self._back_ground_img_crop.scaled(W, H)
        painter.drawPixmap(point, back_ground_img_crop)

    # 绘制坐标轴
    def drawAxes(self, painter):
        x0, x1, y0, y1 = self._extent
        xo, yo = self._L2w(0, 0)
        x0, y0 = self._L2w(x0, y0)
        x1, y1 = self._L2w(x1, y1)
        self._node2pen(self.axes_style)
        self._node2font(self.axes_style)
        painter.drawLine(xo, y0, xo, y1)
        painter.drawLine(x0, yo, x1, yo)
        painter.drawText(x0, yo, str(int(self._extent[0])))
        painter.drawText(x1 - 40, yo, str(int(self._extent[1])))  # 文字在可视区域外了，往前挪40个像素
        painter.drawText(xo, y0, str(int(self._extent[2])))
        painter.drawText(xo, y1 + 20, str(int(self._extent[3])))  # 物理坐标，往下挪20像素

    # 重写绘图事件
    def paintEvent(self, event):
        if self.painter is None:
            self.painter = QPainter()
        painter = self.painter
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 开启抗锯齿功能
        self._draw(painter)
        painter.end()

    # 绘制坐标与所有节点node_list
    # _draw()绘制过程中不能调用外部的绘图函数，这会向node_list添加元素，从而造成明显的卡顿闪烁现象
    @timeis
    def _draw(self, painter):
        # 绘制坐标
        # 1.数据准备
        W = self.w = self.width()
        H = self.h = self.height()
        x0, x1, y0, y1 = self._extent
        self.x_ratio, self.y_ratio = W / (x1 - x0), H / (y0 - y1)  # 逻辑长度转物理长度的比例
        # 绘制边框
        rect = QRect(0, 0, W, H)
        painter.drawRect(rect)
        # 绘制背景图
        if self._back_ground_img_crop is not None:
            self.draw_back_ground(painter)
        # 按入栈的顺序，绘制所有类型节点
        for node in self.node_list:
            if node['status'] == 1:
                if node['type'] == 'line':
                    self._showLine(node, painter)
                elif node['type'] == 'circle':
                    self._showCircle(node, painter)
                elif node['type'] == 'rect':
                    self._showRect(node, painter)
                elif node['type'] == 'pixmap':
                    self._showPixmap(node, painter)
                elif node['type'] == 'path':
                    self._showPath(node, painter)
                elif node['type'] == 'XY':
                    self._showPlot(node, painter)
                elif node['type'] == 'text':
                    self._showText(node, painter)
                    pass
        # 绘制坐标轴
        if self.is_draw_axes:
            self.drawAxes(painter)

    # 逻辑坐标X,Y转物理坐标W,H（为实际在物理坐标系画图做准备）
    def _L2w(self, X=None, Y=None):
        if X is not None and Y is None:
            if isinstance(X, QPoint):
                x, y = X.x(), X.y()
            elif isinstance(X, list):
                x, y = X[0], X[1]
        else:
            x, y = X, Y
        x0, x1, y0, y1 = self._extent
        W, H = self.w, self.h
        Wx = W / (x1 - x0) * (x - x0)
        Hy = H / (y0 - y1) * (y - y1)
        return Wx, Hy

    # 物理坐标W,H转逻辑坐标X,Y（从物理坐标系读取逻辑坐标值）
    def _w2L(self, Wx=None, Hy=None):
        if Wx is not None and Hy is None:
            if isinstance(Wx, QPoint):
                Wx, Hy = Wx.x(), Wx.y()
            elif isinstance(Wx, list):
                Wx, Hy = Wx[0], Wx[1]
        else:
            Wx, Hy = Wx, Hy
        x0, x1, y0, y1 = self._extent
        W, H = self.w, self.h
        x = (Wx / W) * (x1 - x0) + x0
        y = (Hy / H) * (y0 - y1) + y1
        return x, y

    # 逻辑长度X坐标转物理长度W（为实际在物理坐标系画图做准备）
    def _x2w(self, x_length):
        x0, x1, y0, y1 = self._extent
        x_range = x1 - x0
        W = self.width()
        Wx = W / x_range * x_length
        return Wx

    # 逻辑长度Y转物理长度H（为实际在物理坐标系画图做准备）
    def _y2h(self, y_length):
        x0, x1, y0, y1 = self._extent
        y_range = y1 - y0
        H = self.height()
        Hy = H / y_range * y_length
        return Hy

    # 逻辑长度x/y转物理长度W,H
    def xy2w(self, xy):
        x, y = xy
        return self._x2w(x), self._y2h(y)

    # 外部调用方法：画线
    def drawLine(self, start_point, end_point, color='black', lineWidth=1, lineStyle='-'):
        line = {'type': 'line', 'status': 1, 'start_point': start_point, 'end_point': end_point, 'color': color,
                'lineWidth': lineWidth, 'lineStyle': lineStyle}
        self.node_list.append(line)
        self.line_list.append(line)

    # 内部方法：paintEvent发生时绘制node_list中的线
    def _showLine(self, line, painter):
        # 根据node对象设置样式
        self._node2pen(line)
        # 逻辑坐标转成物理坐标
        x0, y0 = line['start_point']
        x1, y1 = line['end_point']
        p1 = self._L2w(x0, y0)
        p2 = self._L2w(x1, y1)
        # 开始绘制node对象
        painter.drawLine(p1[0], p1[1], p2[0], p2[1])

    # 从node节点获取信息来配置pen的样式
    def _node2pen(self, node):
        if self.pen is None:
            self.pen = QPen()
        # 设置线宽
        if 'lineWidth' in node.keys() and node['lineWidth'] is not None:
            self.pen.setWidthF(node['lineWidth'])  # 设置线宽，也就是画笔的粗细
        # 设置颜色
        if 'color' in node.keys() and node['color'] is not None:
            # 列表RGB颜色
            if isinstance(node['color'], list):
                R, G, B = node['color']
                self.pen.setColor(QColor(R, G, B))  # 设置颜色
            # 字符串颜色
            elif isinstance(node['color'], str):
                color = {'black': QColor(0, 0, 0),
                         'grey': QColor(128, 128, 128),
                         'white': QColor(255, 255, 255),
                         'red': QColor(255, 0, 0),
                         'green': QColor(0, 255, 0),
                         'blue': QColor(0, 0, 255)}
                if node['color'] in color.keys():
                    self.pen.setColor(color[node['color']])
                else:
                    raise Exception(f'node2pen() , unknown color:{node["color"]}')
        # 设置线条样式
        if 'lineStyle' in node.keys() and node['lineStyle'] is not None:
            if node['lineStyle'] == '-':
                self.pen.setStyle(Qt.SolidLine)  # 设置实线
            elif node['lineStyle'] == '--':
                self.pen.setDashPattern([4, 3])  # 设置虚线模式，这里表示5个单位长度的线段和2个单位长度的空白交替出现
        self.pen.setCapStyle(Qt.RoundCap)  # 设置线端的样式为圆形
        self.pen.setJoinStyle(Qt.RoundJoin)  # 设置线的连接样式为圆形
        self.painter.setPen(self.pen)  # 应用画笔设置

    # 外部调用方法：画圆
    def drawCircle(self, center_point, radius, color=None, lineWidth=1, lineStyle='-'):
        # 获取初次的相对长度，窗口缩放后，相对长度才会进行等比例缩放
        if isinstance(radius, list):
            Rx = self._x2w(radius[0])
            Ry = self._y2h(radius[1])
            Rx = Rx / self.width()
            Ry = Ry / self.height()
            Rxy = [Rx, Ry]
        else:
            Rx = self._x2w(radius)
            Ry = self._y2h(radius)
            Rx = Rx / self.width()
            Ry = Ry / self.height()
            # R = min(Rx, Ry)
            Rxy = [Rx, Ry]
        circle = {'type': 'circle', 'status': 1, 'center_point': center_point, 'radius': radius, 'Rxy': Rxy,
                  'lineWidth': lineWidth,
                  'color': color,
                  'lineStyle': lineStyle}
        self.node_list.append(circle)
        self.circle_list.append(circle)

    # 内部方法：paintEvent发生时绘制node_list中的圆形
    def _showCircle(self, circle, painter):
        self._node2pen(circle)
        x, y = circle['center_point']
        x, y = self._L2w(x, y)
        # r = self.x_idx * circle['radius']  # 逻辑长度转物理长度
        Rx, Ry = circle['Rxy']
        Rx, Ry = self.width() * Rx, self.height() * Ry
        painter.drawEllipse(x - Rx, y - Ry, 2 * Rx, 2 * Ry)
        # painter.drawEllipse(x - r, y - r, 2 * r, 2 * r)
        pass

    # 将逻辑长度转换为比例长度
    def _length_ratio(self, deltaXY):
        # 获取初次的相对长度，窗口缩放后，相对长度才会进行等比例缩放
        if deltaXY is not None:
            deltaX = self._x2w(deltaXY[0])
            deltaY = self._y2h(deltaXY[1])
            deltaX = deltaX / self.width()
            deltaY = deltaY / self.height()
            deltaXY = [deltaX, deltaY]
        return deltaXY

    # 外部调用方法：画矩形
    def drawRect(self, center_point=None, deltaXY=None, start_point=None, end_point=None, color=None, lineWidth=1,
                 lineStyle='-'):
        # 获取初次的相对长度，窗口缩放后，相对长度才会进行等比例缩放
        if deltaXY is not None:
            deltaXY = self._length_ratio(deltaXY)
        rect = {'type': 'rect', 'status': 1, 'center_point': center_point, 'deltaXY': deltaXY,
                'start_point': start_point, 'end_point': end_point,
                'lineWidth': lineWidth,
                'color': color,
                'lineStyle': lineStyle}
        self.node_list.append(rect)
        self.rect_list.append(rect)

    # 内部方法：paintEvent发生时绘制node_list中的矩形
    def _showRect(self, node, painter):
        self._node2pen(node)
        if node['center_point'] is not None and node['deltaXY'] is not None:
            x, y = node['center_point']
            x, y = self._L2w(x, y)
            deltaXY = node['deltaXY']
            deltaXY = self.width() * deltaXY[0], self.height() * deltaXY[1]
            painter.drawRect(x - deltaXY[0], y - deltaXY[1], 2 * deltaXY[0], 2 * deltaXY[1])
        elif node['start_point'] is not None and node['end_point'] is not None:
            start_point = node['start_point']
            start_point = self._L2w(start_point[0], start_point[1])
            end_point = node['end_point']
            end_point = self._L2w(end_point[0], end_point[1])
            painter.drawRect(start_point[0], start_point[1], end_point[0] - start_point[0],
                             end_point[1] - start_point[1])

    # 将区域列表转成Qrect
    def _area2rect(self, area):
        if area is not None:
            x0, x1, y0, y1 = area
            rect = QRect(x0, y0, x1 - x0, y1 - y0)
            return rect

    # 外部调用方法：position是左上角起始点，deltaXY是宽和高,area是可选参数，用于指定要绘制的区域，它是一个矩形（左上角的点和宽度和高度的二元组）。如果未指定，将绘制整个pixmap。
    def drawPixmap(self, position, pixmap, deltaXY=None, area_rect=None, pen=None):
        pixmap = self.img2pixmap(pixmap)
        deltaXY = self._length_ratio(deltaXY) if deltaXY is not None else None
        area_rect = self._area2rect(area_rect) if area_rect is not None else None
        # deltaXY = self.xy2w(deltaXY) if deltaXY is not None else None
        pixmap = {'type': 'pixmap', 'status': 1, 'pixmap': pixmap, 'position': position, 'deltaXY': deltaXY,
                  'area_rect': area_rect,
                  'pen': pen}
        self.node_list.append(pixmap)

    # 内部方法：paintEvent发生时绘制node_list中的pixmap
    def _showPixmap(self, node, painter):
        pixmap = node['pixmap']
        x, y = node['position']
        area_rect = node['area_rect']
        x, y = self._L2w(x, y)
        point = QPoint(x, y)
        if node['deltaXY'] is not None:
            deltaXY = node['deltaXY']
            deltaXY = self.width() * deltaXY[0], self.height() * deltaXY[1]
            pixmap = pixmap.scaled(deltaXY[0], deltaXY[1])
        if area_rect is not None:
            painter.drawPixmap(point, pixmap, area_rect)
        else:
            painter.drawPixmap(point, pixmap)
        pass

    # 外部调用方法：
    def drawPath(self, points, pen=None):
        Path = {'type': 'path', 'status': 1, 'points': list(points), 'pen': pen}
        self.node_list.append(Path)

    # 内部方法：paintEvent发生时绘制node_list中的路径
    def _showPath(self, line, painter):
        pass

    # 外部调用方法：绘制文字
    def text(self, point, text, fontSize=0, color='black', area=None):
        Text = {'type': 'text', 'status': 1, 'text': text, 'point': list(point), 'area': area, 'fontSize': fontSize,
                'color': color}
        self.node_list.append(Text)
        self.text_list.append(Text)

    # 根据node设置字体
    def _node2font(self, node):
        # 创建 QFont 对象
        if self.textFont is None:
            self.textFont = QFont()
        # 设置字体名称
        self.textFont.setFamily("Arial")
        # 设置字体大小
        if 'fontSize' in node.keys() and node['fontSize'] is not None:
            self.textFont.setPointSize(node['fontSize'])
        # 设置字体粗细
        self.textFont.setBold(False)

    # 内部方法：paintEvent发生时绘制node_list中的文字
    def _showText(self, Text, painter):
        # self._node2pen(Text)
        self._node2font(Text)
        # x, y = Text['point']
        # x, y = self._L2w(x, y)
        # if Text['area'] is not None:
        #     w, h = Text['area']
        #     rect = QRect(x - w, y - h, 2 * w, 2 * h)
        #     painter.drawText(rect, Qt.AlignCenter, Text['text'])
        # else:
        #     painter.drawText(x, y, Text['text'])

    # 外部调用方法：绘制X,Y的线条
    def plot(self, X, Y, color=None, lineWidth=1, lineStyle='-'):
        XY = {'type': 'XY', 'status': 1, 'X': X, 'Y': Y,
              'lineWidth': lineWidth,
              'color': color,
              'lineStyle': lineStyle}
        self.node_list.append(XY)

    # 内部方法：paintEvent发生时绘制node_list中的XY的线条
    def _showPlot(self, line, painter):
        W = self.width()
        H = self.height()
        # 根据node对象设置样式
        self._node2pen(line)
        # 防呆判断
        if len(line['X']) == len(line['Y']):
            num = len(line['X'])
        else:
            print('showPlot() Eorr:X与Y长度不一致')
            exit()
        # 逻辑坐标转成物理坐标
        path = QPainterPath()
        x0, y0 = self._L2w(line['X'][0], line['Y'][0])
        path.moveTo(x0, y0)
        for i in range(num):
            x1 = line['X'][i]
            y1 = line['Y'][i]
            x1, y1 = self._L2w(x1, y1)
            path.lineTo(x1, y1)
        painter.drawPath(path)

    # ###########################################事件处理########################################
    # 窗口缩放事件
    def resizeEvent(self, event):
        # 保持比例不变
        if self.is_axes_equal:
            x0, x1, y0, y1 = self._extent
            x_range = x1 - x0
            y_range = y1 - y0
            win_ratio_old = y_range / x_range
            W = self.width()
            H = self.height()
            win_ratio_now = H / W
            if win_ratio_now >= win_ratio_old:
                H = W * win_ratio_old
            else:
                W = H / win_ratio_old
            self.resize(W, H)

    # pyqt5的鼠标按下事件
    def mousePressEvent(self, QMouseEvent):
        mouseEvent = self.processQMouseEvent(QMouseEvent)
        self.on_press(mouseEvent)

    # 外部调用方法：鼠标按下
    def on_press(self, QMouseEvent):
        print('on_press')
        pass

    # pyqt5的鼠标移动事件
    def mouseMoveEvent(self, QMouseEvent):
        mouseEvent = self.processQMouseEvent(QMouseEvent)
        self.on_move(mouseEvent)

    # 外部调用方法：鼠标移动
    def on_move(self, QMouseEvent):
        print('on_move')
        pass

    # pyqt5的鼠标移动事件
    def mouseReleaseEvent(self, QMouseEvent):
        mouseEvent = self.processQMouseEvent(QMouseEvent)
        self.on_release(mouseEvent)

    # 外部调用方法：鼠标释放
    def on_release(self, QMouseEvent):
        print('on_release')
        pass

    # 写一个pyqt的双击事件
    def mouseDoubleClickEvent(self, QMouseEvent):
        mouseEvent = self.processQMouseEvent(QMouseEvent)
        self.on_double_click(mouseEvent)

    # 外部调用方法：鼠标双击
    def on_double_click(self, QMouseEvent):
        print('on_double_click')

    # 写一个pyqt的按键事件
    def keyPressEvent(self, QKeyEvent):
        keyEvent = self.processQKeyEvent(QKeyEvent)
        self.on_key_press(keyEvent)

    # 外部调用方法：键盘按下
    def on_key_press(self, QKeyEvent):
        print('on_key_press')

    # 写一个pyqt的按键释放事件
    def keyReleaseEvent(self, QKeyEvent):
        keyEvent = self.processQKeyEvent(QKeyEvent)
        self.on_key_release(keyEvent)

    # 外部调用方法：键盘释放
    def on_key_release(self, QKeyEvent):
        pass

    # 外部调用方法：pick，每一种node元素设置一个inArea的方法，判断为True时触发on_pick事件
    def on_pick(self, QMouseEvent):
        print('pickEvent()', QMouseEvent)
        pass

    # #########################################事件处理函数 start######################################
    # 处理pyqt5的键盘按下事件
    def processQKeyEvent(self, QKeyEvent):
        keyEvent = {'key': QKeyEvent.key(), 'text': QKeyEvent.text(), 'isAutoRepeat': QKeyEvent.isAutoRepeat()}
        return keyEvent

    # 处理鼠标事件对象，返回回调函数的参数
    def processQMouseEvent(self, QMouseEvent):
        point = QMouseEvent.pos()
        xy = point.x(), point.y()
        xydata = self._w2L(point)
        xdata, ydata = xydata
        button = self.processButton(QMouseEvent.button())
        mouseEvent = {'button': button, 'xydata': xydata, 'xy': xy, 'xdata': xdata, 'ydata': ydata}
        return mouseEvent

    # 鼠标从pyqt5的124转换到matplotlib的132
    def processButton(self, QMouseEvent_button):
        if QMouseEvent_button == 0:  # 鼠标移动
            button = 0
        elif QMouseEvent_button == 1:  # 鼠标左键
            button = 1
        elif QMouseEvent_button == 4:  # 鼠标右键
            button = 2
        elif QMouseEvent_button == 2:  # 鼠标中键
            button = 3
        else:
            print('processButton() Eorr:不支持的鼠标按钮', QMouseEvent_button)
            exit('processButton() Eorr:不支持的鼠标按钮')
        return button

    # #########################################事件处理函数 end######################################
    # 独立util工具函数：Mat（numpy数组）转Qimg
    def Mat2Qimg(self, Mat):
        Mat = Mat.astype(np.uint8)
        if Mat.shape[-1] == 4:
            Qimg = QImage(Mat.data, Mat.shape[1], Mat.shape[0], Mat.shape[1] * 4, QImage.Format_RGBA8888)
        elif Mat.shape[-1] == 3:
            Qimg = QImage(Mat.data, Mat.shape[1], Mat.shape[0], Mat.shape[1] * 3, QImage.Format_RGB888)
        else:
            exit('图片的通道数不为3或4')
        return Qimg

    # 独立util工具函数：Qimg转Mat（numpy数组）
    def Qimg2Mat(self, Qimg):
        ptr = Qimg.constBits()
        ptr.setsize(Qimg.byteCount())
        mat = np.array(ptr)
        mat = mat.reshape(Qimg.height(), Qimg.width(), 4)
        mat = mat[:, :, :3]
        mat = mat[:, :, ::-1]
        mat = np.round(mat, 2)
        return mat

    # 工具函数：将接收到的所有格式图像转换成Qpixmap格式
    def img2pixmap(self, img):
        if isinstance(img, np.ndarray):
            Qimg = self.Mat2Qimg(img)
            pixmap = QPixmap.fromImage(Qimg)
        elif isinstance(img, str):
            pixmap = QPixmap(img)
        elif isinstance(img, QImage):
            pixmap = QPixmap.fromImage(img)
        elif isinstance(img, QPixmap):
            pixmap = img
        else:
            raise TypeError
        return pixmap

    # 独立util工具函数：裁剪pixmap
    # 根据图像exent_img坐标范围，裁剪pixmap的坐标区域area
    def _extent_to_crop_area(self, pixmap, extent_img, area_rect):
        h, w = pixmap.width(), pixmap.height()
        # 根据坐标周范围，计算图片裁剪的坐标区域area
        X0, X1, Y0, Y1 = extent_img
        X_range = X1 - X0
        Y_range = Y1 - Y0
        x0, y0, x1, y1 = area_rect
        # 根据逻辑坐标计算所在的比例坐标
        x0_ratio, y0_ratio, x1_ratio, y1_ratio = (x0 - X0) / X_range, (Y1 - y1) / Y_range, (x1 - X0) / X_range, (
                Y1 - y0) / Y_range
        # 图像裁剪的区域 点+宽、高
        area = QRect(int(x0_ratio * w), int(y0_ratio * h), int(x1_ratio * w) - int(x0_ratio * w),
                     int(y1_ratio * h) - int(y0_ratio * h))
        return pixmap.copy(area)


if __name__ == "__main__":  ##用于当前窗体测试
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

    img = plt.imread('./Qlab/lab_img.png') * 255
    app = QApplication(sys.argv)  # 创建GUI应用程序
    x = np.arange(-10, 21, 0.5)
    y = 2 * np.sin(x)
    pixmap = QPixmap('./Qlab/lab_img.png')
    w = QWidget()
    w.resize(800, 800)
    axes = Qplotlib()  # 创建坐标
    layout = QVBoxLayout()
    layout.addWidget(axes)
    w.setLayout(layout)
    axes._set_extent([-64, 128, -64, 128])
    # axes.set_back_ground('TL83_300.png',extent_old=[-128, 128, -128, 128], area_rect=[-20,20, -20,20])
    # axes.set_back_ground('TL83_300.png', extent_old=[-128, 128, -128, 128], area_rect=[-128, 128, -128, 128])
    axes._set_back_ground(img, area_rect=[-64, 128, -64, 128])
    # axes.set_back_ground('TL83_300.png')
    # axes.drawPixmap([0, 0], pixmap)

    axes.drawLine((0, 20), (20, 0))
    axes.plot(x, y)
    axes.text([0, 0], 'O', color=[255, 0, 0])
    axes.drawCircle([-32, -32], 32)
    axes.drawRect([-32, -32], [32, 32])
    axes.drawPixmap([64, 128], pixmap, deltaXY=[128, 128], area_rect=[0, 256, 0, 256])
    # axes.drawPixmap([0, 128], pixmap, deltaXY=[128, 128])

    w.show()
    sys.exit(app.exec_())
