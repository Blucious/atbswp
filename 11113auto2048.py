# coding:utf8

import re
import sys
import copy
import math
import random
import pprint
import logging
from selenium import common
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait as By
# from selenium.webdriver.support import expected_conditions as EC


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

fmt = logging.Formatter(fmt='%(levelname)s: %(lineno)d, %(message)s')
stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(fmt)
del fmt
_logger.addHandler(stream)
del stream


class Grid:
    class Direction:
        UP = 1
        DOWN = 2
        LEFT = 3
        RIGHT = 4

    __slots__ = ('_grid', '_sideLen')

    def __init__(self, obj=None):
        """
        :param obj:
            The type decides how to initialize Grid.

            int (default 4): Initialization by length of side
                grid = Grid(5)
            tuple or list: Initialization by tuple or list
                grid = Grid([[0, 2, 0, 0],
                             [0, 0, 0, 0]
                             [0, 0, 2, 0],
                             [0, 0, 0, 0]])
            Grid: Another Grid instance
                grid_a = Grid()
                grid_b = Grid(grid_a)
        """
        _logger.debug('id %d, Grid init with %s' % (id(self), repr(obj)))

        if obj is None:
            obj = 4

        if isinstance(obj, int) and obj >= 4:
            self._grid = [[0] * obj for _ in range(obj)]
        elif isinstance(obj, Grid):
            self._grid = copy.deepcopy(obj._grid)
        elif isinstance(obj, (tuple, list)) \
                and obj and isinstance(obj[0], (tuple, list)) \
                and len(obj) == len(obj[0]) and len(obj) >= 4 and len(obj[0]) >= 4:
            self._grid = [[tile if tile else 0 for tile in row] for row in obj]
        else:
            raise TypeError('invalid type or value, {}'.format(obj))

        self._sideLen = len(self._grid)

    def __setitem__(self, key, value):
        self._grid[key] = value

    def __getitem__(self, item):
        return self._grid[item]

    def __iter__(self):
        return iter(self._grid)

    def __eq__(self, other):
        if not isinstance(other, Grid):
            raise TypeError('Grid is required, got {}'.formaT(other))
        elif self.side_length() != other.side_length():
            raise ValueError('side length not matches')

        for rI in self.iter_by_index():
            if self[rI] != other[rI]:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        lines = []
        for row in self:
            lines.append('` {} `\n'.format(' ` '.join(['{:^4}'.format(cell if cell else '') for cell in row])))
        rowSeparator = '`' * (4 + 4 * self.side_length() + 3 * (self.side_length() - 1)) + '\n'
        return rowSeparator.join([''] + lines + [''])

    def __repr__(self):
        return '<Grid(side_length={}), {}>'.format(self.side_length(), id(self))

    def side_length(self):
        return self._sideLen

    def iter_by_index(self, start=0, stop=None, step=1):
        if stop is None:
            stop = self._sideLen
        return range(start, stop, step)

    @staticmethod
    def evaluate_cells_relation(curr, other):
        if curr > other:
            result = math.log(curr, other)
        else:
            result = math.log(curr, other)
        return result

    def evaluate_grid(self):
        numTiles = 0
        evaluation = 0
        for rowIndex in range(self._sideLen):
            for columnIndex in range(self._sideLen):
                currCell = self._grid[rowIndex][columnIndex]
                if not currCell:
                    continue
                numTiles += 1

                for rI in range(rowIndex - 1, 0 - 1, -1):
                    if self._grid[rI][columnIndex]:
                        evaluation += self.evaluate_cells_relation(currCell, self._grid[rI][columnIndex])
                        break

                for rI in range(rowIndex + 1, self._sideLen):
                    if self._grid[rI][columnIndex]:
                        evaluation += self.evaluate_cells_relation(currCell, self._grid[rI][columnIndex])
                        break

                for cI in range(columnIndex - 1, 0 - 1, -1):
                    if self._grid[rowIndex][cI]:
                        evaluation += self.evaluate_cells_relation(currCell, self._grid[rowIndex][cI])
                        break

                for cI in range(columnIndex + 1, self._sideLen):
                    if self._grid[rowIndex][cI]:
                        evaluation += self.evaluate_cells_relation(currCell, self._grid[rowIndex][cI])
                        break
        assert numTiles != 0  # !!
        return evaluation / numTiles

    def _get_row_by_index(self, row_index, *, reverse=False) -> list:
        sequence = self[row_index].copy()
        if reverse:
            sequence = list(reversed(sequence))
        return sequence

    def _set_row_by_index(self, row_index, sequence, *, reverse=False):
        if len(sequence) != self.side_length():
            raise ValueError('length of side not match, {} is required, got {}'.format(
                self.side_length(), len(sequence)))
        if reverse:
            sequence = reversed(sequence)
        self[row_index] = list(sequence)

    def _get_column_by_index(self, column_index, *, reverse=False) -> list:
        sequence = [self[rI][column_index] for rI in range(self.side_length())]
        if reverse:
            sequence = list(reversed(sequence))
        return sequence

    def _set_column_by_index(self, column_index, sequence, *, reverse=False):
        if len(sequence) != self.side_length():
            raise ValueError('length of side not match, {} is required, got {}'.format(
                self.side_length(), len(sequence)))
        if reverse:
            sequence = list(reversed(sequence))
        for rI in range(self.side_length()):
            self[rI][column_index] = sequence[rI]

    @staticmethod
    def _move_sequence_left(sequence):
        # _logger.debug('call move_sequence_left with {}'.format(sequence))
        seq = sequence.copy()
        k, j = 0, 1
        while j < len(seq):
            if seq[j] != 0:
                if seq[k] == seq[j]:
                    seq[k] *= 2
                    seq[j] = 0
                    k = k + 1
                elif seq[k] == 0:
                    seq[k] = seq[j]
                    seq[j] = 0
                else:
                    seq[k + 1] = seq[j]
                    if k + 1 != j:
                        seq[j] = 0
                    k += 1
            j += 1
        # _logger.debug('move_sequence_left return {}'.format(seq))
        return seq

    def move(self, direction):
        """ Non in-place """
        if not isinstance(direction, int):
            raise TypeError('type int is required, got {}'.format(type(direction)))

        newGrid = Grid(self)

        if direction == Grid.Direction.UP:
            for cI in range(newGrid.side_length()):
                sequence = newGrid._get_column_by_index(cI)
                newGrid._set_column_by_index(cI, newGrid._move_sequence_left(sequence))
        elif direction == Grid.Direction.DOWN:
            for cI in range(newGrid.side_length()):
                sequence = newGrid._get_column_by_index(cI, reverse=True)
                newGrid._set_column_by_index(cI, newGrid._move_sequence_left(sequence), reverse=True)
        elif direction == Grid.Direction.LEFT:
            for rI in range(newGrid.side_length()):
                sequence = newGrid._get_row_by_index(rI)
                newGrid._set_row_by_index(rI, newGrid._move_sequence_left(sequence))
        elif direction == Grid.Direction.RIGHT:
            for rI in range(newGrid.side_length()):
                sequence = newGrid._get_row_by_index(rI, reverse=True)
                newGrid._set_row_by_index(rI, newGrid._move_sequence_left(sequence), reverse=True)
        else:
            raise ValueError('{} is undefined'.format(direction))
        return newGrid

    def get_available_cells(self):
        """ Search for available cells coordinates.
        G.get_available_cells() -> [(x1, y1), (x2, y2) ...]
        """
        cellsAvailable = []
        for rI in range(self.side_length()):
            for cI in range(self.side_length()):
                if not self[rI][cI]:
                    cellsAvailable.append((cI, rI))
        return cellsAvailable

    def add_random_tile(self):
        """ Generate tiles by specified number, In-place. """

        cellsAvailable = self.get_available_cells()

        if cellsAvailable:
            i = random.randrange(0, len(cellsAvailable))
            coordinate = cellsAvailable.pop(i)
            grid[coordinate[1]][coordinate[0]] = 2 if random.random() < 0.9 else 4


# Begin of debug ---------------------------------------
# import os
# grid = Grid([[0, 0, 0, 0],
#              [0, 0, 0, 0],
#              [4, 2, 2, 0],
#              [0, 0, 0, 0]])
# prev = None
# mapping = {'w': Grid.Direction.UP,
#            's': Grid.Direction.DOWN,
#            'a': Grid.Direction.LEFT,
#            'd': Grid.Direction.RIGHT}
# while True:
#     print(grid, flush=True)
#     userInput = None
#     try:
#         userInput = input('w|s|a|d: ')
#         direction = mapping[userInput]
#     except KeyError:
#         if userInput.lower() in ('q', 'quit'):
#             sys.exit()
#         pass
#     grid = grid.move(direction)
#     if not (prev and prev == grid):
#         grid.add_random_tile()
#     prev = Grid(grid)
# End of debug ---------------------------------------


def next_step_getter():
    _stepTuple = (Keys.UP, Keys.RIGHT, Keys.DOWN, Keys.LEFT)
    _index = 0

    def getter():
        nonlocal _index
        _index = (_index + 1) % len(_stepTuple)
        return _stepTuple[_index]
    return getter


class Auto2048:

    tileClassPattern = re.compile(r'^tile tile-(\d+) tile-position-(\d)-(\d).*$')

    def __init__(self):
        self.browser = webdriver.Chrome()  # 'chromedriver.exe' is required

    def run(self):
        try:
            self.browser.get('https://gabrielecirulli.github.io/2048/')

            htmlElem = self.browser.find_element_by_tag_name('html')
            getter = next_step_getter()

            # -------------------- loop --------------------
            while not self.game_over():
                htmlElem.send_keys(getter())
            _logger.info('End of loop')

        except BaseException as err:
            raise err
        finally:
            input('Press any key to quit...')
            self.browser.quit()
            _logger.info('All done.')

    # def get_grid_container(self, side_length=4) -> list:
    #     grid = [[None for _ in range(side_length)] for _ in range(side_length)]
    #     while True:
    #         try:
    #             for tile_divElem in self.browser.find_elements_by_css_selector(
    #                     '[class="tile-container"] > div'):
    #                 match = self.tileClassPattern.match(tile_divElem.get_attribute('class'))
    #                 grid[int(match.group(3)) - 1][int(match.group(2)) - 1] = int(match.group(1))
    #         except common.exceptions.StaleElementReferenceException:
    #             # Prevent the page refresh element does not exsit.
    #             continue
    #         break
    #     _logger.debug('\n{}'.format(pprint.pformat(grid)))
    #     return grid

    def game_over(self) -> bool:
        try:
            self.browser.find_element_by_css_selector('[class*="game-over"]')
        except common.exceptions.NoSuchElementException:
            return False
        return True


if __name__ == '__main__':
    a2 = Auto2048()
    a2.run()
