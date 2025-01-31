import os
import sys
import json
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

# 创建一个按钮编辑器窗口
def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

try:
    # For Python 3
    from urllib.request import urlopen, Request
except ImportError:
    # For Python 2.7
    from urllib2 import urlopen, Request
try:
    PATH = os.path.join(os.path.dirname(__file__), "../../")
    PATH = os.path.abspath(PATH).replace("\\", "/")
except NameError:
    PATH = 'E:/OneButtonManager'
ICON_PATH = PATH + "/icons/"
FONT = PATH + "/Font/RepetitionScrolling.ttf"
FONT_FAMILY = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(FONT))[0]

try:
    PATH = os.path.join(os.path.dirname(__file__), "../../")
    PATH = os.path.abspath(PATH).replace("\\", "/")
except NameError:
    PATH = 'E:/OneButtonManager'
ICON_PATH = PATH + "/icons/"
FONT = PATH + "/Font/RepetitionScrolling.ttf"
FONT_FAMILY = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(FONT))[0]

class ComponentWidget(QWidget):
    def __init__(self, uid=0, size=42):
        super().__init__()
        try:
            uid = self.getUID()
        except:
            pass
        self.uid = uid
        self.SIZE = size
        self.WIDTH = int(165 * size / 42)
        self.fans_count = "00000"
        if self.uid:
            self.fans_count = self.get_bilibili_fans(uid)
            self.adjust_width()
        self.initUI()
        self.setFixedSize(QSize(self.WIDTH, self.SIZE))
        self.setToolTip(u"双击输入UID")
        self.setStatusTip(u"双击输入UID")

        # 设置定时器，每隔10分钟更新一次粉丝数
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fans_count)
        self.timer.start(10 * 60 * 1000)  # 10分钟，单位为毫秒

    def adjust_width(self):
        # 根据粉丝数的长度调整宽度
        extra_digits = len(self.fans_count) - 5
        self.WIDTH = int(165 * self.SIZE / 42) + extra_digits * ((self.SIZE+6) // 2)
        self.setFixedSize(QSize(self.WIDTH, self.SIZE))

    def initUI(self):
        self.globalLayout = QHBoxLayout()
        self.globalLayout.setAlignment(Qt.AlignTop)
        self.globalLayout.setContentsMargins(0, 0, 0, 0)

        self.inputLayout = QHBoxLayout()
        self.inputLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.inputLayout.setContentsMargins(0, 0, 0, 0)

        self.logo = QLabel(self)
        pixmap = QPixmap(ICON_PATH + '/components/bilibili.png')
        pixmap = pixmap.scaledToWidth(self.SIZE)
        self.logo.setPixmap(pixmap)
        self.inputLayout.addWidget(self.logo)

        self.label = QLabel(self.fans_count, self)
        self.label.setStyleSheet("font-size: {}px; font-weight: bold; color: #BDBDBD; font-family: {};".format(self.SIZE, FONT_FAMILY))
        self.inputLayout.addWidget(self.label)
        self.globalLayout.addLayout(self.inputLayout)

        self.inputUID = QLineEdit(self)
        self.inputUID.setPlaceholderText("输入UID并回车")
        self.inputUID.returnPressed.connect(self.update_uid)
        self.inputUID.hide()
        self.inputUID.setGeometry(0, int(self.SIZE/4), self.WIDTH, int(self.SIZE/2))


        self.setLayout(self.globalLayout)
        self.setWindowTitle("Bilibili 粉丝数")
        self.menu = QMenu(self)

    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))

    def get_bilibili_fans(self, uid):
        if not uid or uid == 0:
            return "00000"
        url = "https://api.bilibili.com/x/relation/stat?vmid={}".format(uid)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        request = Request(url, headers=headers)
        response = urlopen(request)
        if response.getcode() == 200:
            data = json.load(response)
            if data['code'] == 0:
                return "{:05d}".format(data['data']['follower'])
            else:
                print("Error: {}".format(data['message']))
        else:
            print("HTTP Error: {}".format(response.getcode()))
        return "00000"

    def update_fans_count(self):
        self.fans_count = self.get_bilibili_fans(self.uid)
        self.label.setText(self.fans_count)
        self.adjust_width()

    def update_uid(self):
        new_uid = self.inputUID.text()
        if new_uid.isdigit():
            self.uid = int(new_uid)
            self.update_fans_count()
        self.inputUID.hide()
        self.adjust_width()

        docPath = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) + '/OneTools/data/componentsData.json'
        with open(docPath, 'r') as f:
            data = json.load(f)
            data['UID'] = self.uid
        with open(docPath, 'w') as f:
            json.dump(data, f)

    def mouseDoubleClickEvent(self, event):
        self.inputUID.show()
        self.inputUID.setFocus()

    def getUID(self):
        # 读取json文件
        # 获取系统文档路径
        docPath = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) + '/OneTools/data/componentsData.json'
        uid = None
        if os.path.exists(docPath):
            with open(docPath, 'r') as f:
                data = json.load(f)
                if 'UID' in data.keys():
                    uid = data['UID']
        else:
            data = {'UID': 0}
            with open(docPath, 'w') as f:
                json.dump(data, f)
        return uid

# 创建一个模糊组件，用来叠在输入框下面，从而模糊背景
class BilibiliFanWidgetBlur(QWidget):
    def __init__(self, parent=None):
        super(BilibiliFanWidgetBlur, self).__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(QApplication.desktop().size())
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.show()

if __name__ == "__main__":
    #app = QApplication(sys.argv)
    uid = 14857382  # 替换为目标用户的 UID
    widget = ComponentWidget(uid)
    widget.show()
    #sys.exit(app.exec_())