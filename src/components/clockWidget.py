# -*- coding: utf-8 -*-
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
        super(ComponentWidget,self).__init__()
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

        # 创建右键菜单
        self.context_menu = QMenu(self)
        delete_action = QAction(u"删除", self)
        delete_action.triggered.connect(lambda: self.deleteLater())
        self.context_menu.addAction(delete_action)
        self.context_menu.addAction(u'闹钟', self.addAlarm)

    def update_time(self):
        # 获取当前时间
        current_time = QTime.currentTime()
        # 格式化时间字符串
        time_text = current_time.toString('hh:mm:ss')
        # 更新 QLCDNumber 显示
        self.lcd.display(time_text)

    def addAlarm(self):
        # 创建闹钟对话框
        alarm_time, ok = QInputDialog.getText(self, u"闹钟", u"设置闹钟时间(格式: hh:mm:ss)")
        if ok:
            # 创建定时器
            alarm_timer = QTimer(self)
            alarm_timer.timeout.connect(lambda: self.alarm(alarm_timer))
            # 获取闹钟时间
            alarm_time = QTime.fromString(alarm_time, 'hh:mm:ss')
            # 计算闹钟时间与当前时间的时间差
            current_time = QTime.currentTime()
            msecs = current_time.msecsTo(alarm_time)
            # 设置定时器
            alarm_timer.start(msecs)
            self.alarm_timer = alarm_timer
            # 在菜单里添加闹钟的时间选项
            self.context_menu.addAction(alarm_time.toString('hh:mm:ss'))
            # 子菜单里添加删除闹钟的选项
            alarm_timeAction = QAction(alarm_time.toString('hh:mm:ss'), self)
            alarm_timeAction.triggered.connect(lambda: self.deleteAlarm(alarm_timer))
            self.context_menu.addAction(alarm_timeAction)
            # 闹钟的子菜单里添加删除选项
            delete_action = QAction(u"删除", self)
            delete_action.triggered.connect(lambda: self.deleteAlarm(alarm_timer))
            alarm_timeAction.setMenu(QMenu())
            alarm_timeAction.menu().addAction(delete_action)
            self.context_menu.exec_()
        
    def alarm(self, alarm_timer):
        # 创建消息框
        QMessageBox.information(self, u"闹钟", u"时间到了！")
        # 停止定时器
        alarm_timer.stop()

    def deleteAlarm(self, alarm_timer):
        # 停止定时器
        alarm_timer.stop()
        # 删除菜单里的闹钟时间选项
        self.context_menu.removeAction(self.sender())
        # 删除子菜单
        self.sender().menu().deleteLater()
        # 删除子菜单里的删除选项
        self.sender().menu().actions()[0].deleteLater()


    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

if __name__ == "__main__":
    #app = QApplication([])
    clock = ComponentWidget()
    clock.show()
    #app.exec_()
