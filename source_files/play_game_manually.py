import pygame
from game import SnakeGame, Direction

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def main():

    pygame.init()
    display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = SnakeGame(display)
    state = game.get_state()
    print(state, state.bitstring() + "\n", sep="")

    # game loop
    while not game.game_over:
        # Constantly making an action. If no input from the user, continue to move in the same direction
        # game.play_step(game.direction)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    game.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    game.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    game.direction = Direction.DOWN
                game.play_step(game.direction)
                state = game.get_state()
                print(state, state.bitstring() + "\n", sep="")

    print('Final Score', game.score)


if __name__ == '__main__':
    main()
