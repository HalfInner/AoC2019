'''
--- Day 13: Care Package ---
As you ponder the solitude of space and the ever-increasing three-hour roundtrip for messages between you and Earth, you notice that the Space Mail Indicator Light is blinking. To help keep you sane, the Elves have sent you a care package.

It's a new game for the ship's arcade cabinet! Unfortunately, the arcade is all the way on the other end of the ship. Surely, it won't be hard to build your own - the care package even comes with schematics.

The arcade cabinet runs Intcode software like the game the Elves sent (your puzzle input). It has a primitive screen capable of drawing square tiles on a grid. The software draws tiles to the screen with output instructions: every three output instructions specify the x position (distance from the left), y position (distance from the top), and tile id. The tile id is interpreted as follows:

0 is an empty tile. No game object appears in this tile.
1 is a wall tile. Walls are indestructible barriers.
2 is a block tile. Blocks can be broken by the ball.
3 is a horizontal paddle tile. The paddle is indestructible.
4 is a ball tile. The ball moves diagonally and bounces off objects.
For example, a sequence of output values like 1,2,3,6,5,4 would draw a horizontal paddle tile (1 tile from the left and 2 tiles from the top) and a ball tile (6 tiles from the left and 5 tiles from the top).

Start the game. How many block tiles are on the screen when the game exits?

Your puzzle answer was 361.

The first half of this puzzle is complete! It provides one gold star: *

--- Part Two ---
The game didn't run because you didn't put in any quarters. Unfortunately, you did not bring any quarters. Memory address 0 represents the number of quarters that have been inserted; set it to 2 to play for free.

The arcade cabinet has a joystick that can move left and right. The software reads the position of the joystick with input instructions:

If the joystick is in the neutral position, provide 0.
If the joystick is tilted to the left, provide -1.
If the joystick is tilted to the right, provide 1.
The arcade cabinet also has a segment display capable of showing a single number that represents the player's current score. When three output instructions specify X=-1, Y=0, the third output instruction is not a tile; the value instead specifies the new score to show in the segment display. For example, a sequence of output values like -1,0,12345 would show 12345 as the player's current score.

Beat the game by breaking all the blocks. What is your score after the last block is broken?
'''

import sys
import os

from collections import deque
from operator import setitem


class VirtualMachine:

    def __init__(self,
                 int_code,
                 program_alarm=False,
                 noun=12, verb=2, quarters=None, debug=False,
                 output_callback=lambda: print, input_callback=lambda: input,
                 machine_name=''):
        self.__debug_mode = debug
        self.__machine_name = machine_name
        self.__debug('Debug Mode... ')

        self.__output_callback = output_callback
        self.__pipe_input_callback = input_callback

        self.__int_code = int_code
        self.__int_code.extend([0] * 10000)  # TODO resize
        self.__is_running = True
        self.__pc = 0
        self.__last_pc = self.__pc
        self.__relative_base = self.__pc
        self.__step_counter = 0
        self.__arg_mode_stack = deque()
        if quarters is not None:
            self.__int_code[0] = quarters

        if program_alarm:
            self.__int_code[1] = noun
            self.__int_code[2] = verb

    def is_running(self):
        return self.__is_running

    def step(self):
        self.__last_pc = self.__pc

        operate_length = self.__operate()

        self.__pc += operate_length
        self.__step_counter += 1

    def first_position(self):
        first_pos = 0
        return self.__int_code[first_pos]

    def print_debug_info(self):
        self.__debug_mode = True
        self.__debug('  IntCode: \n{}'.format(self.__int_code))
        self.__debug('Is Running {}'.format(self.__is_running))
        self.__debug('        PC {}'.format(self.__pc))
        self.__debug('   LAST PC {}'.format(self.__last_pc))
        self.__debug('  relative {}'.format(self.__relative_base))
        self.__debug('     Steps {}'.format(self.__step_counter))
        self.__debug(' arg modes {}'.format(self.__arg_mode_stack))
        self.__debug_mode = False

    def __operate(self):
        self.__arg_mode_stack.clear()

        modes = self.__int_code[self.__pc] // 100
        for arg in range(3):
            arg_mode = modes % 10
            modes //= 10
            self.__arg_mode_stack.appendleft(arg_mode)

        opcode = self.__int_code[self.__pc] % 100
        self.__debug('O({})'.format(opcode))
        return {
            1: self.__add,
            2: self.__multiple,

            3: self.__input,
            4: self.__print,

            5: self.__jmp_if_true,
            6: self.__jmp_if_false,

            7: self.__less_than,
            8: self.__equals,

            9: self.__adjust_relative_base,

            99: self.__exit
        }[opcode]()

    def __add(self):
        arg1 = self.__read_arg()
        arg2 = self.__read_arg()
        self.__write_arg(arg1 + arg2)
        return 1

    def __multiple(self):
        arg1 = self.__read_arg()
        arg2 = self.__read_arg()
        self.__write_arg(arg1 * arg2)
        return 1

    def __input(self):
        val = self.__pipe_input_callback()
        self.__debug('Read: {}'.format(val))

        self.__write_arg(val)
        return 1

    def __print(self):
        arg1 = self.__read_arg()
        self.__output_callback(arg1, end='')
        return 1

    def __jmp_if_true(self):
        arg1 = self.__read_arg()
        jump_pc = self.__read_arg()
        if arg1 != 0:
            self.__pc = jump_pc
            return 0
        return 1

    def __jmp_if_false(self):
        arg1 = self.__read_arg()
        jump_pc = self.__read_arg()
        if arg1 == 0:
            self.__pc = jump_pc
            return 0
        return 1

    def __less_than(self):
        arg1 = self.__read_arg()
        arg2 = self.__read_arg()

        if arg1 < arg2:
            self.__write_arg(1)
        else:
            self.__write_arg(0)
        return 1

    def __equals(self):
        arg1 = self.__read_arg()
        arg2 = self.__read_arg()

        if arg1 == arg2:
            self.__write_arg(1)
        else:
            self.__write_arg(0)
        return 1

    def __adjust_relative_base(self):
        self.__relative_base += self.__read_arg()
        return 1

    def __exit(self):
        self.__is_running = False
        return 1

    # Helpers
    def __read_arg(self):
        self.__pc += 1
        if self.__pc >= len(self.__int_code):
            raise Exception('Segmentation fault')

        return {
            0: lambda: self.__int_code[self.__int_code[self.__pc]],
            1: lambda: self.__int_code[self.__pc],
            2: lambda: self.__int_code[self.__int_code[self.__pc] + self.__relative_base]
        }[self.__arg_mode_stack.pop()]()

    def __write_arg(self, val):
        self.__pc += 1
        if self.__pc >= len(self.__int_code):
            raise Exception('Segmentation fault')

        {
            0: lambda: setitem(self.__int_code, self.__int_code[self.__pc], val),
            1: lambda: setitem(self.__int_code, self.__pc, val),
            2: lambda: setitem(self.__int_code, self.__int_code[self.__pc] + self.__relative_base, val),
        }[self.__arg_mode_stack.pop()]()

    def __debug(self, message):
        if self.__debug_mode:
            print('D_{}:{}'.format(self.__machine_name, message))


def parse_file(file_path: str):
    int_code = []
    with open(file_path, 'r') as f:
        for line in f:
            int_code.extend(map(int, line.replace('\n', '').replace('\r', '').split(',')))

    return int_code


class CarePackager:
    Parameter_1st = 0
    Parameter_2nd = 1
    Parameter_3rd = 2

    BLOCK_EMPTY = 0
    BLOCK_WALL = 1
    BLOCK_TILE = 2
    BLOCK_PADDLE = 3
    BLOCK_BALL = 4

    def __init__(self):
        self.__current_pos = (0, 0)
        self.__current_command_number = 0
        self.__x_tile = -1
        self.__y_tile = -1
        self.__id_tile = -1
        self.__x_ball = 0
        self.__score = 0
        self.__board_elements = {}
        self.__print_queue = deque()
        self.__board_size = (-1, -1)
        self.__board_ready = False
        self.__printable_board = []

    def __call__(self, operation=None, **args):
        if operation is None:
            self.__board_ready = True
            return self.__x_ball - self.__x_paddle

        if (self.__current_command_number % 3) == CarePackager.Parameter_1st:
            self.__x_tile = operation
        elif (self.__current_command_number % 3) == CarePackager.Parameter_2nd:
            self.__y_tile = operation
        elif (self.__current_command_number % 3) == CarePackager.Parameter_3rd:
            self.__id_tile = operation
            self.__draw()
        else:
            raise Exception('Command number is not used')
        self.__current_command_number += 1

    def print(self):
        if not self.__board_ready:
            return [['']]

        self.__normalize_board()
        # [setitem(self.__printable_board[pos[1]], pos[0], self.__tile(tile)) for pos, tile in self.__board_elements.items()]
        [setitem(self.__printable_board[y], x, self.__tile(tile)) for x, y, tile in self.__print_queue]

        return self.__printable_board

    def score(self):
        return self.__score

    def count_printable_blocks(self):
        return len([el_id for key, el_id in self.__board_elements.items() if el_id == CarePackager.BLOCK_TILE])

    def is_ready(self):
        return self.__board_ready

    def __normalize_board(self):
        if not self.__board_size == (-1, -1):
            return

        x_max = -1
        y_max = -1
        for x, y in self.__board_elements.keys():
            x_max = max(x_max, x + 1)
            y_max = max(y_max, y + 1)

        self.__board_size = (x_max, y_max)
        [self.__printable_board.append([' '] * self.__board_size[0]) for _ in range(self.__board_size[1])]
        print('Board size', self.__board_size)

    def __draw(self):
        if self.__x_tile == -1:
            self.__score = self.__id_tile
            return

        if self.__id_tile == CarePackager.BLOCK_BALL:
            self.__x_ball = self.__x_tile

        if self.__id_tile == CarePackager.BLOCK_PADDLE:
            self.__x_paddle = self.__x_tile

        self.__board_elements[(self.__x_tile, self.__y_tile)] = self.__id_tile
        self.__print_queue.append((self.__x_tile, self.__y_tile, self.__id_tile))


    def __tile(self, el_id):
        return {
            CarePackager.BLOCK_EMPTY: ' ',
            CarePackager.BLOCK_WALL: '|',
            CarePackager.BLOCK_TILE: 'o',
            CarePackager.BLOCK_PADDLE: '-',
            CarePackager.BLOCK_BALL: 'x',
        }[el_id]


def main(argv):
    cp = CarePackager()
    vm = VirtualMachine(parse_file(argv[1]), quarters=2, debug=False,
                        output_callback=cp, input_callback=cp,
                        machine_name='Robot')

    print('Loading...')
    is_started_info_printed = True
    while vm.is_running():
        try:
            vm.step()
            # os.system('cls')

            if cp.is_ready():
                if is_started_info_printed:
                    print('Game started...')
                    is_started_info_printed = False
                # os.system('CLS')
                # print('\n'.join([''.join(line) for line in cp.print()]))
                # print('Score: ', cp.score())
        except Exception as e:
            vm.print_debug_info()
            raise e

    print('Printable blocks left: ', cp.count_printable_blocks())
    print('Score: ', cp.score())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
