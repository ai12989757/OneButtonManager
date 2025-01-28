from PySide2.QtWidgets import QApplication, QWidget, QLabel
from PySide2.QtGui import QPixmap, QPainter, QFont, QFontDatabase, QPalette, QColor
from PySide2.QtCore import QTimer, Qt, QRect, QEvent
import sys
import os
import random

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100

FONT = "D:/git/chromeDinosaur/Assets/Font/Minecraft.ttf"
FONT_FAMILY = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(FONT))[0]

GAME_OVER = QPixmap("d:/git/chromeDinosaur/Assets/Other/GameOver.png")
RESET = QPixmap("d:/git/chromeDinosaur/Assets/Other/Reset.png")

RUNNING = [QPixmap("d:/git/chromeDinosaur/Assets/Dino/DinoRun1.png"),
           QPixmap("d:/git/chromeDinosaur/Assets/Dino/DinoRun2.png")]
JUMPING = QPixmap("d:/git/chromeDinosaur/Assets/Dino/DinoJump.png")
DUCKING = [QPixmap("d:/git/chromeDinosaur/Assets/Dino/DinoDuck1.png"),
           QPixmap("d:/git/chromeDinosaur/Assets/Dino/DinoDuck2.png")]
DEAD = QPixmap("d:/git/chromeDinosaur/Assets/Dino/DinoDead.png")

SMALL_CACTUS = [QPixmap("d:/git/chromeDinosaur/Assets/Cactus/SmallCactus1.png"),
                QPixmap("d:/git/chromeDinosaur/Assets/Cactus/SmallCactus2.png"),
                QPixmap("d:/git/chromeDinosaur/Assets/Cactus/SmallCactus3.png")]
LARGE_CACTUS = [QPixmap("d:/git/chromeDinosaur/Assets/Cactus/LargeCactus1.png"),
                QPixmap("d:/git/chromeDinosaur/Assets/Cactus/LargeCactus2.png"),
                QPixmap("d:/git/chromeDinosaur/Assets/Cactus/LargeCactus3.png")]

BIRD = [QPixmap("d:/git/chromeDinosaur/Assets/Bird/Bird1.png"),
        QPixmap("d:/git/chromeDinosaur/Assets/Bird/Bird2.png")]

CLOUD = QPixmap("d:/git/chromeDinosaur/Assets/Other/Cloud.png")

BG = QPixmap("d:/git/chromeDinosaur/Assets/Other/Track.png")

class Dinosaur(QLabel):
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self, parent=None):
        super().__init__(parent)
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
            self.jump_vel -= 0.8
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
        super().__init__(parent)
        self.x = SCREEN_WIDTH
        self.y = 325
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
        super().__init__(parent)
        self.x = SCREEN_WIDTH
        self.y = 300
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
        super().__init__(parent)
        self.x = SCREEN_WIDTH
        self.y = 250
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
        super().__init__(parent)
        self.x = SCREEN_WIDTH + random.randint(0, 3000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.setPixmap(self.image)
        self.setGeometry(self.x, self.y, self.image.width(), self.image.height())

    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.image.width():
            self.x = SCREEN_WIDTH + random.randint(0, 3000)
            self.y = random.randint(50, 150)
        self.move(self.x, self.y)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chrome Dino Game")
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        # 使用 QPalette 设置背景颜色
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#ffffff"))
        self.setPalette(palette)
        self.x_pos_bg = 0
        self.y_pos_bg = 380
        self.game_speed = 20
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
        self.game_over_timer = QTimer(self)
        self.game_over_timer.timeout.connect(self.toggle_game_over)
        self.game_over_blink_count = 0
        self.obstacles = []  # 初始化障碍物列表
        self.score = 0  # 初始化计分器
        self.setFocusPolicy(Qt.StrongFocus) # 设置焦点策略为 StrongFocus
        self.show()
        self.show_start_screen()

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
            
            # 碰撞检测
            if self.check_collision():
                self.dinosaur.die()
                self.timer.stop()
                self.obstacle_timer.stop()
                self.game_over = True
                self.game_over_timer.start(500)  # 每500毫秒切换一次显示状态
            # 更新分数
            self.score += 1
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
        event.accept()  # 阻止事件传播到 Maya

    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.key())
        event.accept()  # 阻止事件传播到 Maya

    def reset_game(self):
        self.score = 0
        self.keys_pressed = set()
        self.game_over = False
        self.show_game_over = True
        self.game_speed = 20  # 重置游戏速度
        # 去除所有障碍物
        
        self.timer.start(30)
        self.obstacle_timer.start(random.randint(0, 1000))
        self.game_over_timer.stop()
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

    def toggle_game_over(self):
        self.show_game_over = not self.show_game_over
        self.game_over_blink_count += 1
        if self.game_over_blink_count >= 6:  # 闪烁三次后停止
            self.game_over_timer.stop()
            self.show_game_over = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.x_pos_bg, self.y_pos_bg, BG)
        painter.drawPixmap(self.x_pos_bg + BG.width(), self.y_pos_bg, BG)
        
        if self.start_screen:
            # 绘制开始画面
            painter.drawPixmap(self.x_pos_bg, self.y_pos_bg, BG)
            painter.drawPixmap(self.x_pos_bg + BG.width(), self.y_pos_bg, BG)

            # 设置像素风字体
            font = QFont(FONT_FAMILY, 24)  # 设置字体大小为24
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "Press Space to Start")

        elif self.game_over:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor("#bdbdbd"))
            self.setPalette(palette)
            # 设置 "GAME OVER" 字体和颜色
            game_over_font = QFont(FONT_FAMILY, 48)  # 设置字体大小为48
            painter.setFont(game_over_font)
            painter.setPen(Qt.white)  # 设置字体颜色为红色
            painter.drawText(self.rect().adjusted(0, -120, 0, 0), Qt.AlignCenter, "GAME OVER")
            
            # 设置 "Press Space to Restart" 字体和颜色
            restart_font = QFont(FONT_FAMILY, 12)  # 设置字体大小为24
            painter.setFont(restart_font)
            painter.setPen(Qt.black)  # 设置字体颜色为白色
            painter.drawText(self.rect().adjusted(0, 50, 0, 0), Qt.AlignCenter, "Press Space to Restart")

            font = QFont(FONT_FAMILY, 12)
            painter.setFont(font)
            painter.setPen(Qt.black)
            painter.drawText(self.rect().adjusted(-10, 10, -50, 10), Qt.AlignTop | Qt.AlignRight, f"Score: {self.score}")
        else:
            self.setGraphicsEffect(None)
            # 绘制分数
            font = QFont(FONT_FAMILY, 12)
            painter.setFont(font)
            painter.setPen(Qt.black)
            painter.drawText(self.rect().adjusted(-10, 10, -50, 10), Qt.AlignTop | Qt.AlignRight, f"Score: {self.score}")

if __name__ == "__main__":
    #app = QApplication(sys.argv)
    window = MainWindow()
    #sys.exit(app.exec())