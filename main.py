import pygame
import sys
from game import Game
class InvalidKeyError(Exception):
    pass

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

    # Valid keys for all players
    valid_keys = {
        pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d,  # Player A
        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,  # Player B
        pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l  # Player C
    }

    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                try:
                    if event.key not in valid_keys:
                        raise InvalidKeyError(f"Invalid key pressed: {event.key}. Valid keys are: {valid_keys}")
                    game.handle_event(event)
                except InvalidKeyError as e:
                    print(f"Error: {e}")
            else:
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

