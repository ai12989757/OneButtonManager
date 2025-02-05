try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from functools import partial

class DragWidgetOrder:
    widgetLayout = None
    alignment = 'h'
    buttonList = []
    buttonIndex = 0
    spacing = 0
    margin = 0

    dragging = False
    startPos = QPoint()
    valueX = 0.00  # 初始化数值
    valueY = 0.00  # 初始化数值
    currentPos = QPoint()
    delta = QPoint()
    widgetStartPos = QPoint()
    widgetCurrentPos = QPoint()
    
    @staticmethod
    def __init__(widget):
        def widgetMousePressEvent(event):
            if event.button() == Qt.MiddleButton:
                DragWidgetOrder.dragging = True
                DragWidgetOrder.startDrag(widget, event)
            #super().mousePressEvent(event)
            super(widget.__class__, widget).mousePressEvent(event)
        def widgetMouseMoveEvent(event):
            if DragWidgetOrder.dragging:
                DragWidgetOrder.performDrag(widget, event)
            #super().mouseMoveEvent(event)
            super(widget.__class__, widget).mouseMoveEvent(event)
        def widgetMouseReleaseEvent(event):
            #if event.button() == Qt.MiddleButton:
            if DragWidgetOrder.dragging:
                DragWidgetOrder.endDrag(widget, event)
            DragWidgetOrder.dragging = False
            super(widget.__class__, widget).mouseReleaseEvent(event)
        widget.mousePressEvent = widgetMousePressEvent
        widget.mouseMoveEvent = widgetMouseMoveEvent
        widget.mouseReleaseEvent = widgetMouseReleaseEvent

    @staticmethod
    def find_widget_layout(widget):
        parent = widget.parent()
        parentLayout = parent.layout()
        if parentLayout == None:
            return
        DragWidgetOrder.widgetLayout = parentLayout
        # for i in range(parentLayout.count()):
        #     if parentLayout.itemAt(i).widget() == widget:
        #         DragWidgetOrder.widgetLayout = parentLayout
        #         if DragWidgetOrder.widgetLayout != None:
        #             DragWidgetOrder.spacing = DragWidgetOrder.widgetLayout.spacing()
        #             DragWidgetOrder.margin = DragWidgetOrder.widgetLayout.contentsMargins().left()

        if DragWidgetOrder.widgetLayout != None:
            DragWidgetOrder.spacing = DragWidgetOrder.widgetLayout.spacing()
            DragWidgetOrder.margin = DragWidgetOrder.widgetLayout.contentsMargins().left()
            DragWidgetOrder.widgetLayout = parentLayout
            DragWidgetOrder.spacing = DragWidgetOrder.widgetLayout.spacing()
            DragWidgetOrder.margin = DragWidgetOrder.widgetLayout.contentsMargins().left()
            # 获取布局是否是水平还是垂直
            DragWidgetOrder.alignment = DragWidgetOrder.widgetLayout.alignment()
            if DragWidgetOrder.alignment & Qt.AlignLeft or DragWidgetOrder.alignment & Qt.AlignRight or DragWidgetOrder.alignment & Qt.AlignVCenter:
                DragWidgetOrder.alignment = 'h'
            elif DragWidgetOrder.alignment & Qt.AlignTop or DragWidgetOrder.alignment & Qt.AlignBottom or DragWidgetOrder.alignment & Qt.AlignHCenter:
                DragWidgetOrder.alignment = 'v'
            else:
                DragWidgetOrder.alignment = 'h'
                
    def startDrag(widget, event):
        try:
            DragWidgetOrder.find_widget_layout(widget)
            widgetParentLayout = DragWidgetOrder.widgetLayout
            if widgetParentLayout == None:
                print('widgetParentLayout is None')
                return
            DragWidgetOrder.valueX = 0.00  # 初始化数值
            DragWidgetOrder.valueY = 0.00  # 初始化数值
            # 获取光标移动的距离
            DragWidgetOrder.startPos = event.pos()
            DragWidgetOrder.widgetStartPos = widget.pos()
            widget.buttonParent = widget.parent()
            # 列出所有的按钮
            DragWidgetOrder.buttonList = []

            for i in range(widgetParentLayout.count()):
                DragWidgetOrder.buttonList.append(widgetParentLayout.itemAt(i).widget())
            # 获取按钮的索引
            if widget in DragWidgetOrder.buttonList:
                DragWidgetOrder.buttonIndex = DragWidgetOrder.buttonList.index(widget)
        except:
            DragWidgetOrder.startDrag(widget, event) # 重新尝试，maya中会出现错误 already deleted 错误, 重新尝试一次就可以了

    def performDrag(widget, event):
        if not DragWidgetOrder.buttonList:
            return
        DragWidgetOrder.currentPos = event.pos()
        DragWidgetOrder.delta = DragWidgetOrder.currentPos - DragWidgetOrder.startPos
        DragWidgetOrder.valueX += DragWidgetOrder.delta.x()
        DragWidgetOrder.valueY += DragWidgetOrder.delta.y()
        DragWidgetOrder.startPos = DragWidgetOrder.currentPos

        if DragWidgetOrder.buttonList == []:
            DragWidgetOrder.startDrag(widget, event)
            if DragWidgetOrder.buttonList == []:
                print('buttonList is empty')
            return
        # 将当前拖拽的按钮显示在最前面
        widget.raise_()

        # 移动按钮
        if DragWidgetOrder.alignment == 'v':
            widget.move(widget.pos() + QPoint(0, DragWidgetOrder.valueY))
        elif DragWidgetOrder.alignment == 'h':
            widget.move(widget.pos() + QPoint(DragWidgetOrder.valueX, 0))
        DragWidgetOrder.widgetCurrentPos = widget.pos()
        # 求出当前按钮移动的距离
        movePos = widget.pos()
    
        # 判断按钮移动方向
        if len(DragWidgetOrder.buttonList) != 1:  # 如果不止一个按钮
            if DragWidgetOrder.alignment == 'h':
                if DragWidgetOrder.valueX > 0:  # 如果按钮向右移动
                    if DragWidgetOrder.buttonIndex != len(DragWidgetOrder.buttonList) - 1:
                        # 获取右边按钮的位置
                        rightButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1]
                        rightButtonPos = rightButton.pos()
                        if movePos.x() + widget.width() + DragWidgetOrder.spacing > rightButtonPos.x() + (rightButton.width() / 2):  # 如果按钮最右边的位置大于右边按钮的一半宽度
                            rightButton.move(QPoint(rightButtonPos.x() - widget.width() - DragWidgetOrder.spacing, rightButtonPos.y()))
                            # 将当前按钮的的索引与右边按钮的索引交换
                            DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1] = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex]
                            # 交换按钮的索引
                            DragWidgetOrder.buttonIndex += 1
                else:  # 如果按钮向左移动
                    if DragWidgetOrder.buttonIndex != 0:
                        # 获取左边按钮的位置
                        leftButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1]
                        leftButtonPos = leftButton.pos()
                        if movePos.x() < leftButtonPos.x() + (leftButton.width() / 2) + DragWidgetOrder.spacing:  # 如果按钮最左边的位置小于左边按钮的一半宽度
                            leftButton.move(QPoint(leftButtonPos.x() + widget.width() + DragWidgetOrder.spacing, leftButtonPos.y()))
                            # 将当前按钮的的索引与左边按钮的索引交换
                            DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1] = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex]
                            # 交换按钮的索引
                            DragWidgetOrder.buttonIndex -= 1
            elif DragWidgetOrder.alignment == 'v':
                if DragWidgetOrder.valueY > 0:  # 如果按钮向下移动
                    if DragWidgetOrder.buttonIndex != len(DragWidgetOrder.buttonList) - 1:
                        # 获取下边按钮的位置
                        bottomButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1]
                        bottomButtonPos = bottomButton.pos()
                        if movePos.y() + widget.height() + DragWidgetOrder.spacing > bottomButtonPos.y() + (bottomButton.height() / 2):  # 如果按钮最下边的位置大于下边按钮的一半高度
                            bottomButton.move(QPoint(bottomButtonPos.x(), bottomButtonPos.y() - widget.height() - DragWidgetOrder.spacing))
                            # 将当前按钮的的索引与下边按钮的索引交换
                            DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1] = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex]
                            # 交换按钮的索引
                            DragWidgetOrder.buttonIndex += 1
                else:  # 如果按钮向上移动
                    if DragWidgetOrder.buttonIndex != 0:
                        # 获取上边按钮的位置
                        topButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1]
                        topButtonPos = topButton.pos()
                        if movePos.y() < topButtonPos.y() + (topButton.height() / 2) + DragWidgetOrder.spacing:  # 如果按钮最上边的位置小于上边按钮的一半高度
                            topButton.move(QPoint(topButtonPos.x(), topButtonPos.y() + widget.height() + DragWidgetOrder.spacing))
                            # 将当前按钮的的索引与上边按钮的索引交换
                            DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1] = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1], DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex]
                            # 交换按钮的索引
                            DragWidgetOrder.buttonIndex -= 1


    def endDrag(widget, event):
        if not DragWidgetOrder.buttonList:
            return
        animationDuration = 100
        animationEasingCurve = QEasingCurve.Linear
        # 中键释放后，将按钮的位置依附到相邻的按钮边上
        # 判断要依附的按钮是左边的还是右边的
        if len(DragWidgetOrder.buttonList) != 1:
            if DragWidgetOrder.alignment == 'h':
                if DragWidgetOrder.buttonIndex == 0:  # 如果是第一个按钮
                    rightButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1]
                    rightButtonPos = rightButton.pos()
                    target_pos = QPoint(rightButtonPos.x() - widget.width() - DragWidgetOrder.spacing, widget.pos().y())
                    if target_pos.x() - widget.pos().x() > widget.width():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                elif DragWidgetOrder.buttonIndex == len(DragWidgetOrder.buttonList) - 1:  # 如果是最后一个按钮
                    leftButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1]
                    leftButtonPos = leftButton.pos()
                    leftButtonWidth = leftButton.width()
                    target_pos = QPoint(leftButtonPos.x() + leftButtonWidth + DragWidgetOrder.spacing, widget.pos().y())
                    if widget.pos().x() - target_pos.x() > widget.width():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                else:
                    animationDuration = 100
                    leftButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1]
                    rightButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1]
                    buttonPos = widget.pos()
                    leftButtonPos = leftButton.pos()
                    rightButtonPos = rightButton.pos()
                    buttonWidth = widget.width()
                    leftButtonWidth = leftButton.width()
                    rightButtonWidth = rightButton.width()
                    distanceToLeftButton = abs(buttonPos.x() - leftButtonPos.x() - leftButtonWidth - DragWidgetOrder.spacing)
                    distanceToRightButton = abs(buttonPos.x() + buttonWidth + DragWidgetOrder.spacing - rightButtonPos.x())
                    if distanceToLeftButton < distanceToRightButton:
                        target_pos = QPoint(leftButtonPos.x() + leftButtonWidth + DragWidgetOrder.spacing, widget.pos().y())
                    else:
                        target_pos = QPoint(rightButtonPos.x() - buttonWidth - DragWidgetOrder.spacing, widget.pos().y())
            elif DragWidgetOrder.alignment == 'v':
                if DragWidgetOrder.buttonIndex == 0:  # 如果是第一个按钮
                    bottomButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1]
                    bottomButtonPos = bottomButton.pos()
                    target_pos = QPoint(widget.pos().x(), bottomButtonPos.y() - widget.height() - DragWidgetOrder.spacing)
                    if target_pos.y() - widget.pos().y() > widget.height():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                elif DragWidgetOrder.buttonIndex == len(DragWidgetOrder.buttonList) - 1:  # 如果是最后一个按钮
                    topButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1]
                    topButtonPos = topButton.pos()
                    topButtonHeight = topButton.height()
                    target_pos = QPoint(widget.pos().x(), topButtonPos.y() + topButtonHeight + DragWidgetOrder.spacing)
                    if widget.pos().y() - target_pos.y() > widget.height():
                        animationDuration = 1000
                        animationEasingCurve = QEasingCurve.OutBounce
                else:
                    animationDuration = 100
                    topButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex - 1]
                    bottomButton = DragWidgetOrder.buttonList[DragWidgetOrder.buttonIndex + 1]
                    buttonPos = widget.pos()
                    topButtonPos = topButton.pos()
                    bottomButtonPos = bottomButton.pos()
                    buttonHeight = widget.height()
                    topButtonHeight = topButton.height()
                    bottomButtonHeight = bottomButton.height()
                    distanceToTopButton = abs(buttonPos.y() - topButtonPos.y() - topButtonHeight - DragWidgetOrder.spacing)
                    distanceToBottomButton = abs(buttonPos.y() + buttonHeight + DragWidgetOrder.spacing - bottomButtonPos.y())
                    if distanceToTopButton < distanceToBottomButton:
                        target_pos = QPoint(widget.pos().x(), topButtonPos.y() + topButtonHeight + DragWidgetOrder.spacing)
                    else:
                        target_pos = QPoint(widget.pos().x(), bottomButtonPos.y() - buttonHeight - DragWidgetOrder.spacing)
        else:
            target_pos = DragWidgetOrder.widgetStartPos # 如果只有一个按钮，那么按钮回到原来的位置
            if DragWidgetOrder.alignment == 'h':
                if abs(DragWidgetOrder.widgetCurrentPos.x()-DragWidgetOrder.widgetStartPos.x()) > widget.width()*2:
                    animationDuration = 1000
                    animationEasingCurve = QEasingCurve.OutBounce
            elif DragWidgetOrder.alignment == 'v':
                if abs(target_pos.y()) > widget.height()*2:
                    animationDuration = 1000
                    animationEasingCurve = QEasingCurve.OutBounce

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(animationDuration)
        animation.setEasingCurve(animationEasingCurve)
        animation.setStartValue(widget.pos())
        animation.setEndValue(target_pos)
        animation.start()
        widget.animation = animation
        # 当动画结束时，更新按钮列表
        widget.animation.finished.connect(partial(DragWidgetOrder.updateButtonList, widget))

    @staticmethod
    def updateButtonList(widget):
        # 获取新的按钮列表
        buttonListNew = []
        widgetParentLayout = DragWidgetOrder.widgetLayout
        if widgetParentLayout == None:
            print('widgetParentLayout is None')
            return

        for i in range(widgetParentLayout.count()):
            buttonListNew.append(widgetParentLayout.itemAt(i).widget())
        # 如果按钮列表不一样，则说明按钮的位置发生了变化
        if DragWidgetOrder.buttonList != buttonListNew:
            # 将layout上的widget全部移除后，重新添加，这样就可以保证按钮的顺序是正确的
            for i in DragWidgetOrder.buttonList:
                i.setParent(None)
            for i in DragWidgetOrder.buttonList:
                widgetParentLayout.addWidget(i)
            DragWidgetOrder.buttonList = buttonListNew