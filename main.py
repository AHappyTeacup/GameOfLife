"""Conway's Game of Life

1) LIVE cell > Less than 2 living neighbours > DEAD.
2) LIVE cell > 2 or 3 living neighbours > LIVE
3) LIVE cell > More than 3 living neighbours > DEAD
4) DEAD cell > Exactly 3 living neighbours > LIVE
"""
import itertools
from typing import Set, Tuple


def next_board_state(live_cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """Get a set of living cells on the board, and update the list to the next board state."""
    next_cells = set()

    for live_cell in live_cells:
        # Get the cell's neighbours
        neighbour_set = get_neighbour_set(live_cell)

        # Does this cell continue to live, or does it die?
        if len(neighbour_set.intersection(live_cells)) in [2, 3]:
            next_cells.add(live_cell)

        # For each neighbour of this living cell, get that cell's neighbours and determine if it should come to life.
        for neighbour_cell in neighbour_set:
            # The cell is already alive, or will be coming to life.
            if neighbour_cell in live_cells or neighbour_cell in next_cells:
                pass

            neighbour_neighbour_set = get_neighbour_set(neighbour_cell)
            if len(neighbour_neighbour_set.intersection(live_cells)) == 3:
                next_cells.add(neighbour_cell)

    return next_cells


def get_neighbour_set(cell: [Tuple[int, int]], cell_range: int = 1) -> Set[Tuple[int, int]]:
    """Get the neighbouring cells for a given cell.
    Optional cell_range to look further than the immediate neighbours.
    """
    cell_x, cell_y = cell
    neighbour_set = set(
        itertools.product(
            [cell_x + mod for mod in range(-cell_range, cell_range+1)],
            [cell_y + mod for mod in range(-cell_range, cell_range+1)]
        )
    )
    neighbour_set.remove(cell)
    return neighbour_set

# Now build a pygame visualisation for the algorithm.
import logging
import pygame
import sys

from pygame.locals import *


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='%H:%M')

# initialise pygame
pygame.init()
# Set the display
pygame.display.set_caption('A*.')
display_info = pygame.display.Info()
WINDOWWIDTH = int(display_info.current_w * 4/5)
WINDOWHEIGHT = int(display_info.current_h * 4/5)
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

# Create a clock object and set the Frames Per Second.
FPS = 30
FPSCLOCK = pygame.time.Clock()

# RGB colour chart.
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)

# The pixel length of the Square sides.
SQUARE_SIDE_LENGTH = 15
# The algorithm will update the board state each PyGame tick, which is a bit too fast. Sleep after each updatge.
SLEEP_TIME = 100

GLOBALS = {
    "RunAlg": False,
}


class Square:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.alive = False

    @property
    def width(self):
        if self.alive:
            return 0
        else:
            return 1

    @property
    def colour(self):
        if self.alive:
            return YELLOW
        else:
            return DARKGREEN

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, SQUARE_SIDE_LENGTH, SQUARE_SIDE_LENGTH)

    def draw(self):
        """Draw the Polygon to the screen."""
        pygame.draw.rect(DISPLAYSURF, self.colour, self.rect(), self.width)


class SquareList:
    def __init__(self):
        self.nodes = []
        self.set_squares()

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def __iter__(self) -> Square:
        for row in self.nodes:
            for node in row:
                yield node

    @property
    def live_node_indexes(self) -> Set[Tuple[int, int]]:
        live_node_indexes = set()
        for square_row in self.nodes:
            for square in square_row:
                if square.alive:
                    square.alive = False
                    live_node_indexes.add((square.x // SQUARE_SIDE_LENGTH, square.y // SQUARE_SIDE_LENGTH))
        return live_node_indexes

    def set_squares(self):
        """Create the squares to fill this list."""
        self.nodes = []
        y = 0
        row_num = 0
        while y <= WINDOWHEIGHT:
            self.nodes.append([])

            # x-coordinate, for loop to scroll along the x-axis.
            x = 0
            col_num = 0
            while x <= WINDOWWIDTH:
                # logger.info(f"({row_num=}, {col_num=}): ({x=}, {y=})")
                self.nodes[row_num].append(Square(x, y))
                x += SQUARE_SIDE_LENGTH
                col_num += 1
            row_num += 1
            y += SQUARE_SIDE_LENGTH

    def reset(self):
        """Reset the object."""
        self.set_squares()

    def draw(self):
        """Draw all the squares in this list."""
        for square_row in self.nodes:
            for square in square_row:
                square.draw()


def find_clicked_square(p: tuple, square_list: SquareList) -> Square:
    logger.warning(f"{p=}")
    x, y = p[0], p[1]
    col_num = x // SQUARE_SIDE_LENGTH
    row_num = y // SQUARE_SIDE_LENGTH
    square = square_list[row_num][col_num]
    logger.warning(f"{col_num=} {row_num=}")
    return square


def check_input(square_list):
    """Monitor user input and react accordingly."""
    for event in pygame.event.get():
        # Exit if x is clicked.
        if event.type == QUIT:
            terminate()

        # Gets a mouseclick and coordinates.
        if event.type == pygame.MOUSEBUTTONDOWN:
            position = pygame.mouse.get_pos()
            if not GLOBALS["RunAlg"]:
                square = find_clicked_square(position, square_list)
                square.alive = not square.alive
                pass

        if event.type == KEYDOWN:
            # Enter triggers the pathfinding.
            if not GLOBALS["RunAlg"]:
                if event.key == K_RETURN:
                    logger.warning("Running Algorithm")
                    GLOBALS["RunAlg"] = True

                elif event.key == K_BACKSPACE:
                    logger.warning("Restarting")
                    square_list.reset()
                    GLOBALS["isFinished"] = False

            elif event.key in [K_RETURN, K_BACKSPACE]:
                logger.warning("Stopping Algorithm")
                GLOBALS["RunAlg"] = False

            # Sets escape to end game.
            if event.key == K_ESCAPE:
                terminate()


def terminate():
    """Terminate the program."""
    pygame.quit()
    sys.exit()


def main():
    square_list = SquareList()

    while True:
        # Clear screen and delay if screen is refreshing too fast.
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        # Set the background colour to black.
        DISPLAYSURF.fill(BLACK)

        # Tessellate the screen with squares.
        square_list.draw()

        check_input(square_list)

        if GLOBALS["RunAlg"]:
            pygame.time.delay(SLEEP_TIME)
            new_live_cells = next_board_state(square_list.live_node_indexes)
            for new_live_cell in new_live_cells:
                new_live_cell_x, new_live_cell_y = new_live_cell
                if new_live_cell_y in range(len(square_list)):
                    if new_live_cell_x in range(len(square_list[new_live_cell_y])):
                        square_list[new_live_cell_y][new_live_cell_x].alive = True


if __name__ == '__main__':
    main()
