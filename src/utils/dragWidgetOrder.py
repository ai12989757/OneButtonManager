try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from functools import partial

def find_widget_layout(widget):
    parent = widget.parent()
    parentLayout = parent.layout()
    widgetLayout = None
    for i in range(parentLayout.count()):
        if parentLayout.itemAt(i).widget() == widget:
            widgetLayout = parentLayout.itemAt(i).layout()
            if widgetLayout != None:
                break
        if widgetLayout == None:
            checkLayout = parentLayout.itemAt(i).layout()
            for j in range(checkLayout.count()):
                if checkLayout.itemAt(j).widget() == widget:
                    widgetLayout = checkLayout
                    if widgetLayout != None:
                        break
    return widgetLayout
    

def startDrag(widget, event):
    widgetParentLayout = find_widget_layout(widget)
    # 获取光标移动的距离
    widget.startPos = event.pos()
    widget.buttonParent = widget.parent()
    # 列出所有的按钮
    widget.buttonList = []
    if widget.buttonParent.__class__.__name__ == 'ButtonEditorWindow':
        widget.buttonList = [widget]
        widget.buttonIndex = 0
        return
    for i in range(widgetParentLayout.count()):
        widget.buttonList.append(widgetParentLayout.itemAt(i).widget())
    # 获取按钮的索引
    widget.buttonIndex = widget.buttonList.index(widget)
    
def performDrag(widget, event, spacing=10):
    # 将当前拖拽的按钮显示在最前面
    widget.raise_()

    # 移动按钮
    widget.move(widget.pos() + QPoint(widget.valueX, 0))

    # 求出当前按钮移动的距离
    movePos = widget.pos()

    # 判断按钮移动方向
    if len(widget.buttonList) != 1:  # 如果不止一个按钮
        if widget.valueX > 0:  # 如果按钮向右移动
            # 判断当前按钮是否是最后一个按钮
            if widget.buttonIndex != len(widget.buttonList) - 1:
                # 获取右边按钮的位置
                rightButton = widget.buttonList[widget.buttonIndex + 1]
                rightButtonPos = rightButton.pos()
                if movePos.x() + widget.width() + spacing > rightButtonPos.x() + (rightButton.width() / 2):  # 如果按钮最右边的位置大于右边按钮的一半宽度
                    rightButton.move(QPoint(rightButtonPos.x() - widget.width() - spacing, rightButtonPos.y()))
                    # 将当前按钮的的索引与右边按钮的索引交换
                    widget.buttonList[widget.buttonIndex], widget.buttonList[widget.buttonIndex + 1] = widget.buttonList[widget.buttonIndex + 1], widget.buttonList[widget.buttonIndex]
                    # 交换按钮的索引
                    widget.buttonIndex += 1
        else:  # 如果按钮向左移动
            if widget.buttonIndex != 0:
                # 获取左边按钮的位置
                leftButton = widget.buttonList[widget.buttonIndex - 1]
                leftButtonPos = leftButton.pos()
                if movePos.x() < leftButtonPos.x() + (leftButton.width() / 2) + spacing:  # 如果按钮最左边的位置小于左边按钮的一半宽度
                    leftButton.move(QPoint(leftButtonPos.x() + widget.width() + spacing, leftButtonPos.y()))
                    # 将当前按钮的的索引与左边按钮的索引交换
                    widget.buttonList[widget.buttonIndex], widget.buttonList[widget.buttonIndex - 1] = widget.buttonList[widget.buttonIndex - 1], widget.buttonList[widget.buttonIndex]
                    # 交换按钮的索引
                    widget.buttonIndex -= 1

def endDrag(widget, event, spacing=10):
    animationDuration = 100
    animationEasingCurve = QEasingCurve.Linear
    # 中键释放后，将按钮的位置依附到相邻的按钮边上
    # 判断要依附的按钮是左边的还是右边的
    if len(widget.buttonList) != 1:
        # 根据button在list中的位置，获取按钮是否在最前面或最后面
        if widget.buttonIndex == 0:  # 如果是第一个按钮
            # 获取右边按钮的位置
            rightButton = widget.buttonList[widget.buttonIndex + 1]
            rightButtonPos = rightButton.pos()
            target_x = rightButtonPos.x() - widget.width() - spacing
            # 将 button 移动到右边按钮的左边
            if target_x - widget.pos().x() > widget.width():
                animationDuration = 1000
                animationEasingCurve = QEasingCurve.OutBounce
        elif widget.buttonIndex == len(widget.buttonList) - 1:  # 如果是最后一个按钮
            # 获取左边按钮的位置
            leftButton = widget.buttonList[widget.buttonIndex - 1]
            leftButtonPos = leftButton.pos()
            # 获取左边按钮的宽度
            leftButtonWidth = leftButton.width()
            # 将 button 移动到左边按钮的右边
            target_x = leftButtonPos.x() + leftButtonWidth + spacing
            if widget.pos().x() - target_x > widget.width():
                animationDuration = 1000
                animationEasingCurve = QEasingCurve.OutBounce
        else:
            animationDuration = 100
            # 根据button在list中的位置，获取左右两个按钮的位置
            leftButton = widget.buttonList[widget.buttonIndex - 1]
            rightButton = widget.buttonList[widget.buttonIndex + 1]
            # 获取 button leftButton rightButton 的位置
            buttonPos = widget.pos()
            leftButtonPos = leftButton.pos()
            rightButtonPos = rightButton.pos()
            # 获取 button leftButton rightButton 的宽度
            buttonWidth = widget.width()
            leftButtonWidth = leftButton.width()
            rightButtonWidth = rightButton.width()
            # 判断 button 与 leftButton 的距离
            distanceToLeftButton = abs(buttonPos.x() - leftButtonPos.x() - leftButtonWidth - spacing)
            # 判断 button 与 rightButton 的距离
            distanceToRightButton = abs(buttonPos.x() + buttonWidth + spacing - rightButtonPos.x())
            # 判断 button 与 leftButton 的距离是否小于 button 与 rightButton 的距离
            if distanceToLeftButton < distanceToRightButton:
                # 将 button 移动到 leftButton 的右边
                target_x = leftButtonPos.x() + leftButtonWidth + spacing
            else:
                # 将 button 移动到 rightButton 的左边
                target_x = rightButtonPos.x() - buttonWidth - spacing
    else:
        target_x = 0
        animationDuration = 1000
        animationEasingCurve = QEasingCurve.OutBounce

    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(animationDuration)
    animation.setEasingCurve(animationEasingCurve)
    animation.setStartValue(widget.pos())
    animation.setEndValue(QPoint(target_x, widget.pos().y()))
    animation.start()
    widget.animation = animation
    # 当动画结束时，更新按钮列表
    widget.animation.finished.connect(partial(updateButtonList, widget))

def updateButtonList(widget):
    # 获取新的按钮列表
    widget.buttonListNew = []
    widgetParentLayout = find_widget_layout(widget)

    for i in range(widgetParentLayout.count()):
        widget.buttonListNew.append(widgetParentLayout.itemAt(i).widget())
    # 如果按钮列表不一样，则说明按钮的位置发生了变化
    if widget.buttonList != widget.buttonListNew:
        # 将layout上的widget全部移除后，重新添加，这样就可以保证按钮的顺序是正确的
        for i in widget.buttonList:
            i.setParent(None)
        for i in widget.buttonList:
            widgetParentLayout.addWidget(i)