"""
What we want:
-This class has a game interface. When you pass in a move, the game plays that move.
 Otherwise, the game is frozen
-Also should have a function get_state()
-i.e SnakeGame takes in a display for where to play out a game, where we pass in moves one at a time

"""

import pygame
import random
from enum import Enum
from collections import namedtuple

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Represents a state in the game. Can be thought of as composed of multiple features, each True or False
# Note 1: ** This may be an indirect way of defining basis functions ? ** - reflect later
# Note 2: Do we need to consider direction snake is moving in? Maybe not
class State:

    def __init__(self, bitstring="00000000000000"):
        # Values need to be corrected afterwards
        self.snake_moving_right = (bitstring[0] == "1")
        self.snake_moving_left = (bitstring[1] == "1")
        self.snake_moving_up = (bitstring[2] == "1")
        self.snake_moving_down = (bitstring[3] == "1")
        self.danger_right = (bitstring[4] == "1")
        self.danger_left = (bitstring[5] == "1")
        self.danger_up = (bitstring[6] == "1")
        self.danger_down = (bitstring[7] == "1")
        self.food_right = (bitstring[8] == "1")
        self.food_left = (bitstring[9] == "1")
        self.food_up = (bitstring[10] == "1")
        self.food_down = (bitstring[11] == "1")
        self.food_adjacent = (bitstring[12] == "1")
        self.hungry = (bitstring[13] == "1")

    def bitstring(self):
        return str(int(self.snake_moving_right)) + str(int(self.snake_moving_left)) + \
               str(int(self.snake_moving_up)) + str(int(self.snake_moving_down)) + \
               str(int(self.danger_right)) + str(int(self.danger_left)) + str(int(self.danger_up)) + \
               str(int(self.danger_down)) + str(int(self.food_right)) + str(int(self.food_left)) + \
               str(int(self.food_up)) + str(int(self.food_down)) + str(int(self.food_adjacent)) + \
               str(int(self.hungry))

    # For debugging purposes
    def __str__(self):
        string = "State:\n"
        string += "Snake moving right: " + str(self.snake_moving_right) + "\n"
        string += "Snake moving left: " + str(self.snake_moving_left) + "\n"
        string += "Snake moving up: " + str(self.snake_moving_up) + "\n"
        string += "Snake moving down: " + str(self.snake_moving_down) + "\n"
        string += "Danger right: " + str(self.danger_right) + "\n"
        string += "Danger left: " + str(self.danger_left) + "\n"
        string += "Danger up: " + str(self.danger_up) + "\n"
        string += "Danger down: " + str(self.danger_down) + "\n"
        string += "Food right: " + str(self.food_right) + "\n"
        string += "Food left: " + str(self.food_left) + "\n"
        string += "Food up: " + str(self.food_up) + "\n"
        string += "Food down: " + str(self.food_down) + "\n"
        string += "Food adjacent: " + str(self.food_adjacent) + "\n"
        string += "Hungry: " + str(self.hungry) + "\n"
        return string

class SnakeGame:

    def __init__(self, display, w=640, h=480, speed=20):
        pygame.init()
        self.font = pygame.font.SysFont('arial', 25)
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.speed = speed

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.turns_since_last_ate = 0

        self.game_over = False
        self._update_ui()

    def get_state(self):
        state = State()

        if self.direction == Direction.RIGHT:
            state.snake_moving_right = True
        elif self.direction == Direction.LEFT:
            state.snake_moving_left = True
        elif self.direction == Direction.DOWN:
            state.snake_moving_down = True
        elif self.direction == Direction.UP:
            state.snake_moving_up = True

        if self._is_obstacle(self.head.x - BLOCK_SIZE, self.head.y):
            state.danger_left = True
        if self._is_obstacle(self.head.x + BLOCK_SIZE, self.head.y):
            state.danger_right = True
        if self._is_obstacle(self.head.x, self.head.y - BLOCK_SIZE):
            state.danger_up = True
        if self._is_obstacle(self.head.x, self.head.y + BLOCK_SIZE):
            state.danger_down = True

        if self.head.x > self.food.x:
            state.food_left = True
        if self.head.x < self.food.x:
            state.food_right = True
        if self.head.y > self.food.y:
            state.food_up = True
        if self.head.y < self.food.y:
            state.food_down = True

        if (self.head.x + BLOCK_SIZE, self.head.y) == (self.food.x, self.food.y) or \
                (self.head.x - BLOCK_SIZE, self.head.y) == (self.food.x, self.food.y) or \
                (self.head.x, self.head.y + BLOCK_SIZE) == (self.food.x, self.food.y) or \
                (self.head.x, self.head.y - BLOCK_SIZE) == (self.food.x, self.food.y):
            state.food_adjacent = True

        if self.turns_since_last_ate > 50:
            state.hungry = True

        return state

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    # 4 possible actions - Move left, right, up or down. Can pass in either a string or a Direction instance
    def play_step(self, action):

        if self.game_over:
            return

        # Check if action passed in is a string or Direction instance
        if isinstance(action, Direction):
            self.direction = Direction(action)
        else:
            possible_actions = ["right", "left", "up", "down"]
            if action not in possible_actions:
                return
            # Update direction based on the action
            direction_enum_value = possible_actions.index(action) + 1
            self.direction = Direction(direction_enum_value)
        self._move()

        # Check if game over
        if self._is_collision():
            self.game_over = True
            return

        # Place new food item if at food tile
        if self.head == self.food:
            self.score += 1
            self._place_food()
            self.turns_since_last_ate = 0
        # if snake didn't eat a food item, need to call pop so size maintained
        else:
            self.snake.pop()
            self.turns_since_last_ate += 1

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)

    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        # hits itself
        if self.head in self.snake[1:]:
            return True
        return False

    # An obstacle is either a block making up the snake body or a boundary
    def _is_obstacle(self, x_pos, y_pos):

        # Check if position is out of bounds
        if x_pos > self.w - BLOCK_SIZE or x_pos < 0 or y_pos > self.h - BLOCK_SIZE or y_pos < 0:
            return True

        # Check if position occupied by a snake body part
        for point in self.snake:
            if (x_pos == point.x) and (y_pos == point.y):
                return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = self.font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    # Move snake using the current direction
    def _move(self):
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)
        self.snake.insert(0, self.head)

