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


class SignalQueue:

    def __init__(self, queue=[], name='', debug=False):
        self.__queue = []
        self.__queue.extend(queue)
        self.__name = name
        self.__debug_mode_on = debug
        self.__special_input = None

    def __call__(self, message=None, **args):
        self.__debug('{}'.format(self.__queue))
        if message is None:
            if not self.__queue:
                print('{}'.format('In: '), end=' ')
                return self.__special_input() if self.__special_input is not None else int(input())
            return self.__queue.pop()
        self.__debug('->{}'.format(message))
        self.__queue.insert(0, int(message))

    def is_empty(self):
        return len(self.__queue) == 0

    def set_special_input(self, CB):
        self.__special_input = CB

    @property
    def last_output(self):
        return self.__counter

    def __debug(self, message):
        if self.__debug_mode_on:
            print('{}:{}'.format(self.__name, message))


class RouteTracker:
    BLACK = 0
    WHITE = 1
    TURN_RIGHT = 1
    TURN_LEFT = 0

    def __init__(self):
        self.__is_even_step = False
        self.__current_pos = (0, 0)
        self.__panel_counter = 0
        self.__direction = 0
        self.__visited_pos = {}
        self.__after_painting = -1
        self.__idx = 1

    def __call__(self, operation=None, **args):
        if operation is None:
            cur_color = -1
            if self.__visited_pos:
                # 249
                cur_color = RouteTracker.BLACK \
                    if self.__current_pos not in self.__visited_pos.keys() else \
                    self.__visited_pos[self.__current_pos]
            else:
                cur_color = RouteTracker.WHITE
            print('{}'.format(cur_color), end=' ')
            return cur_color

        print('{}'.format(operation), end=' ')
        self.__move_operation(operation) if self.__is_even_step else self.__painting_operation(operation)
        self.__is_even_step = not self.__is_even_step

    @property
    def panel_counter(self):
        return len(self.__visited_pos.keys())

    def print(self):
        min_x, max_x, min_y, max_y = 0, 0, 0, 0
        for idx, position in enumerate(self.__visited_pos.keys()):
            if idx == 0:
                min_x, max_x, min_y, max_y = position[0], position[0], position[1], position[1]
                continue
            min_x = min(min_x, position[0])
            max_x = max(max_x, position[0])
            min_y = min(min_y, position[1])
            max_y = max(max_y, position[1])
        len_x = max_x - min_x + 1
        len_y = max_y - min_y + 1

        table = []
        for idx in range(len_y):
            table.append([' '] * len_x)
        print(self.__visited_pos)
        [setitem(table[(coord[1] - min_y)], (coord[0] - min_x), '#') for coord, color in self.__visited_pos.items() if color == RouteTracker.WHITE]
        print(table)
        print('\n'.join([''.join(row) for row in table]))

    def __painting_operation(self, color):
        self.__visited_pos[self.__current_pos] = color

    def __move_operation(self, direction):
        if direction is RouteTracker.TURN_RIGHT:
            self.__direction += 1
        elif direction is RouteTracker.TURN_LEFT:
            self.__direction += -1
        else:
            raise Exception('Not supported operation Op({})'.format(direction))
        self.__direction %= 4
        {
            0: lambda: self.__move((0, 1)),
            1: lambda: self.__move((1, 0)),
            2: lambda: self.__move((0, -1)),
            3: lambda: self.__move((-1, 0))
        }[self.__direction]()

    def __move(self, vec):
        direction = {
            (0, 1): 'U',
            (1, 0): 'R',
            (0, -1): 'D',
            (-1, 0): 'L'
        }[vec]
        print('{}:{}:{}'.format(self.__current_pos, self.__direction, direction))
        self.__current_pos = (self.__current_pos[0] + vec[0], self.__current_pos[1] + vec[1])


def main(argv):
    rt = RouteTracker()
    vm = VirtualMachine(parse_file(argv[1]), debug=False,
                        output_callback=rt, input_callback=rt,
                        machine_name='Robot')

    # for _ in range(40):
    while vm.is_running():
        vm.step()
    rt.print()
    print('Max_output={}'.format(rt.panel_counter))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
