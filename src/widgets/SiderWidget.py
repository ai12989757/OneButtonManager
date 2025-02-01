import os
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class SiderWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)
        self.size = kwargs.get("size", 48)
        self.alignment = kwargs.get("alignment", 'H') # H or h: Horizontal, V or v: Vertical
        self.SCREEN_WIDTH = self.size*3
        self.SCREEN_HEIGHT = self.size
        self.setFixedSize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT )
        # Create a layout
        self.golabalLayout = QHBoxLayout(self)
        self.golabalLayout.setContentsMargins(5, 0, 5, 0)
        self.golabalLayout.setSpacing(0)
        self.golabalLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.golabalLayout)

        # 右击菜单
        self.contextMenu = QMenu(self)
        self.addDefaultMenu()

        # 滑块
        self.slider = QSlider()
        if self.alignment == 'H' or self.alignment == 'h':
            self.slider.setOrientation(Qt.Horizontal)
            self.slider.setFixedHeight(self.size)
        elif self.alignment == 'V' or self.alignment == 'v':
            self.slider.setOrientation(Qt.Vertical)
            self.slider.setFixedWidth(self.size)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        
        self.set_slider_style(style='slider_win11')
        self.golabalLayout.addWidget(self.slider)

    def contextMenuEvent(self, event):
        self.contextMenu.exec_(event.globalPos())

    def set_slider_style(self, style='slider_win11'):
        stylePath = os.path.join(os.path.dirname(__file__), 'styles/')
        stylePath += style + '.qss'
        if not style:
            stylePath += 'slider_win11.qss'
        with open(stylePath, 'r', encoding='utf-8') as f:
            slider_style = f.read()
        self.slider.setStyleSheet(slider_style)

    def addDefaultMenu(self):
        closeAction = QAction('关闭', self)
        closeAction.triggered.connect(self.close)
        self.contextMenu.addAction(closeAction)
        editAction = QAction('编辑', self)
        editAction.triggered.connect(self.edit)
        self.contextMenu.addAction(editAction)

    def edit(self):
        from ..ui.siderEditor import siderEditorWindow
        self.siderEditor = siderEditorWindow(self, language=0)
        self.siderEditor.show()
           
if __name__ == "__main__":
    # import sys
    # app = QApplication(sys.argv)
    window = SiderWidget()
    window.show()
    #sys.exit(app.exec_())