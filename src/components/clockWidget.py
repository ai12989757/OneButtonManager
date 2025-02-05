try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from ..utils import dragWidgetOrder

class ComponentWidget(QWidget):
    def __init__(self):
        super().__init__()
        dragWidgetOrder.DragWidgetOrder(self)
        self.setStyleSheet("QFrame { border: none; }")
        # 创建 QLCDNumber 显示时间
        self.lcd = QLCDNumber(self)
        self.lcd.setDigitCount(8)
        self.lcd.setSegmentStyle(QLCDNumber.Flat) # 设置显示风格,加粗
        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新一次

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setLayout(layout)

        # 初始化时间显示
        self.update_time()

    def update_time(self):
        # 获取当前时间
        current_time = QTime.currentTime()
        # 格式化时间字符串
        time_text = current_time.toString('hh:mm:ss')
        # 更新 QLCDNumber 显示
        self.lcd.display(time_text)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.deleteLater())
        context_menu.addAction(delete_action)
        context_menu.exec_(event.globalPos())

if __name__ == "__main__":
    #app = QApplication([])
    clock = ComponentWidget()
    clock.show()
    #app.exec_()
