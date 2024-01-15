from time import time
import numpy as np
from libs import colorSwitch
from components.Qplotlib import Qplotlib


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


# lab组件:基于matplotlib的pyqt5组件(matplotWidget)
class Qlab(Qplotlib):
    def __init__(self, parent=None):
        super(Qlab, self).__init__(parent)
        self.resize(500, 500)
        print('Qlab Size:', self.size())
        # 默认绘图设置：LAB背景图的3个轴（l\a\b）的范围
        self.l = 75
        self.arange = [-128, 128, 1]
        self.brange = [128, -128, -1]
        # 默认绘图设置：获取LAB的背景图
        self.back_ground_img_old = colorSwitch.range_to_lab_img(self.l, self.arange, self.brange)
        # 画出坐标轴
        # 默认绘图设置：设置坐标轴范围
        self.extent = [-128, 128, -128, 128]
        # 背景图的坐标范围
        self.extent_img = [-128, 128, -128, 128]
        # 显示的背景图区域
        self.area_rect = None
        # 是否绘制坐标轴
        self.is_draw_axes = True
        # XY坐标轴是否保持比例
        self.is_axes_equal = True
        # ############## 私有全局变量 start ################
        # 记录鼠标是否处于移动状态
        self.moved = 0
        # 记录鼠标当前是否按下'press'or 'release'
        self.mouse_status = None
        # 显示的点的数量
        self.num_show = 18
        # 记录按下的圆圈序号
        self.press_circle_i = -1
        # ############## 私有全局变量 end ################

        # ############## 公开全局变量 start################
        # 默认24色块大小
        self.dx = 1.5
        self.dy = 1.5
        self.radius = 2
        self.lineWidth = 1.3
        # 24色卡的lab标准值
        self.labList_standard = colorSwitch.labList_standard.copy()
        # 24色卡的经过CCM后的值
        self.labList_CCM = colorSwitch.labList_standard.copy()
        # 24色卡的目标target值
        self.labList_target = self.labList_CCM.copy()
        # 色块数量
        self.num = len(self.labList_CCM)
        # 24色卡的目标target值的显示与隐藏状态(0隐藏不绘制，1显示要绘制)
        self.labList_target_show = [0, ] * self.num
        # ############## 开放全局变量 end ################

        # ############## 初始化图像 start ################
        # 根据数据绘制图像
        self.draw()
        # ############## 初始化图像 end ################

    # 外部函数：设置化坐标轴
    def set_extent(self, extent):
        self.extent = extent
        self._set_extent(self.extent)
        self.draw()

    # 外部函数：初始化背景
    def set_back_ground(self, img, extent_img=None, area_rect=None):
        if extent_img is None:
            extent_img = self.extent_img
        else:
            self.extent_img = extent_img
        self.back_ground_img_old = img
        self.area_rect = area_rect
        # 画背景图
        self._set_back_ground(self.back_ground_img_old, extent_img=extent_img, area_rect=area_rect)
        self._show()

    # 显示图像
    def imshow(self, img, extent, extent_img=None, area_rect=None):
        self._set_extent(extent)
        # 画背景图
        self._set_back_ground(img, extent_img=extent_img, area_rect=area_rect)

    # 根据数据绘制图形
    @timeis
    def draw(self):
        # 清除前一帧图画
        self.cla()
        # 绘制标准点（矩形）
        a = self.labList_standard[:18, 1]
        b = self.labList_standard[:18, 2]
        self.plotList(a, b, '#', lineWidth=self.lineWidth, num=True)
        # 绘制CCM后的点（圆形）
        a1 = self.labList_CCM[:18, 1]
        b1 = self.labList_CCM[:18, 2]
        self.plotList(a1, b1, 'o', color='grey', lineWidth=self.lineWidth)
        # 绘制labList_target_status等于1的目标点（圆形、虚线）
        a2 = self.labList_target[:18, 1]
        b2 = self.labList_target[:18, 2]
        self.plotList(a2, b2, 'o', color='grey', lineStyle='--', lineWidth=self.lineWidth,
                      status=self.labList_target_show)
        # 绘制连线
        self.plotLines((a, b), (a1, b1), color='black', lineStyle='--', lineWidth=self.lineWidth,
                       status=self.labList_target_show)
        self.plotLines((a, b), (a2, b2), color='blue', lineStyle='--', lineWidth=self.lineWidth,
                       status=self.labList_target_show)

        # 其他状态绘制
        chromaList, CabList, EabList = self.calculate(self.labList_standard, self.labList_CCM)
        CabList = np.array(CabList)
        EabList = np.array(EabList)
        chroma = np.around(np.sum(np.array(chromaList)) / len(chromaList) * 100, 2)
        Cab = np.max(CabList)
        Eab = np.max(EabList)
        # print(CabList,EabList,EabList-CabList)
        self.text([20, 103], 'Chroma: ' + str(chroma) + '%', fontSize=10)
        self.text([33, 93], 'Cab: ' + str(Cab))
        self.text([33, 93], 'Cab: ' + str(Cab), fontSize=0)
        self.text([33, 83], 'Eab: ' + str(Eab))
        # # 将绘制的图形显示出来
        self.repaint()

    def on_press(self, event):
        a1 = self.labList_target[:18, 1]
        b1 = self.labList_target[:18, 2]
        num = len(a1)
        self.mouse_status = 'press'
        # print('按下事件', event)
        x, y = event['xdata'], event['ydata']  # 按下的坐标(x,y)
        # 检查是否在labList_target里面
        for i in np.arange(num):
            # print(f'目标点坐标{i,a1[i], b1[i]}')
            if self.inCircle([a1[i], b1[i]], [x, y], self.radius):
                # 左键按下,记录选中的target圆圈
                if event['button'] == 1:
                    self.press_circle_i = i
                    self.labList_target_show[i] = 1  # 状态设置为’显示‘状态
                    self.draw()
                # 右键按下,取消选中的target圆圈,坐标值重置为ccm的圆圈坐标
                elif event['button'] == 3:
                    # 目标点状态置为隐藏
                    self.labList_target_show[i] = 0
                    # 隐藏后的位置重置为CCM后的点的位置
                    self.labList_target[i] = self.labList_CCM[i]
                    # 取消选中状态，防止鼠标移动
                    self.press_circle_i = -1
                    # 重新绘制一帧
                    self.draw()
        self.draw()

        print(f'按下点的序号：{self.press_circle_i},坐标:{str(int(x))},{str(int(y))} ')

    def on_move(self, event):
        print('on_move')
        # 如果鼠标处于按下状态,且按到了target圆圈i上
        i = self.press_circle_i
        if self.mouse_status == 'press' and i != -1:
            # 记录移动状态
            self.moved = 1
            self.labList_target[:18, 1][i], self.labList_target[:18, 2][i] = event['xdata'], event['ydata']
            self.draw()

    def on_release(self, event):
        # 鼠标状态设置释放
        self.mouse_status = 'release'
        # 按下的target圆圈设置释放
        self.press_circle_i = -1
        # 移动状态设置为未移动
        self.moved = 0

    def on_double_click(self, event):
        # 目标点状态置为隐藏
        self.labList_target_show = [0 for i in self.labList_target_show]
        # 隐藏后的位置重置为CCM后的点的位置
        self.labList_target = self.labList_CCM.copy()  # list需要copy方法来创建一个新副本赋值，不然就会共用同一对象
        self.draw()

    # 根据中心点与距离中心点的距离，绘制矩形
    def rectPoint(self, x, y, dx=1.5, dy=1.5, text='', lineStyle='-', lineWidth=1.0, color='black'):
        self.drawRect([x, y], [dx, dy], lineStyle=lineStyle, lineWidth=lineWidth, color=color)
        self.text([x + 2, y + 2], text, color=[50, 50, 50], fontSize=6)  # 灰色的小字序号

    # 批量绘制矩形、圆形，可以选择线条样式、颜色
    def plotList(self, X, Y, point='#', lineStyle='-', lineWidth=1.0, num=False, color='black', status=None):
        if len(X) == len(Y):
            for i in range(len(X)):
                if status is None or status[i] == 1:
                    if point == '#':
                        if num is True:
                            self.rectPoint(X[i], Y[i], text=str(i + 1), dx=self.dx, dy=self.dy,
                                           lineStyle=lineStyle,
                                           lineWidth=lineWidth,
                                           color=color)
                        else:
                            self.rectPoint(X[i], Y[i], text='', dx=self.dx, dy=self.dy, lineStyle=lineStyle,
                                           color=color)
                    elif point == 'o':
                        self.drawCircle([X[i], Y[i]], self.radius, color=color, lineStyle=lineStyle,
                                        lineWidth=lineWidth)

    # 批量绘制线条
    def plotLines(self, P1, P2, status=None, color='red', lineWidth=1.0, lineStyle='-'):
        X1, Y1 = P1
        X2, Y2 = P2
        for i in range(len(X1)):
            if status is None or status[i] == 1:
                # self.plot([X1[i], X2[i]], [Y1[i], Y2[i]], color=color, linewidth=0.8, lineStyle=lineStyle)
                self.plot([X1[i], X2[i]], [Y1[i], Y2[i]], color=color, lineWidth=lineWidth, lineStyle=lineStyle)

    def inCircle(self, p1, p0, r):
        x1, y1 = p1[0], p1[1]
        x0, y0 = p0[0], p0[1]
        if (x1 - x0) ** 2 + (y1 - y0) ** 2 > r ** 2:
            return False
        else:
            return True

    def calculate(self, LAB1, LAB2):
        chromaList = []
        CabList = []
        EabList = []
        L1, A1, B1 = LAB1[:, 0], LAB1[:, 1], LAB1[:, 2]
        L2, A2, B2 = LAB2[:, 0], LAB2[:, 1], LAB2[:, 2]
        for i in range(len(L1)):
            l1, a1, b1, l2, a2, b2 = L1[i], A1[i], B1[i], L2[i], A2[i], B2[i]
            if i < 18:
                chromaList.append(np.around(np.sqrt(a2 ** 2 + b2 ** 2) / np.sqrt(a1 ** 2 + b1 ** 2), 3))
            CabList.append(np.around(np.sqrt((a2 - a1) ** 2 + (b2 - b1) ** 2), 2))
            EabList.append(np.around(np.sqrt((l2 - l1) ** 2 + (a2 - a1) ** 2 + (b2 - b1) ** 2), 2))
        return chromaList, CabList, EabList

    def mat2str(self, mat):
        str_temp = str(mat).replace('],', '\n')
        str_temp = str_temp.replace('[', '')
        str_temp = str_temp.replace(']', '')
        return str_temp

    # ################################## API接口 start ##################################################
    def get_lab_standard(self):
        return self.labList_standard

    def set_lab_standard(self, labList_standard):
        self.labList_standard = labList_standard
        self.draw()

    def get_lab_ccm(self):
        return self.labList_CCM

    def set_lab_ccm(self, labList_CCM):
        self.labList_CCM = labList_CCM
        self.draw()

    def get_lab_target(self):
        return self.labList_standard

    def set_lab_target(self, labList_standard):
        self.labList_standard = labList_standard
        self.draw()

    def get_lab_target_show(self):
        return self.labList_target_show

    def set_lab_target_show(self, labList_target_show):
        self.labList_target_show = labList_target_show
        self.draw()
    # ################################## API接口 end ##################################################


if __name__ == "__main__":
    # 图像范围0-255
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    import matplotlib.pyplot as plt
    import sys

    img = plt.imread('lab_img.png') * 255
    arange = (-128, 128, 1)
    brange = (128, -128, -1)
    l = 75
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(800, 800)
    pltw = Qlab(w)
    layout = QVBoxLayout()
    layout.addWidget(pltw)
    w.setLayout(layout)
    # 设置区域范围
    lab_img = colorSwitch.range_to_lab_img(l, arange, brange)
    # area = [-128, 128, -128, 128]
    area = [-70, 80, -70, 110]
    pltw.set_extent(extent=area)
    pltw.set_back_ground(lab_img, area_rect=area)
    # pltw.set_back_ground(img, area_rect=area)
    w.show()
    sys.exit(app.exec_())
