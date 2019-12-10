'''
--- Day 1: The Tyranny of the Rocket Equation ---
Santa has become stranded at the edge of the Solar System while delivering presents to other planets! To accurately calculate his position in space, safely align his warp drive, and return to Earth in time to save Christmas, he needs you to bring him measurements from fifty stars.

Collect stars by solving puzzles. Two puzzles will be made available on each day in the Advent calendar; the second puzzle is unlocked when you complete the first. Each puzzle grants one star. Good luck!

The Elves quickly load you into a spacecraft and prepare to launch.

At the first Go / No Go poll, every Elf is Go until the Fuel Counter-Upper. They haven't determined the amount of fuel required yet.

Fuel required to launch a given module is based on its mass. Specifically, to find the fuel required for a module, take its mass, divide by three, round down, and subtract 2.

For example:

For a mass of 12, divide by 3 and round down to get 4, then subtract 2 to get 2.
For a mass of 14, dividing by 3 and rounding down still yields 4, so the fuel required is also 2.
For a mass of 1969, the fuel required is 654.
For a mass of 100756, the fuel required is 33583.
The Fuel Counter-Upper needs to know the total fuel requirement. To find it, individually calculate the fuel needed for the mass of each module (your puzzle input), then add together all the fuel values.

What is the sum of the fuel requirements for all of the modules on your spacecraft?
'''

import sys
import numpy as np
import pygame as pg

from operator import setitem
from re import findall
from PIL import Image
from matplotlib import cm


class SantaSnower:

    def __init__(self, snow_flakes):
        self.__snow_flakes = snow_flakes.copy()
        self.__is_size_calculated = False

    def elapse(self, delta_time=1):
        [setitem(self.__snow_flakes, idx, (
            (
                ((el[0][0] + (el[1][0] * delta_time),
                (el[0][1] + (el[1][1] * delta_time))),
                (el[1][0], el[1][1]))
            )
        )) for idx, el in enumerate(self.__snow_flakes)]

    @property
    def window_size(self):
        self.__calculate_required_size()
        return self.__len_x, self.__len_y

    def print(self, background_representation='.', snow_representation='#'):
        self.__calculate_required_size()
        empty_screen = [background_representation] * self.__len_x * self.__len_y
        [setitem(empty_screen, (pos[0] - self.__min_x) + (pos[1] - self.__min_y) * self.__len_x, snow_representation)
         for pos, _ in self.__snow_flakes]

        return empty_screen

    def __calculate_required_size(self):
        if self.__is_size_calculated:
            return
        min_x, max_x, min_y, max_y = 0, 0, 0, 0
        for idx, position in enumerate(self.__snow_flakes):
            if idx == 0:
                min_x, max_x, min_y, max_y = position[0][0], position[0][0], position[0][1], position[0][1]
                continue
            min_x = min(min_x, position[0][0])
            max_x = max(max_x, position[0][0])
            min_y = min(min_y, position[0][1])
            max_y = max(max_y, position[0][1])
        self.__min_x = min_x
        self.__max_x = max_x
        self.__min_y = min_y
        self.__max_y = max_y
        self.__len_x = self.__max_x - self.__min_x + 1
        self.__len_y = self.__max_y - self.__min_y + 1
        self.__is_size_calculated = True


def parse_file(file_path: str):
    coords_and_velocity = []
    with open(file_path, 'r') as f:
        coords_and_velocity = [((int(pos_vel[0]), int(pos_vel[1])), (int(pos_vel[2]), int(pos_vel[3]))) for pos_vel in
                               [line.replace('position=<', '')
                                    .replace('velocity=<', ',')
                                    .replace('>', '').replace('\r', '').replace('\n', '')
                                    .split(',')
                                for line in f]]

    return coords_and_velocity


def draw_on_screen(pixel_array, width, height):
    pixel_int_array = [ord(char) for char in pixel_array]
    data = np.array(pixel_int_array).reshape((width, height))

    # data *= 1/127.
    im = Image.fromarray(np.uint8(cm.gist_earth(data) * 255))
    im.show()


def main(argv):
    ss = SantaSnower(parse_file(argv[1]))

    background_colour = (255, 255, 255)

    window_size_x, window_size_y = ss.window_size

    expected_window_size = (800, 600)

    screen = pg.display.set_mode(expected_window_size)
    pg.display.set_caption('AoC 2018 10_I')
    screen.fill(background_colour)
    pg.display.flip()
    running = True

    ss.elapse(3)
    printout = ss.print()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        x_len, y_len = ss.window_size
        [pg.draw.circle(screen, 123, (idx % x_len * 10, idx // x_len * 10), 5) for idx, el in enumerate(printout) if el == '#']
        pg.display.flip()
    sys.exit(-1)

    for _ in range(1):
        ss.elapse(3)
        printout = ss.print()
        [print(line) for line in findall('.' * printout_row_size, ''.join(printout))]
        # draw_on_screen(printout, printout_row_size, printout_column_size)



if __name__ == "__main__":
    sys.exit(main(sys.argv))
