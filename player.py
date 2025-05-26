import pygame
import math

class Player:
    def __init__(self, player_id, color, key_up, key_down, key_left, key_right):
        self.id = player_id
        self.color = color
        self.original_color = color  # For power mode flashing
        self.x = self.y = 0
        self.speed = 2
        self.score = 0
        self.prey = None  # Assigned later by the Game
        self.power_mode = False
        self.power_timer = 0
        self.alive = True
        self.respawn_timer = 0

        # Movement keys
        self.key_up, self.key_down = key_up, key_down
        self.key_left, self.key_right = key_left, key_right

        # Current direction (-1/0/1 for x and y)
        self.direction_x = self.direction_y = 0

        # Last non-zero direction (used for drawing mouth direction)
        self.last_dir_x = 1  # Default facing right
        self.last_dir_y = 0

        # Movement cooldown (how many frames to wait before moving again)
        self.move_cooldown = 0
        self.MOVE_COOLDOWN = 6

    # -------------------------------
    # Keyboard event handlers
    # -------------------------------
    def handle_key_down(self, key):
        if key == self.key_up:
            self.direction_x, self.direction_y = 0, -1
        elif key == self.key_down:
            self.direction_x, self.direction_y = 0, 1
        elif key == self.key_left:
            self.direction_x, self.direction_y = -1, 0
        elif key == self.key_right:
            self.direction_x, self.direction_y = 1, 0
        else:
            return
        self.last_dir_x, self.last_dir_y = self.direction_x, self.direction_y

    def handle_key_up(self, key):
        if key in (self.key_up, self.key_down):
            self.direction_y = 0
        elif key in (self.key_left, self.key_right):
            self.direction_x = 0

    # -------------------------------
    # Compute next position
    # -------------------------------
    def calculate_new_position(self, cell, maze, top_margin):
        if not self.alive or (self.direction_x == 0 and self.direction_y == 0):
            return self.x, self.y

        # Wait for cooldown if necessary
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return self.x, self.y

        # Move by one cell in the given direction
        step_x = self.direction_x * cell
        step_y = self.direction_y * cell
        nx, ny = self.x + step_x, self.y + step_y

        # Clamp to screen boundaries
        max_x = pygame.display.get_surface().get_width() - cell
        max_y = pygame.display.get_surface().get_height() - cell
        nx = max(0, min(nx, max_x))
        ny = max(top_margin, min(ny, max_y))

        # Check for wall collisions (adjust y by top_margin for grid index)
        for cx, cy in [(nx, ny), (nx + cell - 1, ny),
                       (nx, ny + cell - 1), (nx + cell - 1, ny + cell - 1)]:
            gx, gy = int(cx // cell), int((cy - top_margin) // cell)
            if not maze.is_valid_position(gx, gy):
                return self.x, self.y  # Movement blocked by wall

        # Movement successful, reset cooldown
        self.move_cooldown = self.MOVE_COOLDOWN
        return nx, ny

    # -------------------------------
    # Collision detection
    # -------------------------------
    def collides_with(self, other, cell):
        if not self.alive or not other.alive:
            return False
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 < (cell // 2) ** 2

    def collides_with_dot(self, dot):
        if not self.alive:
            return False
        return (self.x + dot.radius - dot.x) ** 2 + (self.y + dot.radius - dot.y) ** 2 < (dot.radius * 2) ** 2

    # -------------------------------
    # Drawing the player on screen
    # -------------------------------
    def draw(self, screen, cell):
        radius = cell // 2
        center = (self.x + radius, self.y + radius)

        # Flash white if in power mode
        draw_col = (255, 255, 255) if self.power_mode and (self.power_timer // 5) % 2 == 0 else self.color

        # Use current direction or last known direction if not moving
        dx = self.direction_x if self.direction_x else self.last_dir_x
        dy = self.direction_y if self.direction_y else self.last_dir_y

        # Determine mouth direction
        if dx == 1:
            start_angle, end_angle = 30, 330  # Right
        elif dx == -1:
            start_angle, end_angle = 210, 150  # Left
        elif dy == -1:
            start_angle, end_angle = 120, 60  # Up
        elif dy == 1:
            start_angle, end_angle = 300, 240  # Down
        else:
            start_angle, end_angle = 30, 330  # Default right

        # Animate mouth opening/closing
        mouth_speed, mouth_var = 3, 20
        off = mouth_var * ((pygame.time.get_ticks() // 100) % mouth_speed) / mouth_speed
        start_angle += off
        end_angle -= off

        # Draw Pac-Man body with arc mouth
        pygame.draw.arc(screen, draw_col, (self.x, self.y, cell, cell),
                        math.radians(start_angle), math.radians(end_angle), radius)

        # Draw inner circle for eye / ID background
        pygame.draw.circle(screen, (50, 50, 50), center, radius // 3)

        # Render and draw player ID at center
        txt = pygame.font.SysFont('Arial', 12).render(self.id, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=center))
