# coding:utf8

import os
import sys
import copy
import random

import enum

if sys.platform == 'win32':
    def _clear():
        os.system('cls')
else:
    def _clear():
        os.system('clear')


class Direction(enum.Enum):
    up = 1
    down = 2
    left = 3
    right = 4


class Game2048:
    # -------------------------- Constants --------------------------
    DIRECTION_MAPPING = {'w': Direction.up, 's': Direction.down,
                         'a': Direction.left, 'd': Direction.right}
    MAXIMUM_SIDE_LENGTH = 20
    MINIMUM_SIDE_LENGTH = 1
    COMMANDS = {}

    # -------------------------- Initialization --------------------------
    def __init__(self, side_length=4, num_tiles=2):
        self.init(side_length, num_tiles)

    def _init_grid_with_side_length(self):
        self._grid = [[0 for _ in self._iter_side()] for _ in self._iter_side()]

    def init(self, side_length, num_tiles=2):
        if side_length is None and hasattr(self, '_sideLength'):
            # Follow the previous length
            pass
        else:
            self._set_side_length(side_length)
        self._init_grid_with_side_length()
        self._init_tiles(num_tiles)

    # -------------------------- Side length --------------------------
    def side_length(self):
        return self._sideLength

    def _set_side_length(self, side_length):
        side_length = int(side_length)
        if not (self.MINIMUM_SIDE_LENGTH <= side_length <= self.MAXIMUM_SIDE_LENGTH):
            raise ValueError('invalid side length')
        self._sideLength = side_length

    # -------------------------- Iteration --------------------------
    def _iter_side(self, start_offset=0, stop_offset=0, reverse=False):
        if reverse:
            return range(self._sideLength - 1 + start_offset,
                         -1 + stop_offset,
                         -1)
        else:
            return range(0 + start_offset,
                         self._sideLength + stop_offset,
                         1)

    def _iter_rows(self):
        return iter(self._grid)

    def __iter__(self):
        return self._iter_rows()

    def __setitem__(self, key, value):
        self._grid[key] = value

    def __getitem__(self, item):
        return self._grid[item]

    # -------------------------- Column & Row operation --------------------------
    def _get_column(self, column_index, reverse=False):
        # [[a, x, x],
        #  [b, x, x],
        #  [c, x, x]]
        # G._get_column(0) -> [a, b, c]
        # G._get_column(0, reverse=True) -> [c, b, a]
        self._check_valid_index(column_index, raise_for_invalid=True)

        seq = []
        for rI in self._iter_side(reverse=reverse):
            seq.append(self[rI][column_index])
        return seq

    def _set_column(self, column_index, seq, reverse=False):
        # [[x, x, x],
        #  [x, x, x],
        #  [x, x, x]]
        # G._set_column(0, [a, b, c])
        # -> [[a, x, x],
        #     [b, x, x],
        #     [c, x, x]]
        # --------------------------------
        # [[x, x, x],
        #  [x, x, x],
        #  [x, x, x]]
        # G._set_column(0, [a, b, c], reverse=True)
        # -> [[c, x, x],
        #     [b, x, x],
        #     [a, x, x]]
        self._check_valid_index(column_index, raise_for_invalid=True)
        self._check_vaild_sequence(seq, raise_for_invalid=True)

        for rI in self._iter_side(reverse=reverse):
            self[rI][column_index] = seq[rI]

    def _get_row(self, row_index, reverse=False):
        self._check_valid_index(row_index, raise_for_invalid=True)

        seq = self[row_index].copy()
        if reverse:
            seq = list(reversed(seq))
        return seq

    def _set_row(self, row_index, seq, reverse=False):
        self._check_valid_index(row_index, raise_for_invalid=True)
        self._check_vaild_sequence(seq, raise_for_invalid=True)

        if reverse:
            seq = list(reversed(seq))
        else:
            seq = seq.copy()
        self[row_index] = seq

    # -------------------------- Check --------------------------
    def _check_valid_side_length(self, side_length, raise_for_invalid=False):
        b = (self.MINIMUM_SIDE_LENGTH <= side_length <= self.MAXIMUM_SIDE_LENGTH)
        if raise_for_invalid and not b:
            raise ValueError('invalid side length {}'.format(side_length))
        return b

    def _check_valid_index(self, index, raise_for_invalid=False) -> bool:
        b = (0 <= index < self._sideLength)
        if raise_for_invalid and not b:
            raise ValueError('invalid column index {}'.format(column_index))
        return b

    @staticmethod
    def _check_vaild_sequence(seq, raise_for_invalid=False) -> bool:
        b = isinstance(seq, (tuple, list))
        if raise_for_invalid and not b:
            raise TypeError('list or tuple is required, got {}'.format(type(seq)))
        return b

    @staticmethod
    def _check_vaild_direction(direction, raise_for_invalid=False):
        b = isinstance(direction, Direction)
        if raise_for_invalid and not b:
            raise TypeError('{} is required, got {}'.format(type(Direction.up), type(direction)))
        return b

    @staticmethod
    def _check_vaild_tile(tile_value, raise_for_invalid=False):
        b = (tile_value != 0b1) and (tile_value & (tile_value - 1) == 0)
        if raise_for_invalid and not b:
            raise TypeError('invalid tile {}'.format(tile_value))
        return b

    def check_game_over(self):
        for rI in self._iter_side():
            if 0 in self[rI]:
                return False
        for i in self._iter_side():
            for j in self._iter_side(stop_offset=-1):
                if self[i][j] == self[i][j + 1] or self[j][i] == self[j + 1][i]:
                    return False
        return True

    # -------------------------- Move --------------------------
    @staticmethod
    def _move_left(seq):
        """ In-place """
        k, j = 0, 1
        length = len(seq)
        while j < length:
            if seq[j] > 0:
                if seq[k] == seq[j]:
                    seq[k] *= 2
                    seq[j] = 0
                    k += 1
                elif seq[k] == 0:
                    seq[k] = seq[j]
                    seq[j] = 0
                else:  # seq[k] != seq[j]
                    seq[k + 1] = seq[j]
                    if j != k + 1:
                        seq[j] = 0
                    k += 1
            j += 1
        return seq

    @staticmethod
    def _move_right(seq):
        """ In-place """
        k, j = len(seq) - 1, len(seq) - 1 - 1
        while j >= 0:
            if seq[j] > 0:
                if seq[k] == seq[j]:
                    seq[k] *= 2
                    seq[j] = 0
                    k -= 1
                elif seq[k] == 0:
                    seq[k] = seq[j]
                    seq[j] = 0
                else:  # seq[k] != seq[j]
                    seq[k - 1] = seq[j]
                    if j != k - 1:
                        seq[j] = 0
                    k -= 1
            j -= 1
        return seq

    def move(self, direction) -> bool:
        self._check_vaild_direction(direction, raise_for_invalid=True)

        backup = str(self._grid)
        if direction == Direction.up:
            for cI in self._iter_side():
                seq = self._get_column(cI)
                self._set_column(cI, self._move_left(seq))
        elif direction == Direction.down:
            for cI in self._iter_side():
                seq = self._get_column(cI)
                self._set_column(cI, self._move_right(seq))
        elif direction == Direction.left:
            for rI in self._iter_side():
                self._move_left(self[rI])  # ISSUE
        elif direction == Direction.right:
            for rI in self._iter_side():
                self._move_right(self[rI])
        else:
            assert False, 'unexpected direction'

        return backup != str(self._grid)

    # -------------------------- Tile --------------------------
    def get_available_moves(self) -> list:
        availableCellsCoord = []
        for rI in self._iter_side():
            for cI in self._iter_side():
                if self[rI][cI] == 0:
                    availableCellsCoord.append((cI, rI))
        return availableCellsCoord

    def _init_tiles(self, num_tiles=2):
        self.new_tile(num_tiles)

    def new_tile(self, num_tiles=1):
        availableCellsCoord = self.get_available_moves()
        for _ in range(num_tiles):
            if availableCellsCoord:
                index = random.randint(0, len(availableCellsCoord) - 1)
                coord = availableCellsCoord.pop(index)
                self[coord[1]][coord[0]] = 2 if random.random() < 0.9 else 4
            else:
                break

    # -------------------------- Commands --------------------------
    def _command_init(self, args, argc, info_list) -> bool:
        if argc != 1:
            info_list.append('init take no arguments (%d given)' % (argc - 1, ))
            return False

        self.init(side_length=None)
        return True

    COMMANDS['init'] = _command_init

    def _command_resize(self, args, argc, info_list) -> bool:
        if argc != 2:
            info_list.append('resize expected at most 1 arguments, got %d' % (argc - 1, ))
            return False

        if not args[1].isdigit():
            info_list.append('%s is not a vaild number' % args[1])
            return False

        sideLength = int(args[1])
        if not self._check_valid_side_length(sideLength):
            info_list.append('the effective range of side length is [%d, %d]' % (
                self.MINIMUM_SIDE_LENGTH, self.MAXIMUM_SIDE_LENGTH))
            return False

        self.init(side_length=sideLength)
        return True

    COMMANDS['resize'] = _command_resize

    def _command_settile(self, args, argc, info_list) -> bool:
        if argc != 4:
            info_list.append('settile expected at most 3 arguments, got %d' % (argc - 1, ))
            return False

        if args[1].isdigit() and args[2].isdigit():
            x = int(args[1])
            y = int(args[2])
            if not (self._check_valid_index(x) and self._check_valid_index(y)):
                info_list.append('(%s, %s) is not a valid coordinate' % (args[1], args[2]))
                return False
        else:
            info_list.append('%s is not a vaild number' % (args[1] if not args[1].isdigit() else args[2]))
            return False

        evalGlobals = {}
        try:
            tileValue = int(eval(args[3], evalGlobals))
        except (BaseException, ) as err:
            info_list.append(str(err))
            return False
        if not self._check_vaild_tile(tileValue):
            info_list.append('%d is not a valid tile value' % tileValue)
            return False

        self[y][x] = tileValue
        return True

    COMMANDS['set'] = _command_settile
    COMMANDS['settile'] = _command_settile

    def _command_help(self, args, argc, info_list) -> bool:
        _clear()
        print("""
help/h                       | Help on this game.
init                         | Start a new game.
resize <side length>         | Start a new game and set side length.
settile/set <x> <y> <value>  | Set the value of the tile.
""")
        input('Press any key to quit: ')
        return True

    COMMANDS['help'] = _command_help
    COMMANDS['h'] = _command_help

    # -------------------------- Main loop --------------------------
    def main_loop(self):
        infoList = []

        try:
            while True:
                # -- Show --
                _clear()
                self.show(infoList)
                infoList.clear()

                # -- Process --
                if self.check_game_over():
                    print('Game Over!')
                    break

                # -- Input --
                try:
                    userInput = input('[w/s/a/d/q/h/<command>]$ ').strip().lower()
                except EOFError:
                    break

                # -- Commands --
                if not userInput:
                    continue
                elif userInput in ('q', 'quit'):
                    break
                elif userInput[:1] in self.DIRECTION_MAPPING and not userInput.strip('wsad'):
                    userInput = userInput[:1]
                    direction = self.DIRECTION_MAPPING[userInput]
                else:
                    args = tuple(userInput.split(' '))
                    argc = len(args)
                    if args[0] in self.COMMANDS:
                        if not self.COMMANDS[args[0]](self, args, argc, infoList):
                            infoList.append('ignore: %s' % ' '.join(args))
                    else:
                        infoList.append('%s: command not found' % args[0])
                    continue

                # -- Process --
                if self.move(direction):
                    self.new_tile()
        except KeyboardInterrupt:
            pass

    # -------------------------- Show --------------------------
    CT_TEMPLATE = '\033[47;30m{{:^{}}}\033[0m'
    CB_TEMPLATE = '\033[46;37m{{:^{}}}\033[0m'

    def _colored(self, item_width, color_type, obj=None, by_length=False, end=''):
        assert isinstance(obj, (int, str, list)) or (obj is None)
        assert isinstance(item_width, int)
        assert isinstance(color_type, str) and (color_type in ('tile', 'border'))
        assert (by_length is True and isinstance(obj, list)) or (by_length is False)

        if color_type == 'tile':
            template = self.CT_TEMPLATE.format(item_width)
        else:
            template = self.CB_TEMPLATE.format(item_width)

        if obj is None:
            obj = ''

        if isinstance(obj, (int, str)):
            result = template.format(obj) + end
        else:
            if by_length:
                result = [template.format('')] * len(obj)
            else:
                result = [template.format(item if item != 0 else '') for item in obj]
        return result

    def _ct(self, item_width, obj=None, by_length=False, end=''):
        """ color tile """
        return self._colored(item_width=item_width,
                             color_type='tile',
                             obj=obj,
                             by_length=by_length,
                             end=end)

    def _cb(self, item_width, obj=None, by_length=False, end=''):
        """ color border """
        return self._colored(item_width=item_width,
                             color_type='border',
                             obj=obj,
                             by_length=by_length,
                             end=end)

    def show(self, info_list):
        lines = []
        for row in self._iter_rows():
            rowTilesListFormatted = self._ct(6, row)
            rowNullStringListFormatted = self._ct(6, row, by_length=True)
            text = self._cb(2) + self._cb(2).join(rowTilesListFormatted) + self._cb(2, end='\n')
            spaces = self._cb(2) + self._cb(2).join(rowNullStringListFormatted) + self._cb(2, end='\n')

            lines.append(spaces + text + spaces)
        separator = self._cb(self.side_length() * (6 + 2) + 2, end='\n')
        print(separator.join([''] + lines + ['']))
        print('\n'.join(info_list))


if __name__ == '__main__':
    g = Game2048()
    g.main_loop()
















