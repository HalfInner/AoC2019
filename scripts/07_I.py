'''
--- Day 7: Amplification Circuit ---
Based on the navigational maps, you're going to need to send more power to your ship's thrusters to reach Santa in time. To do this, you'll need to configure a series of amplifiers already installed on the ship.

There are five amplifiers connected in series; each one receives an input signal and produces an output signal. They are connected such that the first amplifier's output leads to the second amplifier's input, the second amplifier's output leads to the third amplifier's input, and so on. The first amplifier's input value is 0, and the last amplifier's output leads to your ship's thrusters.

    O-------O  O-------O  O-------O  O-------O  O-------O
0 ->| Amp A |->| Amp B |->| Amp C |->| Amp D |->| Amp E |-> (to thrusters)
    O-------O  O-------O  O-------O  O-------O  O-------O
The Elves have sent you some Amplifier Controller Software (your puzzle input), a program that should run on your existing Intcode computer. Each amplifier will need to run a copy of the program.

When a copy of the program starts running on an amplifier, it will first use an input instruction to ask the amplifier for its current phase setting (an integer from 0 to 4). Each phase setting is used exactly once, but the Elves can't remember which amplifier needs which phase setting.

The program will then call another input instruction to get the amplifier's input signal, compute the correct output signal, and supply it back to the amplifier with an output instruction. (If the amplifier has not yet received an input signal, it waits until one arrives.)

Your job is to find the largest output signal that can be sent to the thrusters by trying every possible combination of phase settings on the amplifiers. Make sure that memory is not shared or reused between copies of the program.

For example, suppose you want to try the phase setting sequence 3,1,2,4,0, which would mean setting amplifier A to phase setting 3, amplifier B to setting 1, C to 2, D to 4, and E to 0. Then, you could determine the output signal that gets sent from amplifier E to the thrusters with the following steps:

Start the copy of the amplifier controller software that will run on amplifier A. At its first input instruction, provide it the amplifier's phase setting, 3. At its second input instruction, provide it the input signal, 0. After some calculations, it will use an output instruction to indicate the amplifier's output signal.
Start the software for amplifier B. Provide it the phase setting (1) and then whatever output signal was produced from amplifier A. It will then produce a new output signal destined for amplifier C.
Start the software for amplifier C, provide the phase setting (2) and the value from amplifier B, then collect its output signal.
Run amplifier D's software, provide the phase setting (4) and input value, and collect its output signal.
Run amplifier E's software, provide the phase setting (0) and input value, and collect its output signal.
The final output signal from amplifier E would be sent to the thrusters. However, this phase setting sequence may not have been the best one; another sequence might have sent a higher signal to the thrusters.

Here are some example programs:

Max thruster signal 43210 (from phase setting sequence 4,3,2,1,0):

3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0
Max thruster signal 54321 (from phase setting sequence 0,1,2,3,4):

3,23,3,24,1002,24,10,24,1002,23,-1,23,
101,5,23,23,1,24,23,23,4,23,99,0,0
Max thruster signal 65210 (from phase setting sequence 1,0,4,3,2):

3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,
1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0
Try every combination of phase settings on the amplifiers. What is the highest signal that can be sent to the thrusters?
'''

import sys
from collections import deque
from itertools import permutations

class Virtual_Machine:

    def __init__(self, int_code, program_alarm=False, noun=12, verb=2, debug=False, output_callback=print, input=[]):
        self.__debug_mode = debug
        self.__debug('Debug Mode...')

        self.__output_callback = output_callback
        self.__pipe_input = input

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
        self.__debug('')
        self.__debug(' IntCode\n {}'.format(self.__int_code))
        self.__debug('Is Running {}'.format(self.__is_running))
        self.__debug('        PC {}'.format(self.__pc))
        self.__debug('   LAST PC {}'.format(self.__last_pc))
        self.__debug('     Steps {}'.format(self.__step_counter))
        self.__debug(' arg modes {}'.format(self.__arg_mode_stack))

    def __operate(self):
        self.__arg_mode_stack.clear()

        modes = self.__int_code[self.__pc] // 100
        for arg in range(4):
            arg_mode = modes % 10
            modes //= 10
            self.__arg_mode_stack.appendleft(bool(arg_mode))

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
        if self.__pipe_input:
            val = int(self.__pipe_input.pop())
        else:
            val = int(input())

        self.__debug('ReadVal={} Buffer={}'.format(val, self.__pipe_input))
        # if not (0 <= val <= 99):
            # raise Exception('Passed value \'{}\' is not in range [{}, {}]', val, 0, 99)

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
        self.__output_callback(arg1, end='')
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


# TODO(HalfsInner): improve desing of this CB
g_queue = []
def cb_get(message, **args):
    # print(message)
    g_queue.append(int(message))

def parse_file(file_path : str):
    int_code = []
    with open(file_path, 'r') as f:
        for line in f:
            int_code.extend(map(int, line.replace('\n', '').replace('\r', '').split(',')))

    return int_code

def main(argv):
    max_output = 0
    max_permuatation = []
    for permutation in permutations(range(5)):
        g_queue.clear()
        for phase_setting in permutation:
            buffer = [phase_setting]
            if g_queue:
                buffer.insert(0, g_queue.pop())
            else:
                buffer.insert(0, 0)
            vm = Virtual_Machine(parse_file(argv[1]), debug=False, output_callback=cb_get, input=buffer)
            while (vm.is_running()):
                try: vm.step()
                except Exception as e:
                    print('E: {}\n{}'.format(e, vm.print_debug_info()))
                    raise
            
            max_output = max(max_output, g_queue[-1])
            # print('Output?', vm.first_position())
        # print('Permutation: ', list(permutation))
        # break
    print('First Position Value = {}, max_output={}'.format(vm.first_position(), max_output))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
