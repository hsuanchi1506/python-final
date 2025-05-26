import pygame
import sys
from game import Game

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("3-Player Pac-Man")
    
    # Create game instance
    game = Game(screen)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        
        # Update game state
        game.update()
        
        # Render the game
        game.render()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

