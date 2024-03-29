'''
--- Day 10: Monitoring Station ---
You fly into the asteroid belt and reach the Ceres monitoring station. The Elves here have an emergency: they're having trouble tracking all of the asteroids and can't be sure they're safe.

The Elves would like to build a new monitoring station in a nearby area of space; they hand you a map of all of the asteroids in that region (your puzzle input).

The map indicates whether each position is empty (.) or contains an asteroid (#). The asteroids are much smaller than they appear on the map, and every asteroid is exactly in the center of its marked position. The asteroids can be described with X,Y coordinates where X is the distance from the left edge and Y is the distance from the top edge (so the top-left corner is 0,0 and the position immediately to its right is 1,0).

Your job is to figure out which asteroid would be the best place to build a new monitoring station. A monitoring station can detect any asteroid to which it has direct line of sight - that is, there cannot be another asteroid exactly between them. This line of sight can be at any angle, not just lines aligned to the grid or diagonally. The best location is the asteroid that can detect the largest number of other asteroids.

For example, consider the following map:

.#..#
.....
#####
....#
...##
The best location for a new monitoring station on this map is the highlighted asteroid at 3,4 because it can detect 8 asteroids, more than any other location. (The only asteroid it cannot detect is the one at 1,0; its view of this asteroid is blocked by the asteroid at 2,2.) All other asteroids are worse locations; they can detect 7 or fewer other asteroids. Here is the number of other asteroids a monitoring station on each asteroid could detect:

.7..7
.....
67775
....7
...87
Here is an asteroid (#) and some examples of the ways its line of sight might be blocked. If there were another asteroid at the location of a capital letter, the locations marked with the corresponding lowercase letter would be blocked and could not be detected:

#.........
...A......
...B..a...
.EDCG....a
..F.c.b...
.....c....
..efd.c.gb
.......c..
....f...c.
...e..d..c
Here are some larger examples:

Best is 5,8 with 33 other asteroids detected:

......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####
Best is 1,2 with 35 other asteroids detected:

#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.
Best is 6,3 with 41 other asteroids detected:

.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..
Best is 11,13 with 210 other asteroids detected:

.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
Find the best location for a new monitoring station. How many other asteroids can be detected from that location?
'''

import sys
import math
from copy import deepcopy
from itertools import islice, cycle


def ray_2pi_trace_asteroids(asteroid_map, x_pos, y_pos):
    if asteroid_map[y_pos][x_pos] != '#':
        return -1, -1, -1, -1

    x_len = len(asteroid_map[0])
    y_len = len(asteroid_map)

    is_in_range = lambda cur_x, cur_y: 0 <= cur_x < x_len and 0 <= cur_y < y_len
    is_asteroid = lambda field: field != '.'

    elements_2_pi = []
    asteroid_counter = 0
    # print('X|------------------------------------------')
    visited_points = {}
    for x_wall in range(x_pos + 1, x_len):
        y_vec = islice(cycle(range(y_len)), y_pos, y_pos + y_len)
        for vec in zip([x_wall] * x_len, y_vec):
            # # print('vec', vec)
            cur_x, cur_y = vec
            if (cur_x, cur_y) in visited_points.keys():
                continue
            is_found = False
            while is_in_range(cur_x, cur_y):
                if is_asteroid(asteroid_map[cur_y][cur_x]) and not is_found:
                    is_found = True
                    # print('{};{}:{}'.format(cur_x, cur_y, asteroid_map[cur_y][cur_x], end=' '))
                    asteroid_counter += 1
                    elements_2_pi.append((cur_x, cur_y))
                visited_points[(cur_x, cur_y)] = True

                cur_x += vec[0] - x_pos
                cur_y += vec[1] - y_pos

    # print('|X------------------------------------------')
    visited_points = {}
    for x_wall in reversed(range(x_pos)):
        y_vec = islice(cycle(range(y_len)), y_pos, y_pos + y_len)
        for vec in zip([x_wall] * x_len, y_vec):
            cur_x, cur_y = vec
            if (cur_x, cur_y) in visited_points.keys():
                continue
            is_found = False
            while is_in_range(cur_x, cur_y):
                if is_asteroid(asteroid_map[cur_y][cur_x]) and not is_found:
                    is_found = True
                    # print('{};{}:{}'.format(cur_x, cur_y, asteroid_map[cur_y][cur_x], end=' '))
                    asteroid_counter += 1
                    elements_2_pi.append((cur_x, cur_y))
                visited_points[(cur_x, cur_y)] = True

                cur_x += vec[0] - x_pos
                cur_y += vec[1] - y_pos

    # print('^X^-----------------------------------------')
    cur_x, cur_y = x_pos, y_pos + 1
    while is_in_range(cur_x, cur_y):
        if is_asteroid(asteroid_map[cur_y][cur_x]):
            # print('{};{}:{}'.format(cur_x, cur_y, asteroid_map[cur_y][cur_x], end=' '))
            asteroid_counter += 1
            elements_2_pi.append((cur_x, cur_y))
            break
        cur_y += 1

    # print('vXv-----------------------------------------')
    cur_x, cur_y = x_pos, y_pos - 1
    while is_in_range(cur_x, cur_y):
        if is_asteroid(asteroid_map[cur_y][cur_x]):
            # print('{};{}:{}'.format(cur_x, cur_y, asteroid_map[cur_y][cur_x], end=' '))
            asteroid_counter += 1
            elements_2_pi.append((cur_x, cur_y))
            break
        cur_y -= 1

    return x_pos, y_pos, asteroid_counter, elements_2_pi


def normalize_vector(x_pos, y_pos, vec):
    return


def clockwiseangle_and_distance(x_pos, y_pos):
    def _clockwiseangle_and_distance(vec):
        vector = (vec[0] - x_pos, vec[1] - y_pos)
        # Length of vector: ||v||
        lenvector = math.hypot(vector[0], vector[1])
        # If length is zero there is no angle
        if lenvector == 0:
            return -math.pi, 0
        # Normalize vector: v/||v||
        normalized = [vector[0] / lenvector, vector[1] / lenvector]
        # print(normalized)
        refvec = (0, -1)
        dotprod = normalized[0] * refvec[0] + normalized[1] * refvec[1]  # x1*x2 + y1*y2
        diffprod = refvec[1] * normalized[0] - refvec[0] * normalized[1]  # x1*y2 - y1*x2
        angle = -math.atan2(diffprod, dotprod)
        # angle = -math.arctan2(diffprod, dotprod)
        # Negative angles represent counter-clockwise angles so we need to subtract them
        # from 2*pi (360 degrees)
        if angle < 0:
            return 2 * math.pi + angle, lenvector
        # I return first the angle because that's the primary sorting criterium
        # but if two vectors have the same angle then the shorter distance should come first.
        return angle, lenvector

    return _clockwiseangle_and_distance


def vaporize(asteroid_map, x_pos, y_pos, number, initial_buffer=[]):
    destroyed = 0
    while destroyed < number:
        # print('::', sorted(initial_buffer, key=clockwiseangle_and_distance(x_pos, y_pos)))
        for vec in sorted(initial_buffer, key=clockwiseangle_and_distance(x_pos, y_pos)):
            asteroid_map[vec[1]][vec[0]] = '.'
            destroyed += 1
            if destroyed == number:
                print('{}th pos {}, answer={}'.format(number, vec, vec[0] * 100 + vec[1]))

        _, _, _, initial_buffer = ray_2pi_trace_asteroids(asteroid_map, x_pos, y_pos)


def parse_file(file_path: str):
    asteroid_map = []
    with open(file_path, 'r') as f:
        for line in f:
            asteroid_map.append(
                [char for char in (line.replace('\r', '').replace('\n', ''))])
    return asteroid_map


def main(argv):
    asteroid_map = parse_file(argv[1])
    x_best, y_best, max = -1, -1, -1
    elements_2_pi = []
    for y in range(len(asteroid_map)):
        for x in range(len(asteroid_map[0])):
            x_cur, y_cur, count_cur, cur_elements_2_pi = ray_2pi_trace_asteroids(asteroid_map, x, y)
            if max < count_cur:
                max = count_cur
                x_best = x_cur
                y_best = y_cur
                elements_2_pi = cur_elements_2_pi

    vaporize(deepcopy(asteroid_map), x_best, y_best, 200, elements_2_pi)
    # [vaporize(deepcopy(asteroid_map), x_best, y_best, num, elements_2_pi) for num in range(30)]

    print('The max asteroid you see is {} from pos {};{}'.format(max, x_best, y_best))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
