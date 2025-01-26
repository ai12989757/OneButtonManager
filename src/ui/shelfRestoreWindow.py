import os
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from maya import mel
from functools import partial
from ..utils import imageManager
from ..utils import shelfDataManager
from ..utils.getBackShelfList import getBackShelfList
from ..ui import previewShelfWindow

try:
    reload(previewShelfWindow)
except:
    import importlib
    importlib.reload(previewShelfWindow)

from .mayaMQT  import maya_main_window
class toDefUI(QWidget):
    def __init__(self, parent=maya_main_window(), fileList=None, language=0):
        super(toDefUI, self).__init__(parent)
        self.iconDir = __file__.replace('\\', '/').replace('src/ui/shelfRestoreWindow.py', 'icons/')
        self.fileList = fileList
        self.language = language
        self.win = 'Shift2Default'
        self.title = 'Shift Manager'
        self.mPos = None
        self.width = 400
        self.height = 475
        self.setAttribute(Qt.WA_DeleteOnClose) # 设置窗口关闭事件
        self.createUI() # 创建UI
        self.load_settings() # 恢复上次的位置和大小
        
    def createUI(self):
        self.setWindowTitle(self.title)
        self.setObjectName(self.win)
        #self.resize(self.width, self.height) # 设置窗口大小
        #self.setGeometry(0, 0, self.width, self.height)
        #self.setAttribute(Qt.WA_TranslucentBackground)                           # 设置窗口背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)                  # 设置窗口无边框
        self.setFixedSize(self.width, self.height)

        self.Alllayout = QVBoxLayout(self)
        self.setLayout(self.Alllayout)
        self.Alllayout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        self.Alllayout.setSpacing(0)
        self.Alllayout.setContentsMargins(0,0,0,0)

        # 标题栏
        self.titleWidget = titleBar(
            self, text = self.title, 
            icon = self.iconDir+'red/Close.png',
            func = self.close
            )
        self.Alllayout.addWidget(self.titleWidget)
        
        # 图标
        self.iconLabel = QLabel()
        self.iconLabel.setToolTip(u'你干嘛，哎哟~')
        self.iconLabel.setStatusTip(u'你干嘛，哎哟~')
        self.pixmap = QPixmap(self.iconDir + 'AniBotPo.png')
        self.iconLabel.setPixmap(self.pixmap.scaled(QSize(405,100), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.Alllayout.addWidget(self.iconLabel, 0, Qt.AlignCenter)

        # 主布局
        self.layout = QVBoxLayout(self)
        self.Alllayout.addLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10,5,10,10)
        # 提示信息
        self.infoLayout = QHBoxLayout()
        self.layout.addLayout(self.infoLayout)
        self.infoLayout.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.infoLayout.setSpacing(10)
        self.infoLayout.setContentsMargins(0,0,0,0)
        # 类型切换按钮
        self.typeLayout = QHBoxLayout()
        self.infoLayout.addLayout(self.typeLayout)
        self.typeLayout.setAlignment(Qt.AlignLeft)
        self.typeLayout.setSpacing(5)
        self.typeLayout.setContentsMargins(0,0,0,0)
        self.melButton = QPushButton()
        self.melButton.setText('M')
        self.melButton.setStyleSheet('''
            QPushButton {
                border-radius: 22;
                border: 4px solid DeepSkyBlue;
                font: bold;
                font-size: 20px;
                background-color: #5d5d5d;
            }
            QPushButton:hover {
                background-color: #707070;
            }
            QPushButton:pressed {
                background-color: black;
                border: 4px solid white;
            }
        ''')
        self.melButton.setFixedSize(44, 44)
        self.melButton.setToolTip(u'切换显示类型, M: Maya 默认 Shelf, G: Gif 插件 Shelf')
        self.melButton.setStatusTip(u'切换显示类型, M: Maya 默认 Shelf, G: Gif 插件 Shelf')
        self.melButton.clicked.connect(self.listSwitch)
        self.typeLayout.addWidget(self.melButton)
        # 提示信息
        self.infoLabelMessageLayout = QVBoxLayout()
        self.infoLabelMessageLayout.setAlignment(Qt.AlignLeft)
        self.infoLabelMessageLayout.setSpacing(0)
        self.infoLabelMessageLayout.setContentsMargins(0,0,0,0)
        self.infoLayout.addLayout(self.infoLabelMessageLayout)
        self.infoLabel = QLabel()
        if self.language == 0:
            self.infoLabel.setText(u'找到下列<b style="color:DeepSkyBlue;">Maya 默认</b>工具栏备份文件')
        elif self.language == 1:
            self.infoLabel.setText(u'Found the following <b style="color:DeepSkyBlue;">Maya Default</b> Shelf Backup Files')
        # 设置字体
        self.infoLabel.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.infoLabelMessageLayout.addWidget(self.infoLabel, 0, Qt.AlignLeft|Qt.AlignBottom)
        self.infoMassage = QLabel()
        if self.language == 0:
            self.infoMassage.setText(u'双击预览工具栏，<b style="color:#00CED1;">高亮显示项</b>为智能判断为<b style="color:#00CED1;">正确</b>的备份文件')
        elif self.language == 1:
            self.infoMassage.setText(u'Double click to open file, restore shelf')
        self.infoMassage.setFont(QFont("Microsoft YaHei", 7, QFont.Bold))
        self.infoLabelMessageLayout.addWidget(self.infoMassage, 0, Qt.AlignLeft|Qt.AlignTop)


        # 文件列表
        self.fileListWidget = QTreeWidget()
        self.fileListWidget.setColumnCount(4)
        if self.language == 0:
            self.fileListWidget.setHeaderLabels(["名称", "日期", "大小", "操作"])
        elif self.language == 1:
            self.fileListWidget.setHeaderLabels(["Name", "Date", "Size", "Set"])
        self.fileListWidget.header().setDefaultAlignment(Qt.AlignLeft)
        self.fileListWidget.setIndentation(0)  # 去掉第一列里面项目左边的空白
        #self.fileListWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)  # 自动调整列宽
        self.fileListWidget.header().setStretchLastSection(True)  # 自动调整列宽
        self.fileListWidget.setColumnWidth(0, 90)  # 设置第一列宽度
        self.fileListWidget.setColumnWidth(1, 140)  # 设置第二列宽度
        self.fileListWidget.setColumnWidth(2, 80)
        self.fileListWidget.setColumnWidth(3, 30)  # 设置第四列宽度
        self.fileListWidget.setFixedHeight(260)
        self.fileListWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.layout.addWidget(self.fileListWidget)
        self.setFileListWidgetItems(self.fileList)

        # 按钮
        self.buttonLayout = QHBoxLayout()
        self.layout.addLayout(self.buttonLayout)
        self.buttonLayout.setAlignment(Qt.AlignCenter)
        self.buttonLayout.setSpacing(10)
        self.buttonLayout.setContentsMargins(0,0,0,0)
        # 文件夹
        # 系统文件夹路径 os.path.expanduser('~')
        backUPFolder = os.path.expanduser('~') + '/OneTools/data/shelf_backup'
        self.folderButton = QPushButton()
        self.folderButton.setText(u'备份路径')
        self.folderButton.setToolTip(u'打开备份文件夹, %s'%backUPFolder)
        self.folderButton.setStatusTip(u'打开备份文件夹, %s'%backUPFolder)
        self.folderButton.clicked.connect(lambda: os.startfile(backUPFolder))
        self.folderButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.buttonLayout.addWidget(self.folderButton)
        # 恢复所有
        self.restoreAllButton = QPushButton()
        self.restoreAllButton.setText(u'恢复所有')
        self.restoreAllButton.setToolTip(u'恢复列表中所有高亮显示的文件')
        self.restoreAllButton.setStatusTip(u'恢复列表中所有高亮显示的文件')
        self.restoreAllButton.clicked.connect(self.restoreShelf)
        self.restoreAllButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.buttonLayout.addWidget(self.restoreAllButton)
        # 恢复按钮
        self.restoreButton = QPushButton()
        self.restoreButton.setText(u'恢复当前')
        self.restoreButton.setToolTip(u'将当前工具栏恢复成maya默认工具栏，注意: 根据现有工具栏数据恢复，而不是从备份文件中恢复')
        self.restoreButton.setStatusTip(u'将根据当前工具栏恢复成maya默认工具栏，注意: 根据现有工具栏数据恢复，而不是从备份文件中恢复')
        self.restoreButton.clicked.connect(self.restoreShelf)
        self.restoreButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.buttonLayout.addWidget(self.restoreButton)
        # 刷新列表
        self.refreshButton = QPushButton()
        self.refreshButton.setText(u'刷新列表')
        self.refreshButton.setToolTip(u'刷新备份文件列表')
        self.refreshButton.setStatusTip(u'刷新备份文件列表')
        def refreshList():
            self.fileList = getBackShelfList(os.path.expanduser('~') + '/OneTools/data/shelf_backup/')
            self.fileListWidget.clear()
            self.setFileListWidgetItems(self.fileList)
        self.refreshButton.clicked.connect(refreshList)
        self.refreshButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.buttonLayout.addWidget(self.refreshButton)
        # 智能清理
        self.cleanButton = QPushButton()
        self.cleanButton.setText(u'智能清理')
        self.cleanButton.setToolTip(u'清理备份文件夹中的重复文件')
        self.cleanButton.setStatusTip(u'清理备份文件夹中的重复文件')
        def cleanBackUPShelf():
            for i in self.fileList:
                if i[3] is False:
                    if os.path.exists(i[4]):
                        os.remove(i[4])
            refreshList()
        self.cleanButton.clicked.connect(cleanBackUPShelf)
        self.cleanButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.buttonLayout.addWidget(self.cleanButton)

    def listSwitch(self):
        if self.melButton.text() == 'G':
            self.melButton.setText('M')
            self.melButton.setStyleSheet('''
            QPushButton {
                border-radius: 22;
                border: 4px solid DeepSkyBlue;
                font: bold;
                font-size: 20px;
                background-color: #5d5d5d;
            }
            QPushButton:hover {
                background-color: #707070;
            }
            QPushButton:pressed {
                background-color: black;
                border: 4px solid white;
            }
        ''')
            self.infoLabel.setText(u'找到下列<b style="color:DeepSkyBlue;">Maya 默认</b>工具栏备份文件')
            self.fileList = getBackShelfList(os.path.expanduser('~') + '/OneTools/data/shelf_backup/',fileType='mel')
            self.fileListWidget.clear()
            self.setFileListWidgetItems(self.fileList)
        elif self.melButton.text() == 'M':
            self.melButton.setText('G')
            self.melButton.setStyleSheet('''
                QPushButton {
                    font: bold;
                    font-size: 22px;
                    background-color: #5d5d5d;
                    border-radius: 22;
                    border: 4px solid #EE82EE;
                }
                QPushButton:hover {
                    background-color: #707070;
                }
                QPushButton:pressed {
                    background-color: black;
                    border: 4px solid white;
                }
            ''')
            self.infoLabel.setText(u'找到下列<b style="color:#EE82EE;">Gif 插件</b>工具栏备份文件')
            self.fileList = getBackShelfList(os.path.expanduser('~') + '/OneTools/data/shelf_backup/',fileType='json')
            self.fileListWidget.clear()
            self.setFileListWidgetItems(self.fileList)

    def setFileListWidgetItems(self,fileList):
        if fileList:
            for i in fileList:
                file_item = QTreeWidgetItem(self.fileListWidget)
                file_item.setText(0, i[0])
                file_item.setText(1, i[1])
                file_item.setText(2, i[2])
                self.fileListWidget.addTopLevelItem(file_item)
                file_item.setToolTip(0, i[4])
                file_item.setToolTip(1, i[4])
                file_item.setToolTip(2, i[4])
                file_item.setStatusTip(0, i[4])
                file_item.setStatusTip(1, i[4])
                file_item.setStatusTip(2, i[4])

                # 检查是否存在同名文件
                if i[3] == 1:
                    file_item.setForeground(0, QBrush(QColor('#00CED1')))
                    file_item.setForeground(1, QBrush(QColor('#00CED1')))
                    file_item.setForeground(2, QBrush(QColor('#00CED1')))
                elif i[3] == 2:
                    file_item.setForeground(0, QBrush(QColor('#FF6347')))
                    file_item.setForeground(1, QBrush(QColor('#FF6347')))
                    file_item.setForeground(2, QBrush(QColor('#FF6347')))

                # 恢复按钮
                restore_button = QPushButton()
                restore_button.setIcon(QIcon(self.iconDir+'green/Restore.png'))
                restore_button.setIconSize(QSize(15, 15))
                restore_button.setStyleSheet('background-color: rgba(0,0,0,0);border: none;')
                restore_button.enterEvent = partial(self.restore_button_on_enter_event, button=restore_button)
                restore_button.leaveEvent = partial(self.restore_button_on_leave_event, button=restore_button)
                restore_button.setToolTip(u'恢复备份文件')
                restore_button.setStatusTip(u'恢复备份文件')
                restore_button.clicked.connect(partial(self.restoreShelf, item=file_item, index=0))

                # 删除按钮
                delete_button = QPushButton()
                delete_button.setIcon(QIcon(self.iconDir+'red/Recycle.png'))
                delete_button.setIconSize(QSize(15, 15))
                delete_button.setStyleSheet('background-color: rgba(0,0,0,0);border: none;')
                delete_button.enterEvent = partial(self.delete_button_on_enter_event, button=delete_button)
                delete_button.leaveEvent = partial(self.delete_button_on_leave_event, button=delete_button)
                delete_button.setToolTip(u'删除选中的备份文件')
                delete_button.setStatusTip(u'删除选中的备份文件')
                delete_button.clicked.connect(partial(self.deleteItem, item=file_item))

                # 将按钮添加到 QTreeWidget 的同一列
                button_widget = QWidget()
                button_widget.setFixedWidth(40)
                button_layout = QHBoxLayout(button_widget)
                button_layout.addWidget(restore_button)
                button_layout.addWidget(delete_button)
                button_layout.setContentsMargins(5, 0, 0, 0)
                button_layout.setSpacing(10)
                self.fileListWidget.setItemWidget(file_item, 3, button_widget)

    def restoreShelf(self, item, index):
        index = self.fileListWidget.indexOfTopLevelItem(item)
        shelfDataManager.returnShelfData(shelfFile=self.fileList[index][4])

    def deleteItem(self, item):
        index = self.fileListWidget.indexOfTopLevelItem(item)
        filePath = self.fileList[index][4]
        if os.path.exists(filePath):
            os.remove(filePath)
            item.setHidden(True)
            mel.eval('print "// 结果: 文件已删除\\n"')
        else:
            item.setHidden(True)
            mel.eval('warning -n "文件不存在，已/移除列表项"')

    def on_item_double_clicked(self, item):
        index = self.fileListWidget.indexOfTopLevelItem(item)
        mel.eval('print "// 结果: 文件地址: %s\\n"' % self.fileList[index][4])
        #print('文件地址:', self.fileList[column][4])
        previewShelfWindow.PreviewShelfWindow(shelfFile=self.fileList[index][4]).show()

    def restore_button_on_enter_event(self, event,button):
        button.setIcon(imageManager.enhanceIcon(self.iconDir+'green/Restore.png'))
        button.setIconSize(QSize(20, 20))
    def restore_button_on_leave_event(self, event,button):
        button.setIcon(QIcon(self.iconDir+'green/Restore.png'))
        button.setIconSize(QSize(15, 15))
    def delete_button_on_enter_event(self, event,button):
        button.setIcon(imageManager.enhanceIcon(self.iconDir+'red/Recycle.png'))
        button.setIconSize(QSize(20, 20))
    def delete_button_on_leave_event(self, event,button):
        button.setIcon(QIcon(self.iconDir+'red/Recycle.png'))
        button.setIconSize(QSize(15, 15))

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.move(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()

    def closeEvent(self, event):
        # 保存当前的位置和大小
        self.save_settings()
        event.accept()

    def save_settings(self):
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())

    def load_settings(self):
        settings = QSettings()
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def paintEvent(self, event):
        # 设置圆角
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 10, 10) # 设置圆角路径
        path.translate(0.5, 0.5) # 修复边框模糊
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        # 创建一个 QPainter 对象来绘制边框
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # 抗锯齿
        pen = QPen(Qt.darkGray, 5)  # 设置描边颜色和宽度
        painter.setPen(pen)
        painter.drawPath(path)
        painter.end()

class titleBar(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(titleBar, self).__init__(parent)
        self.text = kwargs.get('text', None)
        self.icon = kwargs.get('icon', None)
        self.func = kwargs.get('func', None)
        self.setStyleSheet('background-color: rgba(0,0,0,0);')
        self.setFixedHeight(40)
        self.titleLayout = QHBoxLayout()
        #self.titleLayout.setAlignment(Qt.AlignCenter|Qt.AlignLeft)
        self.titleLayout.setContentsMargins(10, 4, 5, 0)
        self.setLayout(self.titleLayout)
        self.titleLabel = QLabel(self.text)
        
        self.titleLabel.setToolTip(u'标题栏')
        self.titleLabel.setStatusTip(u'标题栏')
        self.titleLabel.setStyleSheet('font: bold;font-size:20px;color: DeepSkyBlue;') # #00BFFF
        self.titleLayout.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        # 关闭按钮
        self.closeButton = QPushButton()
        self.closeButton.setToolTip(u'关闭')
        self.closeButton.setStatusTip(u'关闭')
        self.closeButton.setIcon(QIcon(self.icon))
        self.closeButton.setIconSize(QSize(30, 30))
        self.closeButton.setFixedSize(30, 30)
        # 设置按钮样式，无背景无边框
        self.closeButton.setStyleSheet('background-color: rgba(0,0,0,0);border: none;')
        self.closeButton.clicked.connect(self.func)
        self.closeButton.enterEvent = self.closeButtonEnterEvent
        self.closeButton.leaveEvent = self.closeButtonLeaveEvent
        self.titleLayout.addWidget(self.closeButton, 0, Qt.AlignRight)

        self.applyColorEffect()

    def applyColorEffect(self):
        import random
        self.colored_text = ""
        for char in self.text:
            # 生成随机颜色，确保颜色不偏黑
            while True:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                if r + g + b > 600:  # 确保颜色不偏黑
                    break
            color = QColor(r, g, b)
            self.colored_text += f'<span style="color: rgb({color.red()}, {color.green()}, {color.blue()});">{char}</span>'
        self.titleLabel.setText(self.colored_text)
        self.titleLabel.setTextFormat(Qt.RichText)

    def closeButtonEnterEvent(self,event):
        self.closeButton.setIcon(imageManager.enhanceIcon(self.icon))
    def closeButtonLeaveEvent(self,event):
        self.closeButton.setIcon(QIcon(self.icon))
