# -*- coding: utf-8 -*-
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *


# 混合两张图片
def blendTwoImages(image1, image2, size, position = 'left'):
    '''
    args:
        image1: QImage or QPixmap or str
        image2: QImage or QPixmap or str
        size: int 混合后图片的高度/宽度
        position: str 位置 'left', 'right', 'center'
    return:
        QPixmap
    '''
    if isinstance(image1, str):
        image1 = QPixmap(image1)
    if isinstance(image2, str):
        image2 = QPixmap(image2)
    if image1.isNull() or image2.isNull():
        return QImage()
    image1 = QPixmap(image1).scaledToHeight(size, Qt.SmoothTransformation)
    image2 = QPixmap(image2).scaledToHeight(size, Qt.SmoothTransformation)
    painter = QPainter(image1)
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    if position == 'left':
        painter.drawPixmap(0, 0, image2)
    elif position == 'right':
        painter.drawPixmap(image1.width() - image2.width(), 0, image2)
    elif position == 'center':
        painter.drawPixmap((image1.width() - image2.width()) // 2, 0, image2)
    painter.end()
    return image1

# 更改图片的饱和度/亮度/对比度
def enhanceIcon(image, saturation = 1.3, brightness = 1.2):
    '''
    args:
        image: QImage or QPixmap or str
        saturation: float 饱和度
        brightness: float 亮度
    return:
        QPixmap
    '''
    if isinstance(image, str):
        image = QPixmap(image)
        image = image.toImage()
    elif isinstance(image, QPixmap):
        image = image.toImage()
    if not image:
        return None
    # 增加对比度
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            alpha = color.alpha()
            if alpha > 200:
            #if color.red() > 0 or color.green() > 0 or color.blue() > 0:
                # 转换为 HSV
                hsv = color.toHsv()
                h, s, v= hsv.hue(), hsv.saturation(), hsv.value()
                
                # 调整 S 和 V 的值
                s = min(255, int(s * saturation))  # 增加饱和度
                v = min(255, int(v * brightness))  # 增加亮度
                # 转换回 RGB
                enhancedColor = QColor.fromHsv(h, s, v)
                image.setPixelColor(x, y, enhancedColor)
    return QPixmap(image)