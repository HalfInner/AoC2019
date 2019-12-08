'''
--- Part Two ---
The air conditioner comes online! Its cold air feels good for a while, but then the TEST alarms start to go off. Since the air conditioner can't vent its heat anywhere but back into the spacecraft, it's actually making the air inside the ship warmer.

Instead, you'll need to use the TEST to extend the thermal radiators. Fortunately, the diagnostic program (your puzzle input) is already equipped for this. Unfortunately, your Intcode computer is not.

Your computer is only missing a few opcodes:

Opcode 5 is jump-if-true: if the first parameter is non-zero, it sets the instruction pointer to the value from the second parameter. Otherwise, it does nothing.
Opcode 6 is jump-if-false: if the first parameter is zero, it sets the instruction pointer to the value from the second parameter. Otherwise, it does nothing.
Opcode 7 is less than: if the first parameter is less than the second parameter, it stores 1 in the position given by the third parameter. Otherwise, it stores 0.
Opcode 8 is equals: if the first parameter is equal to the second parameter, it stores 1 in the position given by the third parameter. Otherwise, it stores 0.
Like all instructions, these instructions need to support parameter modes as described above.

Normally, after an instruction is finished, the instruction pointer increases by the number of values in that instruction. However, if the instruction modifies the instruction pointer, that value is used and the instruction pointer is not automatically increased.

For example, here are several programs that take one input, compare it to the value 8, and then produce one output:

3,9,8,9,10,9,4,9,99,-1,8 - Using position mode, consider whether the input is equal to 8; output 1 (if it is) or 0 (if it is not).
3,9,7,9,10,9,4,9,99,-1,8 - Using position mode, consider whether the input is less than 8; output 1 (if it is) or 0 (if it is not).
3,3,1108,-1,8,3,4,3,99 - Using immediate mode, consider whether the input is equal to 8; output 1 (if it is) or 0 (if it is not).
3,3,1107,-1,8,3,4,3,99 - Using immediate mode, consider whether the input is less than 8; output 1 (if it is) or 0 (if it is not).
Here are some jump tests that take an input, then output 0 if the input was zero or 1 if the input was non-zero:

3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9 (using position mode)
3,3,1105,-1,9,1101,0,0,12,4,12,99,1 (using immediate mode)
Here's a larger example:

3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99
The above example program uses an input instruction to ask for a single number. The program will then output 999 if the input value is below 8, output 1000 if the input value is equal to 8, or output 1001 if the input value is greater than 8.

This time, when the TEST diagnostic program runs its input instruction to get the ID of the system to test, provide it 5, the ID for the ship's thermal radiator controller. This diagnostic test suite only outputs one number, the diagnostic code.

What is the diagnostic code for system ID 5?
'''

import sys
from collections import deque

class Virtual_Machine:

    def __init__(self, int_code, program_alarm=False, noun=12, verb=2, debug=False):
        self.__debug_mode = debug
        if self.__debug_mode:
            print('Debug Mode...')

        self.__int_code = int_code
        self.__is_running = True
        self.__pc = 0
        self.__last_pc = self.__pc
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
        self.__debug(' IntCode\n {}'.format(self.__int_code))
        self.__debug('Is Running {}'.format(self.__is_running))
        self.__debug('        PC {}'.format(self.__pc))
        self.__debug('   LAST PC {}'.format(self.__last_pc))
        self.__debug('     Steps {}'.format(self.__step_counter))
        self.__debug(' arg modes {}'.format(self.__arg_mode_stack))

    def __operate(self):
        self.__arg_mode_stack.clear()
        opcode = self.__int_code[self.__pc] % 100
        modes = self.__int_code[self.__pc] // 100
        for arg in range(3):
            arg_mode = modes % 10
            modes //= 10
            self.__arg_mode_stack.appendleft(bool(arg_mode))

        self.__debug('O({})'.format(opcode))
        return \
        {
            1  : self.__add,
            2  : self.__multiple,

            3  : self.__input,
            4  : self.__print,

            5  : self.__jmp_if_true,
            6  : self.__jmp_if_false,

            7  : self.__less_than,
            8  : self.__equals,

            99 : self.__exit
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
        val = 0
        try:
            val = int(input())
        except Exception as e:
            self.__debug('Reading input problem. Val={} ErrorMessage={}'.format(val, e))
            pass
        if not (0 <= val <= 99):
            raise Exception('Passed value \'{}\' is not in range [{}, {}]', val, 0, 99)

        self.__write_arg(val)
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

    def __print(self):
        arg1 = self.__read_arg()
        print(arg1, end='')
        return 1

    def __exit(self):
        self.__is_running = False
        return 1

    # Helpers
    def __read_arg(self):
        self.__pc += 1
        if self.__pc >= len(self.__int_code):
            raise Exception('Segmentation fault')

        ret = 0
        if self.__arg_mode_stack.pop():
            ret = self.__int_code[self.__pc]
        else:
            ret = self.__int_code[self.__int_code[self.__pc]]

        return ret

    def __write_arg(self, val):
        self.__pc += 1
        if self.__pc >= len(self.__int_code):
            raise Exception('Segmentation fault')

        if self.__arg_mode_stack.pop():
            self.__int_code[self.__pc] = val
        else:
            self.__int_code[self.__int_code[self.__pc]] = val

    def __debug(self, str):
        if self.__debug_mode:
            print('D:{}'.format(str))

def parse_file(file_path : str):
    int_code = []
    with open(file_path, 'r') as f:
        for line in f:
            int_code.extend(map(int, line.replace('\n', '').split(',')))

    return int_code

def main(argv):
    vm = Virtual_Machine(parse_file(argv[1]), debug=False)
    while (vm.is_running()):
        try:
            vm.step()
        except Exception as e:
            print('E:', e)
            break
    vm.print_debug_info()
    print('First Position Value = {}'.format(vm.first_position()))

if __name__ == "__main__":
    sys.exit(main(sys.argv))

