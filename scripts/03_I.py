'''
--- Day 3: Crossed Wires ---
The gravity assist was successful, and you're well on your way to the Venus refuelling station. During the rush back on Earth, the fuel management system wasn't completely installed, so that's next on the priority list.

Opening the front panel reveals a jumble of wires. Specifically, two wires are connected to a central port and extend outward on a grid. You trace the path each wire takes as it leaves the central port, one wire per line of text (your puzzle input).

The wires twist and turn, but the two wires occasionally cross paths. To fix the circuit, you need to find the intersection point closest to the central port. Because the wires are on a grid, use the Manhattan distance for this measurement. While the wires do technically cross right at the central port where they both start, this point does not count, nor does a wire count as crossing with itself.

For example, if the first wire's path is R8,U5,L5,D3, then starting from the central port (o), it goes right 8, up 5, left 5, and finally down 3:

...........
...........
...........
....+----+.
....|....|.
....|....|.
....|....|.
.........|.
.o-------+.
...........
Then, if the second wire's path is U7,R6,D4,L4, it goes up 7, right 6, down 4, and left 4:

...........
.+-----+...
.|.....|...
.|..+--X-+.
.|..|..|.|.
.|.-X--+.|.
.|..|....|.
.|.......|.
.o-------+.
...........
These wires cross at two locations (marked X), but the lower-left one is closer to the central port: its distance is 3 + 3 = 6.

Here are a few more examples:

R75,D30,R83,U83,L12,D49,R71,U7,L72
U62,R66,U55,R34,D71,R55,D58,R83 = distance 159
R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51
U98,R91,D20,R16,D67,R40,U7,R15,U6,R7 = distance 135
What is the Manhattan distance from the central port to the closest intersection?
'''

import sys
import math


def create_point_path(wire_schema):
    start_point = (0, 0)
    start_length = 0
    route = {}
    for step in wire_schema:
        direction = step[0]
        length = int(step[1:])
        move = {
            'R': lambda p: (p[0] + 1, p[1]),
            'L': lambda p: (p[0] - 1, p[1]),
            'U': lambda p: (p[0], p[1] + 1),
            'D': lambda p: (p[0], p[1] - 1),
        }[direction]
        for s in range(length):
            start_point = move(start_point)
            if start_point not in route.keys():
                route[start_point] = start_length + 1 + s

    return route


def find_closet_path(wires):
    wire1_path = create_point_path(wires[1])
    wire2_path = create_point_path(wires[2])
    cross_length = float('inf')
    last_cross_coord = (0, 0)
    for w1_s in wire1_path.keys():
        if w1_s in wire2_path:
            cross_length_prev = min(cross_length, math.sqrt(w1_s[0] ** 2 + w1_s[1] ** 2))
            if cross_length_prev != cross_length:
                cross_length = cross_length_prev
                last_cross_coord = w1_s

    return abs(last_cross_coord[0]) + abs(last_cross_coord[1])


def parse_file(file_path: str):
    wires = {}
    with open(file_path, 'r') as f:
        idx = 0
        for line in f:
            idx += 1
            wires[idx] = line.split(',')
    return wires


def main(argv):
    wires = parse_file(argv[1])
    print('Minimal cross path is {}'.format(find_closet_path(wires)))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
