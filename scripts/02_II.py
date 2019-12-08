'''
--- Part Two ---
"Good, the new computer seems to be working correctly! Keep it nearby during this mission - you'll probably use it again. Real Intcode computers support many more features than your new one, but we'll let you know what they are as you need them."

"However, your current priority should be to complete your gravity assist around the Moon. For this mission to succeed, we should settle on some terminology for the parts you've already built."

Intcode programs are given as a list of integers; these values are used as the initial state for the computer's memory. When you run an Intcode program, make sure to start by initializing memory to the program's values. A position in memory is called an address (for example, the first value in memory is at "address 0").

Opcodes (like 1, 2, or 99) mark the beginning of an instruction. The values used immediately after an opcode, if any, are called the instruction's parameters. For example, in the instruction 1,2,3,4, 1 is the opcode; 2, 3, and 4 are the parameters. The instruction 99 contains only an opcode and has no parameters.

The address of the current instruction is called the instruction pointer; it starts at 0. After an instruction finishes, the instruction pointer increases by the number of values in the instruction; until you add more instructions to the computer, this is always 4 (1 opcode + 3 parameters) for the add and multiply instructions. (The halt instruction would increase the instruction pointer by 1, but it halts the program instead.)

"With terminology out of the way, we're ready to proceed. To complete the gravity assist, you need to determine what pair of inputs produces the output 19690720."

The inputs should still be provided to the program by replacing the values at addresses 1 and 2, just like before. In this program, the value placed in address 1 is called the noun, and the value placed in address 2 is called the verb. Each of the two input values will be between 0 and 99, inclusive.

Once the program has halted, its output is available at address 0, also just like before. Each time you try a pair of inputs, make sure you first reset the computer's memory to the values in the program (your puzzle input) - in other words, don't reuse memory from a previous attempt.

Find the input noun and verb that cause the program to produce the output 19690720. What is 100 * noun + verb? (For example, if noun=12 and verb=2, the answer would be 1202.)
'''

import sys

class Virtual_Machine:
    
    def __init__(self, int_code, program_alarm=False, noun=12, verb=2):
        self.__int_code = int_code
        self.__is_running = True
        self.__pc = 0
        if program_alarm:
            self.__int_code[1] = noun
            self.__int_code[2] = verb
        
    def is_running(self):
        return self.__is_running
        
    def step(self):
        self.__pc += self.__operate()
        
    def first_position(self):
        first_pos = 0
        return self.__int_code[first_pos]
        
    def __operate(self):
        return \
        {  
            1  : self.__add,
            2  : self.__multiple,
            99 : self.__exit 
        }[self.__int_code[self.__pc]]()
    
    def __add(self):
        arg1_pos = self.__int_code[self.__pc + 1]
        arg2_pos = self.__int_code[self.__pc + 2]
        out = self.__int_code[self.__pc + 3]
        
        self.__int_code[out] = self.__int_code[arg1_pos] + self.__int_code[arg2_pos]
        return 4
    
    def __multiple(self):
        arg1_pos = self.__int_code[self.__pc + 1]
        arg2_pos = self.__int_code[self.__pc + 2]
        out = self.__int_code[self.__pc + 3]
        
        self.__int_code[out] = self.__int_code[arg1_pos] * self.__int_code[arg2_pos]
        return 4
    
    def __exit(self):
        self.__is_running = False
        return 1


def parse_file(file_path : str):
    int_code = []
    with open(file_path, 'r') as f:
        for line in f:
            int_code.extend(map(int, line.split(',')))
    
    return int_code

def main(argv):
    seek_value = 19690720
    for noun in range(100):
        for verb in range(100):
            black_box_mode = True
            vm = Virtual_Machine(parse_file(argv[1]), black_box_mode, noun, verb)
            while (vm.is_running()):
                vm.step()
            
            if vm.first_position() == seek_value:
                print ('For noun={} & verb={} the first Position Value = {}. Sentence is {}'.format(noun, verb, vm.first_position(), 100 * noun + verb))
                print('!!!!! Win !!!!!!')
                break
    print('Seek over')

if __name__ == "__main__":
    sys.exit(main(sys.argv))
