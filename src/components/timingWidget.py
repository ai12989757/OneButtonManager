import random
try:
    from PySide2.QtWidgets import QApplication, QVBoxLayout, QWidget, QLCDNumber, QMenu, QAction
    from PySide2.QtCore import QTimer, QTime, Qt
    from PySide2.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
except ImportError:
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLCDNumber, QMenu, QAction
    from PySide6.QtCore import QTimer, QTime, Qt
    from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
    
def random_rainbow_color():
    """生成随机彩虹颜色，避免过暗的颜色"""
    hue = random.randint(0, 360)
    saturation = 150  # 保持较高的饱和度
    value = random.randint(200, 255)  # 保持较高的亮度
    return QColor.fromHsv(hue, saturation, value)

class TimerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border: none; }")
        # self.setWindowTitle("计时器组件")
        # self.setGeometry(0, 0, 245, 42)

        # 创建 QLCDNumber 显示时间
        self.lcd = QLCDNumber(self)
        self.lcd.setDigitCount(12)  # 设置显示位数为12位，格式为 hh:mm:ss.zzz
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.mousePressEvent = self.handle_mouse_press  # 绑定点击事件

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        # 初始化计时器时间
        self.time = QTime(0, 0, 0, 0)

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # 移除布局的间距
        
        self.setLayout(layout)

        # 初始化时间显示
        self.update_time()

        # 计次菜单项列表
        self.lap_times = []

    def update_time(self):
        # 增加1毫秒
        self.time = self.time.addMSecs(1)
        # 格式化时间字符串
        time_text = self.time.toString('hh:mm:ss.zzz')
        # 更新 QLCDNumber 显示
        self.lcd.display(time_text)

    def handle_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_timer()

    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            # 记录当前时间作为计次
            self.lap_times.append(self.time.toString('hh:mm:ss.zzz'))
        else:
            self.timer.start(1)  # 每1毫秒更新一次

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        
        # 添加所有计次菜单项
        for index, lap_time in enumerate(self.lap_times, start=1):
            lap_action = QAction(f"{lap_time}", self)
            # 创建数字图标
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(random_rainbow_color())
            font = QFont()
            font.setBold(True)
            font.setPointSize(18)  # 设置字体大小
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, str(index))
            painter.end()
            lap_action.setIcon(QIcon(pixmap))
            context_menu.addAction(lap_action)

        # 添加重置菜单项
        reset_action = QAction("重置", self)
        reset_action.triggered.connect(self.reset_timer)
        context_menu.addAction(reset_action)
        # 删除
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.deleteLater())
        context_menu.addAction(delete_action)

        context_menu.exec_(event.globalPos())

    def reset_timer(self):
        self.timer.stop()
        self.time = QTime(0, 0, 0, 0)
        self.update_time()
        self.lap_times.clear()  # 清除所有计次

if __name__ == "__main__":

    timer = TimerWidget()
    timer.show()
