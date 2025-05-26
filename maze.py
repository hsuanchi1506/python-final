import pygame
import random

class Maze:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = self.generate_maze()

    # --------------------------------------------------
    # Generate maze grid with outer walls and random internal walls
    # --------------------------------------------------
    def generate_maze(self):
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # Add outer boundary walls
        for x in range(self.width):
            grid[0][x] = 1
            grid[self.height - 1][x] = 1
        for y in range(self.height):
            grid[y][0] = 1
            grid[y][self.width - 1] = 1

        # Add random internal walls (about 25% of total cells)
        for _ in range(int(self.width * self.height * 0.25)):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            grid[y][x] = 1

        return grid

    # --------------------------------------------------
    # Check if the given grid coordinates are walkable
    # --------------------------------------------------
    def is_valid_position(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.grid[y][x] == 0  # 0 = walkable, 1 = wall

    # --------------------------------------------------
    # Return a list of valid random positions on the maze
    # --------------------------------------------------
    def get_valid_positions(self, count):
        valid = []
        tries, max_try = 0, 1000
        while len(valid) < count and tries < max_try:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.is_valid_position(x, y):
                pos = (x * self.cell_size, y * self.cell_size)
                # Ensure each position is not too close to existing ones (at least 3 cells apart)
                if all(((pos[0]-px)**2 + (pos[1]-py)**2) >= (3 * self.cell_size)**2 for px, py in valid):
                    valid.append(pos)
            tries += 1
        return valid

    # --------------------------------------------------
    # Draw the maze walls to the screen; support vertical offset
    # --------------------------------------------------
    def draw(self, screen, offset_y=0):
        wall_color = (0, 51, 255)
        inner_color = (0, 102, 255)

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size + offset_y,  # Apply vertical offset
                        self.cell_size,
                        self.cell_size
                    )
                    # Draw solid wall block
                    pygame.draw.rect(screen, wall_color, rect)
                    # Rounded corners
                    pygame.draw.rect(screen, wall_color, rect, border_radius=self.cell_size // 4)
                    # Inner highlight
                    pygame.draw.rect(screen, inner_color,
                                     rect.inflate(-2, -2), width=1, border_radius=self.cell_size // 6)

    # --------------------------------------------------
    # Break walls in a square region centered at (cx, cy) with radius r
    # --------------------------------------------------
    def blast_walls(self, cx, cy, r):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                gx, gy = cx + dx, cy + dy
                if 0 <= gx < self.width and 0 <= gy < self.height:
                    self.grid[gy][gx] = 0  # Remove wall
