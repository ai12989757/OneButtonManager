try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import os
try:
    ICONPATH = os.path.dirname(__file__).replace('\\', '/').replace('src/widgets', 'icons/') # /OneButtonManager/icons/
except:
    ICONPATH = 'D:/git/OneTools/icons/'
class WidgetBG(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(WidgetBG, self).__init__(parent)
        self.color = kwargs.get("color", (0, 0, 0)) # rgb(0, 0, 0) # 背景颜色
        self.iconPath = kwargs.get("iconPath", None)               # 图标路径
        self.size = kwargs.get("size", 0)                          # 图标大小
        self.WIDTH = self.size                                     # 窗口宽度
        self.HEIGHT = self.size                                    # 窗口高度
        self.round = int(self.size/2)                              # 圆角大小
        self.menuSub = kwargs.get("menuSub", False)                # 是否有子菜单角标
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)                           # 设置窗口背景透明
        self.pixmap = QPixmap(self.iconPath)
        self.pixmap = self.pixmap.scaledToHeight(self.size, Qt.SmoothTransformation)
        
        self.WIDTH = self.pixmap.width()
        self.HEIGHT = self.pixmap.height()
        if self.WIDTH != self.HEIGHT:
            self.round = int(self.size/4)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

    # def setSub(self):
    #     if self.menuSub:
    #         subImage = QImage(ICONPATH + 'sub/subR.png')
    #         newColor = QColor(self.color[0], self.color[1], self.color[2])
    #         for y in range(subImage.height()):
    #             for x in range(subImage.width()):
    #                 imageColor = subImage.pixelColor(x, y)
    #                 alpha = imageColor.alpha()
    #                 if alpha > 0:
    #                     subImage.setPixelColor(x, y, newColor)

    #         self.menuSubLable = QLabel(self)
    #         subImage = QPixmap.fromImage(subImage)
    #         subImage = subImage.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #         self.menuSubLable.setPixmap(subImage)
    #         self.menuSubLable.setGeometry(0, 0, self.size, self.size)
    #         self.menuSubLable.show()
    #     else:
    #         if hasattr(self, "menuSubLable"):
    #             self.menuSubLable.hide()

    def paintEvent(self, event):
        # 设置圆角
        path = QPainterPath()
        path.moveTo(0, 0)  # 左上角
        path.lineTo(self.WIDTH - self.round, 0)  # 右上角
        path.arcTo(self.WIDTH - self.round*2, 0, self.round*2, self.round*2, 90, -90)  # 右上角圆角
        path.lineTo(self.WIDTH, self.HEIGHT)  # 右下角
        if self.menuSub:
            path.arcTo(self.WIDTH - self.round/2, self.HEIGHT - self.round/2, self.round/2, self.round/2, 0, -90)  # 右下角圆角
        else:
            path.arcTo(self.WIDTH - self.round*2, self.HEIGHT - self.round*2, self.round*2, self.round*2, 0, -90)  # 右下角圆角
        path.lineTo(self.round, self.HEIGHT)  # 左下角
        path.arcTo(0, self.HEIGHT - self.round*2, self.round*2, self.round*2, 270, -90)  # 左下角圆角
        path.lineTo(0, self.round)  # 左上角
        path.arcTo(0, 0, self.round*2, self.round*2, 180, -90)  # 左上角圆角

        # 创建一个 QPainter 对象来绘制渐变
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # 抗锯齿

        # 绘制渐变背景
        gradient = QLinearGradient(0, 0, self.WIDTH, self.HEIGHT)
        lightColor = QColor(self.color[0], self.color[1], self.color[2]) # 亮色
        darkColor = QColor(self.color[0] - 100 if self.color[0] - 100 >= 0 else 0, 
                        self.color[1] - 100 if self.color[1] - 100 >= 0 else 0, 
                        self.color[2] - 100 if self.color[2] - 100 >= 0 else 0) # 暗色
        gradient.setColorAt(0.0, lightColor)  # 左上角亮
        gradient.setColorAt(1.0, darkColor)  # 右下角暗

        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(path)

        # # 绘制边框
        # borderPath = QPainterPath()
        # borderPath.addRoundedRect(1, 1, self.WIDTH - 2, self.HEIGHT - 2, self.round - 1, self.round - 1) # 设置圆角路径
        # borderGradient = QLinearGradient(0, 0, self.WIDTH, self.HEIGHT)
        # borderGradient.setColorAt(0.0, darkColor)  # 左上角暗
        # borderGradient.setColorAt(1.0, lightColor)  # 右下角亮
        # pen = QPen(QBrush(borderGradient), 1)  # 设置边框渐变颜色和宽度
        # painter.setPen(pen)
        # painter.drawPath(borderPath)

        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(path)

        # 绘制右下角小圆点
        if self.menuSub:
            dot_radius = 3
            painter.setBrush(lightColor)
            painter.drawEllipse(self.WIDTH - dot_radius * 2 -2 , self.HEIGHT - dot_radius * 2 - 2, dot_radius * 2, dot_radius * 2)


if __name__ == "__main__":
    try:
        widgetssss.close()
    except:
        pass
    widgetssss = WidgetBG(iconPath="D:/MELcopy/OneTools/icons/Loop.png", size=42, color=(147, 112, 219),menuSub=True)
    widgetssss.initUI()
    widgetssss.show()