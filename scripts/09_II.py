'''
--- Day 9: Sensor Boost ---
You've just said goodbye to the rebooted rover and left Mars when you receive a faint distress signal coming from the asteroid belt. It must be the Ceres monitoring station!

In order to lock on to the signal, you'll need to boost your sensors. The Elves send up the latest BOOST program - Basic Operation Of System Test.

While BOOST (your puzzle input) is capable of boosting your sensors, for tenuous safety reasons, it refuses to do so until the computer it runs on passes some checks to demonstrate it is a complete Intcode computer.

Your existing Intcode computer is missing one key feature: it needs support for parameters in relative mode.

Parameters in mode 2, relative mode, behave very similarly to parameters in position mode: the parameter is interpreted as a position. Like position mode, parameters in relative mode can be read from or written to.

The important difference is that relative mode parameters don't count from address 0. Instead, they count from a value called the relative base. The relative base starts at 0.

The address a relative mode parameter refers to is itself plus the current relative base. When the relative base is 0, relative mode parameters and position mode parameters with the same value refer to the same address.

For example, given a relative base of 50, a relative mode parameter of -7 refers to memory address 50 + -7 = 43.

The relative base is modified with the relative base offset instruction:

Opcode 9 adjusts the relative base by the value of its only parameter. The relative base increases (or decreases, if the value is negative) by the value of the parameter.
For example, if the relative base is 2000, then after the instruction 109,19, the relative base would be 2019. If the next instruction were 204,-34, then the value at address 1985 would be output.

Your Intcode computer will also need a few other capabilities:

The computer's available memory should be much larger than the initial program. Memory beyond the initial program starts with the value 0 and can be read or written like any other memory. (It is invalid to try to access memory at a negative address, though.)
The computer should have support for large numbers. Some instructions near the beginning of the BOOST program will verify this capability.
Here are some example programs that use these features:

109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99 takes no input and produces a copy of itself as output.
1102,34915192,34915192,7,4,7,99,0 should output a 16-digit number.
104,1125899906842624,99 should output the large number in the middle.
The BOOST program will ask for a single input; run it in test mode by providing it the value 1. It will perform a series of checks on each opcode, output any opcodes (and the associated parameter modes) that seem to be functioning incorrectly, and finally output a BOOST keycode.

Once your Intcode computer is fully functional, the BOOST program should report no malfunctioning opcodes when run in test mode; it should only output a single value, the BOOST keycode. What BOOST keycode does it produce?

Your puzzle answer was 3507134798.

--- Part Two ---
You now have a complete Intcode computer.

Finally, you can lock on to the Ceres distress signal! You just need to boost your sensors using the BOOST program.

The program runs in sensor boost mode by providing the input instruction the value 2. Once run, it will boost the sensors automatically, but it might take a few seconds to complete the operation on slower hardware. In sensor boost mode, the program will output a single value: the coordinates of the distress signal.

Run the BOOST program in sensor boost mode. What are the coordinates of the distress signal?
'''

import sys
from collections import deque
from itertools import permutations, cycle
from operator import setitem

class Virtual_Machine:

    def __init__(self, int_code, program_alarm=False, noun=12, verb=2, debug=False, output_callback=print, input=[], machine_name=''):
        self.__debug_mode = debug
        self.__machine_name = machine_name
        self.__debug('Debug Mode... ')

        self.__output_callback = output_callback
        self.__pipe_input = input

        self.__int_code = int_code
        self.__int_code.extend([0] * 10000) # TODO resize
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
        self.__debug('')
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
            1  : self.__add,
            2  : self.__multiple,

            3  : self.__input,
            4  : self.__print,

            5  : self.__jmp_if_true,
            6  : self.__jmp_if_false,

            7  : self.__less_than,
            8  : self.__equals,
            
            9  : self.__adjust_relative_base,

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
        if self.__pipe_input: # Todo add lambda
            val = int(self.__pipe_input.pop())
        else:
            print('Pass value:', end='')
            val = int(input())

        self.__debug('ReadVal={} Buffer={}'.format(val, self.__pipe_input))

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
            0: lambda : self.__int_code[self.__int_code[self.__pc]],
            1: lambda : self.__int_code[self.__pc],
            2: lambda : self.__int_code[self.__int_code[self.__pc] + self.__relative_base]
        }[self.__arg_mode_stack.pop()]()
        

    def __write_arg(self, val):
        self.__pc += 1
        if self.__pc >= len(self.__int_code):
            raise Exception('Segmentation fault')

        {
            0 : lambda : setitem(self.__int_code, self.__int_code[self.__pc], val),
            1 : lambda : setitem(self.__int_code, self.__pc, val),
            2 : lambda : setitem(self.__int_code, self.__int_code[self.__pc] + self.__relative_base, val),
        }[self.__arg_mode_stack.pop()]()
            

    def __debug(self, message):
        if self.__debug_mode:
            print('D_{}:{}'.format(self.__machine_name, message))


# TODO(HalfsInner): improve desing of this CB
g_queue = []
def cb_get(message, **args):
    print(message)
    g_queue.append(int(message))

def parse_file(file_path : str):
    int_code = []
    with open(file_path, 'r') as f:
        for line in f:
            int_code.extend(map(int, line.replace('\n', '').replace('\r', '').split(',')))

    return int_code

def parse_file(file_path : str):
    int_code = []
    with open(file_path, 'r') as f:
        for line in f:
            int_code.extend(map(int, line.replace('\n', '').replace('\r', '').split(',')))

    return int_code
    

class SignalQueue: 
    g_move = False
    g_counter = 0
    g_max = 0
    
    def __init__(self, queue=[], name=''):
        self.__queue = []
        self.__queue.extend(queue)
        self.__name = name       
    
    def __call__(self, message, **args):
        print('{}'.format(message), end=' ')
        self.__queue.insert(0, int(message))
        SignalQueue.g_move = True
        SignalQueue.g_max = max(SignalQueue.g_max, int(message))

        
    def get_queue(self):
        return self.__queue


def main(argv):
    sq = SignalQueue([], 'SQ')
    vm = Virtual_Machine(parse_file(argv[1]), debug=True, output_callback=sq, machine_name='MySuperiorMachine')
    while vm.is_running():
        vm.step()
        
    print('Max_output={}'.format(SignalQueue.g_max))
        

if __name__ == "__main__":
    sys.exit(main(sys.argv))
