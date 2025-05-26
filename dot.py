# dot.py — Classic Pac-Man Style Dot Implementation

import pygame

class Dot:
    def __init__(self, x: int, y: int, base_radius: int, power: bool = False):
        """
        Parameters
        ----------
        x, y        : Top-left pixel coordinates (aligned to maze grid)
        base_radius : Half the size of one cell; normal dots will use half of this
        power       : True → power pellet (larger, flashing dot)
        """
        self.x, self.y = x, y
        self.is_power_pellet = power
        self.radius = base_radius if power else base_radius // 2
        self.color = (255, 255, 255)

        # Used for flashing animation of power pellets; not used for normal dots
        self.blink_counter = 0

    # ──────────────────────────────
    def draw(self, screen: pygame.Surface):
        """Draw the dot on screen; power pellets blink every 10 frames"""
        if self.is_power_pellet:
            self.blink_counter += 1
            # Toggle visibility every 10 frames
            if (self.blink_counter // 10) % 2 == 0:
                pygame.draw.circle(
                    screen,
                    self.color,
                    (self.x + self.radius, self.y + self.radius),
                    self.radius,
                )
        else:
            pygame.draw.circle(
                screen,
                self.color,
                (self.x + self.radius * 2, self.y + self.radius * 2),
                self.radius,
            )
