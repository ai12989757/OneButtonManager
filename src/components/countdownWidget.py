try:
    from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLCDNumber, QMenu, QAction, QLabel
    from PySide2.QtCore import QTimer, QTime, Qt, QElapsedTimer
    from PySide2.QtGui import QColor
except ImportError:
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLCDNumber, QMenu, QAction, QLabel
    from PySide6.QtCore import QTimer, QTime, Qt, QElapsedTimer
    from PySide6.QtGui import QColor

class CountdownWidget(QWidget):
    def __init__(self, countdown_time="00:00:00.000"):
        super().__init__()
        self.indexTepm = 0
        # 单击鼠标左键开始倒计时
        self.mousePressEvent = self.toggle_timer
        self.setStyleSheet("QFrame { border: none; }")
        # 创建 QLCDNumber 显示时间
        self.lcd_hours = QLCDNumber(self)
        self.lcd_hours.setDigitCount(2)  # 设置显示位数为2位，格式为 hh
        self.lcd_hours.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_hours.setFixedSize(42, 42)
        self.lcd_hours.setMouseTracking(True)  # 确保鼠标事件被捕获
        self.lcd_hours.installEventFilter(self)  # 安装事件过滤器

        self.lcd_minutes = QLCDNumber(self)
        self.lcd_minutes.setDigitCount(2)  # 设置显示位数为2位，格式为 mm
        self.lcd_minutes.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_minutes.setFixedSize(42, 42)
        self.lcd_minutes.setMouseTracking(True)  # 确保鼠标事件被捕获
        self.lcd_minutes.installEventFilter(self)  # 安装事件过滤器

        self.lcd_seconds = QLCDNumber(self)
        self.lcd_seconds.setDigitCount(2)  # 设置显示位数为2位，格式为 ss
        self.lcd_seconds.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_seconds.setFixedSize(42, 42)
        self.lcd_seconds.setMouseTracking(True)  # 确保鼠标事件被捕获
        self.lcd_seconds.installEventFilter(self)  # 安装事件过滤器

        self.lcd_ms = QLCDNumber(self)
        self.lcd_ms.setFixedSize(63, 42)
        self.lcd_ms.setDigitCount(3)  # 设置显示位数为3位，格式为 zzz
        self.lcd_ms.setSegmentStyle(QLCDNumber.Flat)

        # 创建 QLabel 显示冒号
        self.label_colon1 = QLabel(":")
        self.label_colon2 = QLabel(":")
        self.label_colon3 = QLabel(".")

        self.lcd_hours.setStyleSheet(f"QLCDNumber {{ color: #bdbdbd; }}")
        self.lcd_minutes.setStyleSheet(f"QLCDNumber {{ color:#bdbdbd; }}")
        self.lcd_seconds.setStyleSheet(f"QLCDNumber {{ color: #bdbdbd; }}")
        self.lcd_ms.setStyleSheet(f"QLCDNumber {{ color: #bdbdbd; }}")
        self.label_colon1.setStyleSheet(f"QLabel {{ color: #bdbdbd; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
        self.label_colon2.setStyleSheet(f"QLabel {{ color: #bdbdbd; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
        self.label_colon3.setStyleSheet(f"QLabel {{ color: #bdbdbd; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
        

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        # 初始化倒计时时间
        self.initial_time = QTime.fromString(countdown_time, 'hh:mm:ss.zzz')
        self.time = QTime.fromString(countdown_time, 'hh:mm:ss.zzz')

        # 创建布局
        layout = QHBoxLayout()
        layout.addWidget(self.lcd_hours)
        layout.addWidget(self.label_colon1)
        layout.addWidget(self.lcd_minutes)
        layout.addWidget(self.label_colon2)
        layout.addWidget(self.lcd_seconds)
        layout.addWidget(self.label_colon3)
        layout.addWidget(self.lcd_ms)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)  # 设置布局的间距
        
        self.setLayout(layout)

        # 初始化时间显示
        self.update_time()
        # 创建 QElapsedTimer
        self.elapsed_timer = QElapsedTimer()

        # 记录鼠标拖拽的起始位置
        self.drag_start_pos = None
        self.dragging_component = None

    def eventFilter(self, source, event):
        if event.type() == event.MouseButtonPress and event.button() == Qt.MiddleButton:
            self.indexTepm = 0
            self.drag_start_pos = event.pos()
            self.dragging_component = source
            return True
        elif event.type() == event.MouseMove and self.drag_start_pos:
            self.dragging = True
            self.handle_drag(event.pos())
            return True
        elif event.type() == event.MouseButtonRelease and event.button() == Qt.MiddleButton:
            self.indexTepm = 0
            self.drag_start_pos = None
            self.dragging_component = None
            return True
        elif event.type() == event.Wheel:
            self.dragging_component = source
            self.handle_wheel(event.angleDelta())
            return True

        return super().eventFilter(source, event)
    
    def handle_wheel(self, delta):
        direction = 1 if delta.y() > 0 else -1
        if self.dragging_component is self.lcd_hours:
            if self.time.hour() == 0 and direction < 0:
                return
            if self.time.hour() == 23 and direction > 0:
                return
            new_time = self.time.addSecs(3600 * direction)
            # 确保小时在0到24之间
            if 0 <= new_time.hour() <= 23:
                self.time = new_time
        elif self.dragging_component is self.lcd_minutes:
            if self.time.minute() == 0 and direction < 0:
                return
            if self.time.minute() == 59 and direction > 0:
                return
            
            new_time = self.time.addSecs(60 * direction)
            # 确保分钟在0到59之间
            if 0 <= new_time.minute() <= 59:
                self.time = new_time
        elif self.dragging_component is self.lcd_seconds:
            if self.time.second() == 0 and direction < 0:
                return
            if self.time.second() == 59 and direction > 0:
                return
            new_time = self.time.addSecs(direction)

            # 确保秒在0到59之间
            if 0 <= new_time.second() <= 59:
                self.time = new_time
        # 初始化倒计时时间
        self.initial_time = self.time
        self.update_time()

    def handle_drag(self, current_pos):
        if not self.drag_start_pos or not self.dragging_component:
            return

        delta = current_pos - self.drag_start_pos
        
        direction = 1 if delta.x() > 0 else -1
        if self.indexTepm != 5 and self.indexTepm != -5:
            self.indexTepm += direction
            return 
        self.indexTepm = 0
        if self.dragging_component is self.lcd_hours:
            if self.time.hour() == 0 and direction < 0:
                return
            if self.time.hour() == 23 and direction > 0:
                return
            new_time = self.time.addSecs(3600 * direction)
            # 确保小时在0到24之间
            if 0 <= new_time.hour() <= 23:
                self.time = new_time
        elif self.dragging_component is self.lcd_minutes:
            if self.time.minute() == 0 and direction < 0:
                return
            if self.time.minute() == 59 and direction > 0:
                return
            
            new_time = self.time.addSecs(60 * direction)
            # 确保分钟在0到59之间
            if 0 <= new_time.minute() <= 59:
                self.time = new_time
        elif self.dragging_component is self.lcd_seconds:
            if self.time.second() == 0 and direction < 0:
                return
            if self.time.second() == 59 and direction > 0:
                return
            new_time = self.time.addSecs(direction)

            # 确保秒在0到59之间
            if 0 <= new_time.second() <= 59:
                self.time = new_time

        # 初始化倒计时时间
        self.initial_time = self.time
        self.update_time()
        self.drag_start_pos = current_pos

    def update_time(self):
        if self.timer.isActive():
            elapsed = self.elapsed_timer.elapsed()
            self.elapsed_timer.restart()
            self.time = self.time.addMSecs(-elapsed)
        # 检查倒计时是否结束
        if self.time <= QTime(0, 0, 0, 10):
            self.time = QTime(0, 0, 0, 0)
            self.timer.stop()
        # 格式化时间字符串
        hours_text = self.time.toString('hh')
        minutes_text = self.time.toString('mm')
        seconds_text = self.time.toString('ss')
        ms_text = self.time.toString('zzz')
        # 更新 QLCDNumber 显示
        self.lcd_hours.display(hours_text)
        self.lcd_minutes.display(minutes_text)
        self.lcd_seconds.display(seconds_text)
        self.lcd_ms.display(ms_text)
        # 更新颜色
        self.update_color()

    def update_color(self):
        # 计算剩余时间的百分比
        if self.initial_time == QTime(0, 0, 0, 0):
            return
        total_milliseconds = (self.initial_time.hour() * 3600 + self.initial_time.minute() * 60 + self.initial_time.second()) * 1000 + self.initial_time.msec()
        remaining_milliseconds = (self.time.hour() * 3600 + self.time.minute() * 60 + self.time.second()) * 1000 + self.time.msec()
        percentage = remaining_milliseconds / total_milliseconds

        # 计算颜色
        start_color = QColor(173, 255, 47)  # 淡绿色
        end_color = QColor(255, 99, 71)    # 淡红色

        red = start_color.red() + percentage * (end_color.red() - start_color.red())
        green = start_color.green() + percentage * (end_color.green() - start_color.green())
        blue = start_color.blue() + percentage * (end_color.blue() - start_color.blue())

        color = QColor(int(red), int(green), int(blue)).name()

        self.lcd_hours.setStyleSheet(f"QLCDNumber {{ color: {color}; }}")
        self.lcd_minutes.setStyleSheet(f"QLCDNumber {{ color: {color}; }}")
        self.lcd_seconds.setStyleSheet(f"QLCDNumber {{ color: {color}; }}")
        self.lcd_ms.setStyleSheet(f"QLCDNumber {{ color: {color}; }}")
        self.label_colon1.setStyleSheet(f"QLabel {{ color: {color}; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
        self.label_colon2.setStyleSheet(f"QLabel {{ color: {color}; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
        self.label_colon3.setStyleSheet(f"QLabel {{ color: {color}; font-size: 32px; font-family: '等线'; font-weight: bold;}}")

    def toggle_timer(self,event=None):
        # 如果是左击事件
        if event and event.button() == Qt.LeftButton:
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.elapsed_timer.restart()  # 重置计时器
                self.timer.start(10)  # 每1毫秒更新一次

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # 添加停止菜单项
        stop_action = QAction("停止", self)
        stop_action.triggered.connect(self.stop_timer)
        context_menu.addAction(stop_action)

        # 归零
        reset_action = QAction("归零", self)
        reset_action.triggered.connect(lambda: self.set_preset_time("00:00:00.000"))
        context_menu.addAction(reset_action)

        # 添加倒计时预设菜单项
        preset_menu = QMenu("倒计时预设", self)
        preset_5min = QAction("5分钟", self)
        preset_5min.triggered.connect(lambda: self.set_preset_time("00:05:00.000"))
        preset_menu.addAction(preset_5min)
        preset_10min = QAction("10分钟", self)
        preset_10min.triggered.connect(lambda: self.set_preset_time("00:10:00.000"))
        preset_menu.addAction(preset_10min)
        preset_15min = QAction("15分钟", self)
        preset_15min.triggered.connect(lambda: self.set_preset_time("00:15:00.000"))
        preset_menu.addAction(preset_15min)
        preset_30min = QAction("30分钟", self)
        preset_30min.triggered.connect(lambda: self.set_preset_time("00:30:00.000"))
        preset_menu.addAction(preset_30min)
        context_menu.addMenu(preset_menu)
        
        # 添加删除菜单项
        context_menu.addSeparator()
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_widget)
        context_menu.addAction(delete_action)

        # 显示菜单
        context_menu.exec_(event.globalPos())

    def set_preset_time(self, preset_time):
        self.timer.stop()
        self.initial_time = QTime.fromString(preset_time, 'hh:mm:ss.zzz')
        self.time = QTime.fromString(preset_time, 'hh:mm:ss.zzz')
        if self.time == QTime(0, 0, 0, 0):
            self.lcd_hours.setStyleSheet(f"QLCDNumber {{ color: #bdbdbd; }}")
            self.lcd_minutes.setStyleSheet(f"QLCDNumber {{ color:#bdbdbd; }}")
            self.lcd_seconds.setStyleSheet(f"QLCDNumber {{ color: #bdbdbd; }}")
            self.lcd_ms.setStyleSheet(f"QLCDNumber {{ color: #bdbdbd; }}")
            self.label_colon1.setStyleSheet(f"QLabel {{ color: #bdbdbd; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
            self.label_colon2.setStyleSheet(f"QLabel {{ color: #bdbdbd; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
            self.label_colon3.setStyleSheet(f"QLabel {{ color: #bdbdbd; font-size: 32px; font-family: '等线'; font-weight: bold;}}")
        self.update_time()

    def stop_timer(self):
        self.timer.stop()
        self.time = QTime.fromString(self.initial_time.toString('hh:mm:ss.zzz'), 'hh:mm:ss.zzz')
        self.update_time()

    def delete_widget(self):
        self.timer.stop()
        self.deleteLater()

if __name__ == "__main__":
    #app = QApplication([])
    countdown_time = "00:00:10.000"  # 设置倒计时时间为默认值
    countdown = CountdownWidget(countdown_time)
    countdown.show()
    #app.exec_()