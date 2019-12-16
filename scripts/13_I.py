'''
--- Day 11: Space Police ---
On the way to Jupiter, you're pulled over by the Space Police.

"Attention, unmarked spacecraft! You are in violation of Space Law! All spacecraft must have a clearly visible registration identifier! You have 24 hours to comply or be sent to Space Jail!"

Not wanting to be sent to Space Jail, you radio back to the Elves on Earth for help. Although it takes almost three hours for their reply signal to reach you, they send instructions for how to power up the emergency hull painting robot and even provide a small Intcode program (your puzzle input) that will cause it to paint your ship appropriately.

There's just one problem: you don't have an emergency hull painting robot.

You'll need to build a new emergency hull painting robot. The robot needs to be able to move around on the grid of square panels on the side of your ship, detect the color of its current panel, and paint its current panel black or white. (All of the panels are currently black.)

The Intcode program will serve as the brain of the robot. The program uses input instructions to access the robot's camera: provide 0 if the robot is over a black panel or 1 if the robot is over a white panel. Then, the program will output two values:

First, it will output a value indicating the color to paint the panel the robot is over: 0 means to paint the panel black, and 1 means to paint the panel white.
Second, it will output a value indicating the direction the robot should turn: 0 means it should turn left 90 degrees, and 1 means it should turn right 90 degrees.
After the robot turns, it should always move forward exactly one panel. The robot starts facing up.

The robot will continue running for a while like this and halt when it is finished drawing. Do not restart the Intcode computer inside the robot during this process.

For example, suppose the robot is about to start running. Drawing black panels as ., white panels as #, and the robot pointing the direction it is facing (< ^ > v), the initial state and region near the robot looks like this:

.....
.....
..^..
.....
.....
The panel under the robot (not visible here because a ^ is shown instead) is also black, and so any input instructions at this point should be provided 0. Suppose the robot eventually outputs 1 (paint white) and then 0 (turn left). After taking these actions and moving forward one panel, the region now looks like this:

.....
.....
.<#..
.....
.....
Input instructions should still be provided 0. Next, the robot might output 0 (paint black) and then 0 (turn left):

.....
.....
..#..
.v...
.....
After more outputs (1,0, 1,0):

.....
.....
..^..
.##..
.....
The robot is now back where it started, but because it is now on a white panel, input instructions should be provided 1. After several more outputs (0,1, 1,0, 1,0), the area looks like this:

.....
..<#.
...#.
.##..
.....
Before you deploy the robot, you should probably have an estimate of the area it will cover: specifically, you need to know the number of panels it paints at least once, regardless of color. In the example above, the robot painted 6 panels at least once. (It painted its starting panel twice, but that panel is still only counted once; it also never painted the panel it ended on.)

Build a new emergency hull painting robot and run the Intcode program on it. How many panels does it paint at least once?
'''

import sys
from collections import deque
from itertools import permutations, cycle
from operator import setitem


class VirtualMachine:

    def __init__(self, int_code, program_alarm=False, noun=12, verb=2, debug=False, output_callback=print,
                 input_callback=lambda: input,
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
        self.__debug('  IntCode: \n{}'.format(self.__int_code))
        self.__debug('Is Running {}'.format(self.__is_running))
        self.__debug('        PC {}'.format(self.__pc))
        self.__debug('   LAST PC {}'.format(self.__last_pc))
        self.__debug('  relative {}'.format(self.__relative_base))
        self.__debug('     Steps {}'.format(self.__step_counter))
        self.__debug(' arg modes {}'.format(self.__arg_mode_stack))

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
        self.__current_commnad_number = 0
        self.__x_tile = -1
        self.__y_tile = -1
        self.__id_tile = -1
        self.__board_elements = {}

    def __call__(self, operation=None, **args):
        if operation is None:
            print('Read{}'.format(None), end=' ')
            return None

        if (self.__current_commnad_number % 3) == CarePackager.Parameter_1st:
            self.__x_tile = operation
        elif (self.__current_commnad_number % 3) == CarePackager.Parameter_2nd:
            self.__y_tile = operation
        elif (self.__current_commnad_number % 3) == CarePackager.Parameter_3rd:
            self.__id_tile = operation
            self.__draw()
        else:
            raise Exception('Command number is not used')
        self.__current_commnad_number += 1

    def print(self):
        self.__normalize_board()

    def count_printable_blocks(self):
        return len([el_id for key, el_id in self.__board_elements.items() if el_id == CarePackager.BLOCK_TILE])

    def __normalize_board(self):
        x_max = -1
        y_max = -1
        for x, y in self.__board_elements.keys():
            x_max = max(x_max, x)
            y_max = max(y_max, y)

    def __draw(self):
        print('({};{})={}'.format(self.__x_tile, self.__y_tile, self.__id_tile))
        self.__board_elements[(self.__x_tile, self.__y_tile)] = self.__id_tile

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
    vm = VirtualMachine(parse_file(argv[1]), debug=False,
                        output_callback=cp, input_callback=cp,
                        machine_name='Robot')

    while vm.is_running():
        vm.step()

    print('Printable blocks left: ', cp.count_printable_blocks())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
