import pygame, random
from player import Player
from maze   import Maze
from dot    import Dot
from bigfruit import BigFruit

class Game:
    TOP_MARGIN = 60  # Scoreboard height

    def __init__(self, screen):
        self.screen = screen
        self.sw, self.sh = screen.get_width(), screen.get_height()
        self.bg_color = (0, 0, 0)

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
        h  = self.TOP_MARGIN            # 60 px
        pad = 6                         # inner padding
        col_w = self.sw // len(self.players)

        # ---------- background gradient & border ----------
        grad = pygame.Surface((self.sw, h), pygame.SRCALPHA)
        for y in range(h):
            c = 200 - int(170 * y / h)
            grad.fill((0, 0, c, 230), pygame.Rect(0, y, self.sw, 1))
        self.screen.blit(grad, (0, 0))
        pygame.draw.rect(self.screen, (0, 51, 255),
                         pygame.Rect(0, 0, self.sw, h), width=2, border_radius=8)

        # ---------- line 1: predator → prey ----------
        def make_circle_surf(col, r=8):
            """Return a surface containing a filled circle of given color/radius."""
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, col, (r, r), r)
            return s

        def make_arrow_surf(w=20, h=16, col=(255,255,255), bar_thick=6):
            """
            Draw a short, thick horizontal arrow.
            """
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(
                surf, col,
                (0, (h - bar_thick)//2, w - h//2, bar_thick)  # shorten main bar
            )
            pygame.draw.polygon(
                surf, col,
                [(w - h//2, 0), (w, h//2), (w - h//2, h)]     # triangle head
            )
            return surf

        arrow_srf  = make_arrow_surf()              # shorter arrow
        gap_srf    = pygame.Surface((6, 1), pygame.SRCALPHA)  # 6-px transparent gap

        pieces = []
        for p in self.players:
            pieces += [
                make_circle_surf(p.color),
                gap_srf,          # gap before arrow
                arrow_srf,
                gap_srf,          # gap after arrow
                make_circle_surf(p.prey.color),
                gap_srf           # extra gap between pairs
            ]


        # for p in self.players:
        #     # predator circle
        #     pieces.append(make_circle_surf(p.color))
        #     # arrow
        #     pieces.append(arrow_srf)
        #     # prey circle
        #     pieces.append(make_circle_surf(p.prey.color))
        #     # spacing
        #     pieces.append(space_srf)

        # center all pieces horizontally
        tot_w = sum(s.get_width() for s in pieces)
        cur_x = self.sw // 2 - tot_w // 2
        for srf in pieces:
            self.screen.blit(srf, (cur_x, 4))   # y = 4 px 下緣對齊舊字體
            cur_x += srf.get_width()

        # ---------- line 2: player cards (unchanged) ----------
        card_h   = 26
        base_y   = 30
        score_f  = pygame.font.SysFont("Arial", 18, bold=True)
        small_f  = pygame.font.SysFont("Arial", 14)

        for i, p in enumerate(self.players):
            x0 = i * col_w + pad
            card_rect = pygame.Rect(x0, base_y, col_w - 2 * pad, card_h)
            pygame.draw.rect(self.screen, (30, 30, 30, 220), card_rect, border_radius=10)
            pygame.draw.rect(self.screen, p.color, card_rect, width=2, border_radius=10)

            # avatar
            pygame.draw.circle(
                self.screen,
                p.color if p.alive else (90, 90, 90),
                (x0 + 15, base_y + card_h // 2), 10,
                0 if p.alive else 2
            )

            # score
            sc_txt = score_f.render(str(p.score), True, (255, 255, 255))
            self.screen.blit(sc_txt,
                             (x0 + 35, base_y + card_h // 2 - sc_txt.get_height() // 2))

            # extra seconds (power / respawn)
            extra = ""
            if p.power_mode:
                extra = f"{p.power_timer // 60 + 1}s"
            elif not p.alive:
                extra = f"{p.respawn_timer // 60 + 1}s"
            if extra:
                ext_col = (255, 215, 0) if p.power_mode else (200, 200, 200)
                ex_srf  = small_f.render(extra, True, ext_col)
                self.screen.blit(ex_srf,
                                 (card_rect.right - ex_srf.get_width() - 6,
                                  base_y + card_h // 2 - ex_srf.get_height() // 2))
