# -*- coding: utf-8 -*-
try:
    from PySide2.QtCore import QPropertyAnimation
    from PySide2.QtGui import QColor
    from PySide2.QtWidgets import QGraphicsDropShadowEffect
except:
    from PySide6.QtCore import QPropertyAnimation
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import QGraphicsDropShadowEffect

# 彩色循环描边效果
def colorCycleEffect(widget, interval=4000, alignment='H'):
    '''
    widget : QWidget 需要添加效果的控件
    interval : int 效果变化间隔时间
    alignment : str 描边方向 'H' or 'V' or 'h' or 'v'
    '''
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(QColor(255, 255, 255))
    # 设置描边大小为自身大小的 6%
    if alignment in ['H', 'h']:
        effect.setBlurRadius(widget.height() * 0.2)
    else:
        effect.setBlurRadius(widget.width() * 0.2)
    effect.setOffset(0, 0)
    widget.setGraphicsEffect(effect)
    colorAnimation = QPropertyAnimation(effect, b"color")
    colorAnimation.setStartValue(QColor(127, 179, 213))
    colorAnimation.setKeyValueAt(0.07, QColor(133, 193, 233))
    colorAnimation.setKeyValueAt(0.14, QColor(118, 215, 196))
    colorAnimation.setKeyValueAt(0.21, QColor(115, 198, 182))
    colorAnimation.setKeyValueAt(0.28, QColor(125, 206, 160))
    colorAnimation.setKeyValueAt(0.35, QColor(130, 224, 170))
    colorAnimation.setKeyValueAt(0.42, QColor(247, 220, 111))
    colorAnimation.setKeyValueAt(0.49, QColor(248, 196, 113))
    colorAnimation.setKeyValueAt(0.56, QColor(240, 178, 122))
    colorAnimation.setKeyValueAt(0.63, QColor(229, 152, 102))
    colorAnimation.setKeyValueAt(0.70, QColor(217, 136, 128))
    colorAnimation.setKeyValueAt(0.77, QColor(241, 148, 138))
    colorAnimation.setKeyValueAt(0.84, QColor(195, 155, 211))
    colorAnimation.setKeyValueAt(0.91, QColor(187, 143, 206))
    colorAnimation.setEndValue(QColor(127, 179, 213))
    colorAnimation.setDuration(interval)
    colorAnimation.setLoopCount(-1)
    colorAnimation.start()
    return effect,colorAnimation

def colorSaturate(widget,saturate):
    '''
    widget : QWidget 需要添加效果的控件
    saturate : Float 饱和度
    '''
    pass