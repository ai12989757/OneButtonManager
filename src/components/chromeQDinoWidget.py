import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide2.QtCore import QTimer, Qt, QRect
from PySide2.QtGui import QPainter, QColor

class DinoGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小恐龙游戏")
        self.setGeometry(100, 100, 800, 400)
        self.init_game()

    def init_game(self):
        self.dino_y = 300
        self.dino_jump = False
        self.dino_fall = False
        self.jump_height = 100
        self.jump_speed = 20
        self.fall_speed = 20
        self.obstacle_x = 800
        self.obstacle_speed = 10
        self.score = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(30)

        self.setFocusPolicy(Qt.StrongFocus)

    def update_game(self):
        if self.dino_jump:
            self.dino_y -= self.jump_speed
            if self.dino_y <= 300 - self.jump_height:
                self.dino_jump = False
                self.dino_fall = True
        elif self.dino_fall:
            self.dino_y += self.fall_speed
            if self.dino_y >= 300:
                self.dino_y = 300
                self.dino_fall = False

        self.obstacle_x -= self.obstacle_speed
        if self.obstacle_x < 0:
            self.obstacle_x = 800
            self.score += 1

        self.check_collision()
        self.update()

    def check_collision(self):
        if self.obstacle_x < 50 and self.dino_y > 250:
            self.timer.stop()
            self.game_over()

    def game_over(self):
        self.setWindowTitle(f"游戏结束 - 得分: {self.score}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not self.dino_jump and not self.dino_fall:
            self.dino_jump = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawRect(0, 350, 800, 50)  # 地面
        painter.setBrush(QColor(255, 0, 0))
        painter.drawRect(50, self.dino_y, 50, 50)  # 恐龙
        painter.setBrush(QColor(0, 255, 0))
        painter.drawRect(self.obstacle_x, 300, 50, 50)  # 障碍物

if __name__ == "__main__":
    #app = QApplication(sys.argv)
    game = DinoGame()
    game.show()
    #sys.exit(app.exec_())