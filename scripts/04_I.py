'''
--- Day 4: Secure Container ---
You arrive at the Venus fuel depot only to discover it's protected by a password. The Elves had written the password on a sticky note, but someone threw it out.

However, they do remember a few key facts about the password:

It is a six-digit number.
The value is within the range given in your puzzle input.
Two adjacent digits are the same (like 22 in 122345).
Going from left to right, the digits never decrease; they only ever increase or stay the same (like 111123 or 135679).
Other than the range rule, the following are true:

111111 meets these criteria (double 11, never decreases).
223450 does not meet these criteria (decreasing pair of digits 50).
123789 does not meet these criteria (no double).
How many different passwords within the range given in your puzzle input meet these criteria?
'''

import sys
import math

def is_avaible(password):
    is_satisfy_digit = password.isdigit()
    
    is_satisfy_length = len(password) == 6
    
    is_satisfy_double = False
    for idx in range(len(password) - 1):
        if password[idx] == password[idx + 1]:
            is_satisfy_double = True
            break
    
    is_satisfy_never_decrease = True
    for idx in range(len(password) - 1):
        if password[idx] > password[idx + 1]:
            is_satisfy_never_decrease = False
            break
    
    return is_satisfy_digit and is_satisfy_length and is_satisfy_double and is_satisfy_never_decrease

def calculate_possible_passwords(seek_range):
    min, max = seek_range
    
    possibile_passwords = 0
    for password in range(int(min), int(max) + 1):
        if is_avaible(str(password)):
            possibile_passwords += 1
    
    return possibile_passwords

def parse_file(file_path : str):
    seek_range = (0,0)
    with open(file_path, 'r') as f:
        for line in f:
            seek_ranges = line.split('-')
            seek_range = (seek_ranges[0], seek_ranges[1])
    return seek_range

def main(argv):
    seek_range = parse_file(argv[1])
    possibilites = calculate_possible_passwords(seek_range)
    print('Possible number of password in range {} is {}'. format(seek_range, possibilites))
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
