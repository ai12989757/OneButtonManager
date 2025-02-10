try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class WidgetBG(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(WidgetBG, self).__init__(parent)
        self.color = kwargs.get("color", (0, 0, 0)) # rgb(0, 0, 0)
        self.iconPath = kwargs.get("iconPath", None)
        self.size = kwargs.get("size", 0)
        self.WIDTH = self.size
        self.HEIGHT = self.size
        self.round = int(self.size/2)

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

    def paintEvent(self, event):
        # 设置圆角
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.WIDTH, self.HEIGHT, self.round, self.round) # 设置圆角路径

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

if __name__ == "__main__":
    try:
        widgetssss.close()
    except:
        pass
    widgetssss = WidgetBG(iconPath="D:/MELcopy/OneTools/icons/Loop.png", size=42, color=(205, 92, 92))
    widgetssss.initUI()
    widgetssss.show()