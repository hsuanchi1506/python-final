import pygame

class BigFruit:
    """地圖上的超大果實──被吃會爆破牆壁"""
    def __init__(self, x, y, radius, blast_cells=3):
        self.x = x          # 像素座標（左上角）
        self.y = y
        self.radius = radius
        self.blast_cells = blast_cells  # 牆壁爆破半徑（格數）
        self.color = (255, 128, 0)      # 橘色
        self.exists = True              # 爆炸後設 False 做動畫用

    def draw(self, screen):
        if not self.exists:
            return
        pygame.draw.circle(screen, self.color,
                           (self.x + self.radius, self.y + self.radius),
                           self.radius)
