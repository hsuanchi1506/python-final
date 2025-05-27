import pygame, random
from player import Player
from maze   import Maze
from dot    import Dot


class Game:
    # TOP_MARGIN = 60  # Scoreboard height
    TOP_MARGIN = 80

    def __init__(self, screen):
        self.screen = screen
        self.sw, self.sh = screen.get_width(), screen.get_height()
        self.bg_color = (33, 47, 60)

        # ---------- Maze (excluding top 60px) ----------
        self.cell = 20
        self.maze = Maze(self.sw // self.cell,
                         (self.sh - self.TOP_MARGIN) // self.cell,
                         self.cell)

        # ---------- Players ----------
        self.players = [
            Player("A", (255,255,0), pygame.K_w,  pygame.K_s,   pygame.K_a, pygame.K_d),
            Player("B", (255,0,0),   pygame.K_UP, pygame.K_DOWN,pygame.K_LEFT, pygame.K_RIGHT),
            Player("C", (0,255,255), pygame.K_i,  pygame.K_k,   pygame.K_j, pygame.K_l),
        ]
        self.players[0].prey = self.players[1]
        self.players[1].prey = self.players[2]
        self.players[2].prey = self.players[0]

        for p, (x, y) in zip(self.players, self.maze.get_valid_positions(3)):
            p.x, p.y = x, y + self.TOP_MARGIN  # Move downward

        # ---------- Dots ----------
        self.dots = []
        self.add_dots(200)
        self.dot_timer, self.dot_intv, self.dot_amt = 0, 600, 10

        # ---------- Game State ----------
        self.game_over = self.paused = False
        self.font = pygame.font.SysFont("Arial", 24)
        self.respawn_delay = 180  # 3s @ 60FPS

        for p in self.players:
            p.speed = self.cell 

    # --------------------------------------------------
    def add_dots(self, n):
        for x, y in self.maze.get_valid_positions(n):
            self.dots.append(Dot(x, y + self.TOP_MARGIN, self.cell // 2))

    # --------------------------------------------------
    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            elif ev.key == pygame.K_r and self.game_over:
                self.__init__(self.screen)
            for p in self.players:
                p.handle_key_down(ev.key)

        elif ev.type == pygame.KEYUP:
            for p in self.players:
                p.handle_key_up(ev.key)

    # --------------------------------------------------
    def update(self):
        if self.paused or self.game_over: return

        # ---- Player Movement ----
        for p in self.players:
            nx, ny = p.calculate_new_position(self.cell, self.maze, self.TOP_MARGIN)
            p.x, p.y = nx, ny

        # ---- Player Eat Player ----
        for p in self.players:
            if not p.alive: continue
            for o in self.players:
                if p is o or not o.alive: continue
                if p.collides_with(o, self.cell):
                    if p.power_mode or o == p.prey:
                        p.score += 15 if p.power_mode else 10
                        o.alive = False
                        o.respawn_timer = self.respawn_delay
                        o.x = o.y = -self.cell
                        o.power_mode = False

        # ---- Eat Dots ----
        for p in self.players:
            if not p.alive: continue
            for d in self.dots[:]:
                if p.collides_with_dot(d):
                    p.score += 5 if d.is_power_pellet else 1
                    if d.is_power_pellet:
                        p.power_mode, p.power_timer = True, 300
                    self.dots.remove(d)

        # ---- Power Mode Countdown ----
        for p in self.players:
            if p.power_mode:
                p.power_timer -= 1
                if p.power_timer <= 0: p.power_mode = False

        # ---- Respawn Countdown ----
        for p in self.players:
            if not p.alive:
                p.respawn_timer -= 1
                if p.respawn_timer <= 0:
                    p.alive = True
                    x, y = self.maze.get_valid_positions(1)[0]
                    p.x, p.y = x, y + self.TOP_MARGIN

        # ---- Dot Spawn Timer ----
        self.dot_timer += 1
        if not self.dots:
            self.add_dots(50); self.dot_timer = 0
        elif self.dot_timer >= self.dot_intv:
            self.add_dots(self.dot_amt); self.dot_timer = 0

    # --------------------------------------------------
    def render(self):
        self.screen.fill(self.bg_color)

        # Draw scoreboard before maze (so maze walls don’t cover it)
        self.draw_scores()
        self.maze.draw(self.screen, offset_y=self.TOP_MARGIN)

        for d in self.dots: d.draw(self.screen)
        for p in self.players: p.draw(self.screen, self.cell)

    # --------------------------------------------------
    # Scoreboard
    # --------------------------------------------------
    def draw_scores(self):
        pad = 6
        col_w = self.sw // len(self.players)

        # --------------------
        # Background gradient & border
        # --------------------
        grad = pygame.Surface((self.sw, self.TOP_MARGIN), pygame.SRCALPHA)
        base_color = (22, 160, 133)
        for y in range(self.TOP_MARGIN):
            grad.fill((*base_color, 230), pygame.Rect(0, y, self.sw, 1))
        self.screen.blit(grad, (0, 0))
        pygame.draw.rect(
            self.screen,
            (247, 220, 111),
            pygame.Rect(0, 0, self.sw, self.TOP_MARGIN),
            width=2,
            border_radius=8
        )

        # --------------------
        # Row 1: predator -> prey and controls
        # --------------------
        y_baseline = 8  # vertical start for icons & keys

        def make_circle_surf(color, radius=8):
            surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (radius, radius), radius)
            return surf

        def make_arrow_surf(width=20, height=16, color=(255,255,255), thickness=6):
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(
                surf,
                color,
                (0, (height-thickness)//2, width-height//2, thickness)
            )
            pygame.draw.polygon(
                surf,
                color,
                [(width-height//2, 0), (width, height//2), (width-height//2, height)]
            )
            return surf

        arrow_surf = make_arrow_surf()
        icon_height = arrow_surf.get_height()  # 16px

        key_layouts = [
            ["W", "A", "S", "D"],
            ["↑", "←", "↓", "→"],
            ["I", "J", "K", "L"],
        ]
        box_w, box_h = 28, 28
        box_gap    = 6
        font_small = pygame.font.SysFont("Arial", 14)

        # center-line for icons and boxes
        icon_center_y = y_baseline + icon_height / 2
        box_y = int(icon_center_y - box_h / 2)

        for i, p in enumerate(self.players):
            x0 = i * col_w + pad

            # draw predator -> prey
            pieces = [
                make_circle_surf(p.color),
                pygame.Surface((6,1), pygame.SRCALPHA),
                arrow_surf,
                pygame.Surface((6,1), pygame.SRCALPHA),
                make_circle_surf(p.prey.color if p.prey else (90,90,90))
            ]
            cur_x = x0
            for piece in pieces:
                self.screen.blit(piece, (cur_x, y_baseline))
                cur_x += piece.get_width()

            cur_x += 6  # small gap before controls

            # draw control keys, horizontally aligned with icons
            for j, key in enumerate(key_layouts[i]):
                bx = cur_x + j * (box_w + box_gap)
                by = box_y
                box_rect = pygame.Rect(bx, by, box_w, box_h)

                pygame.draw.rect(self.screen, (50,50,50), box_rect, border_radius=6)
                pygame.draw.rect(self.screen, p.color, box_rect, width=2, border_radius=6)

                key_surf = font_small.render(key, True, (255,255,255))
                kx = bx + (box_w - key_surf.get_width()) // 2
                ky = by + (box_h - key_surf.get_height()) // 2
                self.screen.blit(key_surf, (kx, ky))

        # --------------------
        # Row 2: player cards (closer margin = 4px)
        # --------------------
        card_h = 26
        content_height = max(icon_height, box_h)
        vertical_margin = 4  # <-- was 8, now 4 for tighter spacing
        base_y = y_baseline + content_height + vertical_margin
        font_score = pygame.font.SysFont("Arial", 18, bold=True)

        for i, p in enumerate(self.players):
            x0 = i * col_w + pad
            card_rect = pygame.Rect(x0, base_y, col_w - 2*pad, card_h)

            pygame.draw.rect(self.screen, (30,30,30,220), card_rect, border_radius=10)
            pygame.draw.rect(self.screen, p.color, card_rect, width=2, border_radius=10)

            # avatar
            pygame.draw.circle(
                self.screen,
                p.color if p.alive else (90,90,90),
                (x0 + 15, base_y + card_h//2),
                10,
                0 if p.alive else 2
            )

            # score
            score_surf = font_score.render(str(p.score), True, (255,255,255))
            self.screen.blit(
                score_surf,
                (x0 + 35, base_y + card_h//2 - score_surf.get_height()//2)
            )

            # extra timer
            extra = ""
            if p.power_mode:
                extra = f"{p.power_timer//60 + 1}s"
            elif not p.alive:
                extra = f"{p.respawn_timer//60 + 1}s"
            if extra:
                color_extra = (255,215,0) if p.power_mode else (200,200,200)
                extra_surf = font_small.render(extra, True, color_extra)
                self.screen.blit(
                    extra_surf,
                    (card_rect.right - extra_surf.get_width() - 6,
                    base_y + card_h//2 - extra_surf.get_height()//2)
                )


