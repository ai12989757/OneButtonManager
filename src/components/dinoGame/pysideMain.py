# -*- coding: utf-8 -*-
import os, json, random
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

ASSETS_PATH = __file__.replace("pysideMain.py", "Assets/")
FONT = ASSETS_PATH+"Font/Minecraft.ttf"
FONT_FAMILY = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(FONT))[0]

def update_globals(size):
    # Global Constants
    global GOLBAL_SIZE, SCALE_FACTOR, SCREEN_HEIGHT, SCREEN_WIDTH, RUNNING, JUMPING, DUCKING, DEAD, SMALL_CACTUS, LARGE_CACTUS, BIRD, CLOUD, BG
    GOLBAL_SIZE = size # default 300
    SCALE_FACTOR = GOLBAL_SIZE/300

    SCREEN_HEIGHT = GOLBAL_SIZE # default 300
    SCREEN_WIDTH = int(GOLBAL_SIZE*3.3) # default 1100

    # GAME_OVER = QPixmap(ASSETS_PATH+"Other/GameOver.png")
    # RESET = QPixmap(ASSETS_PATH+"Other/Reset.png")

    RUNNING = [QPixmap(ASSETS_PATH+"Dino/DinoRun1.png"),
            QPixmap(ASSETS_PATH+"Dino/DinoRun2.png")]
    JUMPING = QPixmap(ASSETS_PATH+"Dino/DinoJump.png")
    DUCKING = [QPixmap(ASSETS_PATH+"Dino/DinoDuck1.png"),
            QPixmap(ASSETS_PATH+"Dino/DinoDuck2.png")]
    DEAD = QPixmap(ASSETS_PATH+"Dino/DinoDead.png")
    RUNNING = [dino.scaledToHeight(int(dino.height()*SCALE_FACTOR)) for dino in RUNNING]
    JUMPING = JUMPING.scaledToHeight(int(JUMPING.height()*SCALE_FACTOR))
    DUCKING = [dino.scaledToHeight(int(dino.height()*SCALE_FACTOR)) for dino in DUCKING]
    DEAD = DEAD.scaledToHeight(int(DEAD.height()*SCALE_FACTOR))

    SMALL_CACTUS = [QPixmap(ASSETS_PATH+"Cactus/SmallCactus1.png"),
                    QPixmap(ASSETS_PATH+"Cactus/SmallCactus2.png"),
                    QPixmap(ASSETS_PATH+"Cactus/SmallCactus3.png")]
    LARGE_CACTUS = [QPixmap(ASSETS_PATH+"Cactus/LargeCactus1.png"),
                    QPixmap(ASSETS_PATH+"Cactus/LargeCactus2.png"),
                    QPixmap(ASSETS_PATH+"Cactus/LargeCactus3.png")]
    SMALL_CACTUS = [cactus.scaledToHeight(int(cactus.height()*SCALE_FACTOR)) for cactus in SMALL_CACTUS]
    LARGE_CACTUS = [cactus.scaledToHeight(int(cactus.height()*SCALE_FACTOR)) for cactus in LARGE_CACTUS]

    BIRD = [QPixmap(ASSETS_PATH+"Bird/Bird1.png"),
            QPixmap(ASSETS_PATH+"Bird/Bird2.png")]
    BIRD = [bird.scaledToHeight(int(bird.height()*SCALE_FACTOR)) for bird in BIRD]


    CLOUD = QPixmap(ASSETS_PATH+"Other/Cloud.png")
    CLOUD = CLOUD.scaledToHeight(CLOUD.height()*SCALE_FACTOR)

    BG = QPixmap(ASSETS_PATH+"Other/Track.png")
    BG = BG.scaledToHeight(BG.height()*SCALE_FACTOR)

class Dinosaur(QLabel):
    def __init__(self, parent=None):
        super(Dinosaur, self).__init__(parent)
        self.X_POS = int(SCREEN_WIDTH/13.75) # default 80
        self.Y_POS = int(SCREEN_HEIGHT*2.6/4) # default 310
        self.Y_POS_DUCK = int(SCREEN_HEIGHT*3/4) # default 340
        self.JUMP_VEL = SCREEN_HEIGHT/49.4117 # default 8.5
        self.run_images = RUNNING
        self.jump_image = JUMPING
        self.duck_images = DUCKING
        self.dead_image = DEAD
        self.image = self.run_images[0]
        self.setPixmap(self.image)
        self.setGeometry(self.X_POS, self.Y_POS, self.image.width(), self.image.height())
        self.is_jumping = False
        self.is_ducking = False
        self.jump_vel = self.JUMP_VEL
        self.step_index = 0

    def update(self, keys_pressed):
        if self.is_jumping:
            self.jump()
        elif self.is_ducking:
            self.duck()
        else:
            self.run()

        if (Qt.Key_Up in keys_pressed or Qt.Key_W in keys_pressed) and not self.is_jumping:
            self.is_jumping = True
            self.is_ducking = False
        elif (Qt.Key_Down in keys_pressed or Qt.Key_S in keys_pressed) and not self.is_jumping:
            self.is_ducking = True
        elif not (Qt.Key_Down in keys_pressed or Qt.Key_S in keys_pressed or self.is_jumping):
            self.is_ducking = False
            self.is_jumping = False

        self.step_index += 1
        if self.step_index >= 10:
            self.step_index = 0

    def run(self):
        self.image = self.run_images[self.step_index // 5]
        self.setPixmap(self.image)
        self.setGeometry(self.X_POS, self.Y_POS, self.image.width(), self.image.height())

    def duck(self):
        self.image = self.duck_images[self.step_index // 5]
        self.setPixmap(self.image)
        self.setGeometry(self.X_POS, self.Y_POS_DUCK, self.image.width(), self.image.height())

    def jump(self):
        self.image = self.jump_image
        self.setPixmap(self.image)
        if self.is_jumping:
            self.setGeometry(self.X_POS, self.y() - self.jump_vel * 4, self.image.width(), self.image.height())
            self.jump_vel -= self.JUMP_VEL / 12
        if self.jump_vel < -self.JUMP_VEL:
            self.is_jumping = False
            self.jump_vel = self.JUMP_VEL
            self.setGeometry(self.X_POS, self.Y_POS, self.image.width(), self.image.height())

    def die(self):
        self.image = self.dead_image
        self.setPixmap(self.image)
        self.setGeometry(self.X_POS, self.Y_POS, self.image.width(), self.image.height())

class SmallCactus(QLabel):
    def __init__(self, parent=None):
        super(SmallCactus, self).__init__(parent)
        self.x = SCREEN_WIDTH
        self.y = 215*SCALE_FACTOR
        self.images = SMALL_CACTUS
        self.index = random.randint(0, 2)
        self.image = self.images[self.index]
        self.setPixmap(self.image)
        self.setGeometry(self.x, self.y, self.image.width(), self.image.height())

    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.image.width():
            self.index = random.randint(0, 2)
            self.image = self.images[self.index]
            self.setPixmap(self.image)
        self.move(self.x, self.y)

class LargeCactus(QLabel):
    def __init__(self, parent=None):
        super(LargeCactus, self).__init__(parent)
        self.x = SCREEN_WIDTH
        self.y = 190*SCALE_FACTOR
        self.images = LARGE_CACTUS
        self.index = random.randint(0, 2)
        self.image = self.images[self.index]
        self.setPixmap(self.image)
        self.setGeometry(self.x, self.y, self.image.width(), self.image.height())

    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.image.width():
            self.index = random.randint(0, 2)
            self.image = self.images[self.index]
            self.setPixmap(self.image)
        self.move(self.x, self.y)

class Bird(QLabel):
    def __init__(self, parent=None):
        super(Bird, self).__init__(parent)
        self.x = SCREEN_WIDTH
        self.y = int(150*SCALE_FACTOR)
        self.images = BIRD
        self.index = 0
        self.image = self.images[self.index]
        self.setPixmap(self.image)
        self.setGeometry(self.x, self.y, self.image.width(), self.image.height())
        self.frame_count = 0  # 用于记录帧数

    def update(self, game_speed):
        self.x -= game_speed
        self.frame_count += 1
        if self.frame_count % 5 == 0:  # 每隔 5 帧改变一次图标
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]
            self.setPixmap(self.image)
        self.move(self.x, self.y)

class Cloud(QLabel):
    def __init__(self, parent=None):
        super(Cloud, self).__init__(parent)
        self.x = SCREEN_WIDTH + random.randint(0, int(3000*SCALE_FACTOR))
        self.y = random.randint(int(50*SCALE_FACTOR), int(100*SCALE_FACTOR))
        self.image = CLOUD
        self.setPixmap(self.image)
        self.setGeometry(self.x, self.y, self.image.width(), self.image.height())

    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.image.width():
            self.x = SCREEN_WIDTH + random.randint(0, int(3000*SCALE_FACTOR))
            self.y = random.randint(int(50*SCALE_FACTOR), int(150*SCALE_FACTOR))
        self.move(self.x, self.y)

from ...utils import dragWidgetOrder
class ComponentWidget(QWidget):
    def __init__(self,size=300):
        super(ComponentWidget,self).__init__()
        dragWidgetOrder.DragWidgetOrder(self)
        update_globals(size)
        # 设置背景颜色
        self.setAutoFillBackground(True)
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        # 使用 QPalette 设置背景颜色
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        self.setPalette(palette)
        self.x_pos_bg = 0
        self.y_pos_bg = int(270*SCALE_FACTOR) # default 380
        self.game_speed = int(20*SCALE_FACTOR) # default 20
        self.clouds = [Cloud(self) for _ in range(2)]
        self.birds = Bird(self)
        self.smallCactus = SmallCactus(self)
        self.largeCactus = LargeCactus(self)
        self.dinosaur = Dinosaur(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)
        self.current_obstacle = None
        self.obstacle_timer = QTimer(self)
        self.obstacle_timer.timeout.connect(self.spawn_obstacle)
        self.spawn_obstacle()  # 初始化时生成一个障碍物
        self.keys_pressed = set()
        self.game_over = False
        self.show_game_over = True
        self.obstacles = []  # 初始化障碍物列表
        self.score = 0  # 初始化计分器
        self.setFocusPolicy(Qt.StrongFocus) # 设置焦点策略为 StrongFocus, 组织焦点被其他控件抢走
        self.show_start_screen()
        self.menu = QMenu(self)
        self.topScore = 0
        self.docPath = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) + '/OneTools/data/componentsData.json'
        self.componentsData = {}
        if os.path.exists(self.docPath):
            with open(self.docPath, 'r') as f:
                self.componentsData = json.load(f)
        else:
            self.componentsData['Dino'] = 0
            with open(self.docPath, 'w') as f:
                json.dump(self.componentsData, f)
        if 'Dino' in self.componentsData.keys():
            self.topScore = self.componentsData['Dino']

    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))

    def show_start_screen(self):
        self.timer.stop()
        self.obstacle_timer.stop()
        self.start_screen = True
        self.update()

    def start_game(self):
        self.start_screen = False
        self.timer.start(30)
        self.spawn_obstacle()
        self.obstacle_timer.start(random.randint(0, 1000))
        self.update()

    def spawn_obstacle(self):
        if self.current_obstacle is None or self.current_obstacle.x < -self.current_obstacle.width():  # 如果当前没有障碍物或障碍物已经完全离开屏幕
            # 创建一个障碍物列表，排除当前障碍物
            obstacles = [self.smallCactus, self.largeCactus, self.birds]
            if self.current_obstacle in obstacles:
                obstacles.remove(self.current_obstacle)
            
            # 随机选择一个新的障碍物
            self.current_obstacle = random.choice(obstacles)
            self.current_obstacle.x = SCREEN_WIDTH + 100  # 重置障碍物位置
            self.obstacle_timer.start(random.randint(0, 1000))  # 重新设置0~1秒之间的随机时间

    def update_game(self):
        if not self.game_over:
            self.game_speed += 0.01*SCALE_FACTOR
            self.x_pos_bg -= self.game_speed
            
            if self.x_pos_bg <= -BG.width():
                self.x_pos_bg = 0
            for cloud in self.clouds:
                cloud.update(self.game_speed)
            
            # 更新当前障碍物
            if self.current_obstacle:
                self.current_obstacle.update(self.game_speed)
                if self.current_obstacle.x < -self.current_obstacle.width():  # 如果当前障碍物已经完全离开屏幕
                    self.spawn_obstacle()
            
            # 更新恐龙
            self.dinosaur.update(self.keys_pressed)
            # 更新分数
            self.score += 1
            # 碰撞检测
            if self.check_collision():
                self.dinosaur.die()
                self.timer.stop()
                self.obstacle_timer.stop()
                self.game_over = True
                if self.score > self.topScore:
                    self.topScore = self.score
                    self.componentsData['Dino'] = self.topScore
                    with open(self.docPath, 'w') as f:
                        json.dump(self.componentsData, f)
            
        self.update()

    def check_collision(self):
        dino_rect = self.dinosaur.geometry()
        obstacle_rect = self.current_obstacle.geometry()
        return dino_rect.intersects(obstacle_rect)
        
    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
        if self.start_screen and event.key() == Qt.Key_Space:
            self.start_game()
        if self.game_over and event.key() == Qt.Key_Space:
            self.reset_game()
        #event.accept()  # 阻止事件传播到 Maya

    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.key())
        #event.accept()  # 阻止事件传播到 Maya

    def reset_game(self):
        self.score = 0
        self.keys_pressed = set()
        self.game_over = False
        self.show_game_over = True
        self.game_speed = int(20*SCALE_FACTOR) # default 20
        # 去除所有障碍物
        
        self.timer.start(30)
        self.obstacle_timer.start(random.randint(0, 1000))
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        self.setPalette(palette)
        self.dinosaur.run()
        # 将当前障碍物设置为重启后的第一个障碍物
        if self.current_obstacle:
            self.current_obstacle.x = SCREEN_WIDTH + 100
        else:
            self.spawn_obstacle()
        self.update()

    def paintEvent(self, event):
        # 设置圆角
        path = QPainterPath()
        path.addRoundedRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 10, 10) # 设置圆角路径
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
        
        painter = QPainter(self)
        painter.drawPixmap(self.x_pos_bg, self.y_pos_bg, BG)
        painter.drawPixmap(self.x_pos_bg + BG.width(), self.y_pos_bg, BG)

        if self.start_screen:
            # 绘制开始画面
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#ffffff"))
            self.setPalette(palette)
            painter.drawPixmap(self.x_pos_bg, self.y_pos_bg, BG)
            painter.drawPixmap(self.x_pos_bg + BG.width(), self.y_pos_bg, BG)

            # 设置像素风字体
            font = QFont(FONT_FAMILY, int(24 * SCALE_FACTOR))  # 设置字体大小为24
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "Press Space to Start")

        elif self.game_over:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#bdbdbd"))
            self.setPalette(palette)
            # 设置 "GAME OVER" 字体和颜色
            game_over_font = QFont(FONT_FAMILY, int(48 * SCALE_FACTOR))  # 设置字体大小为48
            painter.setFont(game_over_font)
            painter.setPen(Qt.white)  # 设置字体颜色为白色
            painter.drawText(self.rect().adjusted(0, int(-40 * SCALE_FACTOR), 0, 0), Qt.AlignCenter, "GAME OVER")

            # 设置 "Press Space to Restart" 字体和颜色
            restart_font = QFont(FONT_FAMILY, int(12 * SCALE_FACTOR))  # 设置字体大小为12
            painter.setFont(restart_font)
            painter.setPen(Qt.black)  # 设置字体颜色为黑色
            painter.drawText(self.rect().adjusted(0, int(50 * SCALE_FACTOR), 0, 0), Qt.AlignCenter, "Press Space to Restart")

            # 绘制分数
            self.draw_score(painter, restart_font)

            # 绘制最高分
            painter.setFont(restart_font)
            if self.score >= self.topScore:
                painter.setPen('#DC143C')
            else:
                painter.setPen(Qt.black)
            painter.drawText(self.rect().adjusted(0, int(100 * SCALE_FACTOR), 0, 0), Qt.AlignCenter, "TopScore: {}".format(self.topScore))
        else:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#ffffff"))
            self.setPalette(palette)
            self.setGraphicsEffect(None)
            # 绘制分数
            self.draw_score(painter, QFont(FONT_FAMILY, int(12 - (1 / SCALE_FACTOR))))

    def draw_score(self, painter, font):
        painter.setFont(font)
        if self.score >= self.topScore:
            painter.setPen(QColor('#DC143C'))  # 设置分数颜色为淡蓝色
        else:
            painter.setPen(QColor(Qt.black))  # 设置分数颜色为红色
        painter.drawText(self.rect().adjusted(int(-10 * SCALE_FACTOR), int(10 * SCALE_FACTOR), int(-50 * SCALE_FACTOR), int(10 * SCALE_FACTOR)), Qt.AlignTop | Qt.AlignRight, "Score: {}".format(self.score))

if __name__ == "__main__":
    #app = QApplication(sys.argv)
    windsdasdow = MainWindow(size=150)
    windsdasdow.show()
    #sys.exit(app.exec())