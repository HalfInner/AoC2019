'''
--- Part Two ---
An Elf just remembered one more important detail: the two adjacent matching digits are not part of a larger group of matching digits.

Given this additional criterion, but still ignoring the range rule, the following are now true:

112233 meets these criteria because the digits never decrease and all repeated digits are exactly two digits long.
123444 no longer meets the criteria (the repeated 44 is part of a larger group of 444).
111122 meets the criteria (even though 1 is repeated more than twice, it still contains a double 22).
How many different passwords within the range given in your puzzle input meet all of the criteria?
'''

import sys
import math

def is_avaible(password):
    is_satisfy_digit = password.isdigit()
    
    is_satisfy_length = len(password) == 6
    
    is_satisfy_double_extended = False
    last_digit = ''
    for idx in range(len(password) - 1):
        #print('Password={} idx={} last_digit={}'.format(password[idx], idx, last_digit))
        if password[idx] != password[idx + 1] or password[idx] == last_digit:
            continue

        last_digit = password[idx]
        if ((idx + 2) == len(password)) or (password[idx] != password[idx + 2]):
            is_satisfy_double_extended = True
            break

    is_satisfy_never_decrease = True
    for idx in range(len(password) - 1):
        if password[idx] > password[idx + 1]:
            is_satisfy_never_decrease = False
            break
    
    return is_satisfy_digit and is_satisfy_length and is_satisfy_double_extended and is_satisfy_never_decrease

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
