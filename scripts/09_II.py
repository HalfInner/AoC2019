'''--- Part Two ---
It's no good - in this configuration, the amplifiers can't generate a large enough output signal to produce the thrust you'll need. The Elves quickly talk you through rewiring the amplifiers into a feedback loop:

      O-------O  O-------O  O-------O  O-------O  O-------O
0 -+->| Amp A |->| Amp B |->| Amp C |->| Amp D |->| Amp E |-.
   |  O-------O  O-------O  O-------O  O-------O  O-------O |
   |                                                        |
   '--------------------------------------------------------+
                                                            |
                                                            v
                                                     (to thrusters)
Most of the amplifiers are connected as they were before; amplifier A's output is connected to amplifier B's input, and so on. However, the output from amplifier E is now connected into amplifier A's input. This creates the feedback loop: the signal will be sent through the amplifiers many times.

In feedback loop mode, the amplifiers need totally different phase settings: integers from 5 to 9, again each used exactly once. These settings will cause the Amplifier Controller Software to repeatedly take input and produce output many times before halting. Provide each amplifier its phase setting at its first input instruction; all further input/output instructions are for signals.

Don't restart the Amplifier Controller Software on any amplifier during this process. Each one should continue receiving and sending signals until it halts.

All signals sent or received in this process will be between pairs of amplifiers except the very first signal and the very last signal. To start the process, a 0 signal is sent to amplifier A's input exactly once.

Eventually, the software on the amplifiers will halt after they have processed the final loop. When this happens, the last output signal from amplifier E is sent to the thrusters. Your job is to find the largest output signal that can be sent to the thrusters using the new phase settings and feedback loop arrangement.

Here are some example programs:

Max thruster signal 139629729 (from phase setting sequence 9,8,7,6,5):

3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,
27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5
Max thruster signal 18216 (from phase setting sequence 9,7,8,5,6):

3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,
-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,
53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10
Try every combination of the new phase settings on the amplifier feedback loop. What is the highest signal that can be sent to the thrusters?
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
        # if not (0 <= val <= 99):
            # raise Exception('Passed value \'{}\' is not in range [{}, {}]', val, 0, 99)

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
