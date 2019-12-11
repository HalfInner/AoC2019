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
import pygame as pg

from operator import setitem
from re import findall

class SantaSnower:

    def __init__(self, snow_flakes):
        self.__snow_flakes = snow_flakes.copy()
        self.__is_size_calculated = False
        self.__elapsed_time = 0

    def elapse(self, delta_time=1):
        [setitem(self.__snow_flakes, idx, (
            (
                ((el[0][0] + (el[1][0] * delta_time),
                  (el[0][1] + (el[1][1] * delta_time))),
                 (el[1][0], el[1][1]))
            )
        )) for idx, el in enumerate(self.__snow_flakes)]
        self.__elapsed_time += delta_time

    @property
    def window_size(self):
        self.__calculate_required_size()
        return self.__len_x, self.__len_y

    @property
    def elapsed_time(self):
        return self.__elapsed_time

    def print(self, background_representation='.', snow_representation='#'):
        self.__calculate_required_size()
        return (((pos[0] - self.__min_x), (pos[1] - self.__min_y)) for pos, _ in self.__snow_flakes)

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
        coords_and_velocity = [((float(pos_vel[0]), float(pos_vel[1])), (float(pos_vel[2]), float(pos_vel[3]))) for
                               pos_vel in
                               [line.replace('position=<', '')
                                    .replace('velocity=<', ',')
                                    .replace('>', '').replace('\r', '').replace('\n', '')
                                    .split(',')
                                for line in f]]

    return coords_and_velocity


def main(argv):
    ss = SantaSnower(parse_file(argv[1]))

    background_colour = (255, 255, 255)

    expected_window_size = (1280, 720)

    screen = pg.display.set_mode(expected_window_size)
    pg.display.set_caption('AoC 2018 10_I')
    pg.font.init()
    my_font = pg.font.SysFont('Comic Sans MS', 30)

    ss.elapse(0)  # TOOD(HalfsInner): no 0 elapse cause shrinkt the output
    ss.elapse(8000)  # TOOD(HalfsInner): no 0 elapse cause shrinkt the output

    pg.key.set_repeat(1)
    running = True
    zoom_scalar = 30.
    delta_time = 0
    while running:
        screen.fill(background_colour)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    delta_time = 3
                    pg.key.set_repeat(1)
                if event.key == pg.K_SLASH:
                    ss.elapse(-delta_time)
                if event.key == pg.K_RETURN:
                    delta_time = 0
                    pg.key.set_repeat(100)
                if event.key == pg.K_LEFT:
                    ss.elapse(-1)
                if event.key == pg.K_RIGHT:
                    ss.elapse(1)

        ss.elapse(delta_time)
        map_idx_to_screen_x = lambda pos_x: (pos_x / ss.window_size[0]) * float(expected_window_size[0])
        map_idx_to_screen_y = lambda pos_y: (pos_y / ss.window_size[1]) * float(expected_window_size[1])
        map_idx_to_screen = lambda pos: (int(map_idx_to_screen_x(pos[0])), int(map_idx_to_screen_y(pos[1])))
        zoom_screen = lambda p: (int(((p[0] - float(expected_window_size[0]) / 2.) * zoom_scalar)
                                     + expected_window_size[0] / 2.),
                                 int(((p[1] - float(expected_window_size[1]) / 2.) * zoom_scalar)
                                     + expected_window_size[1] / 2.))

        zoom_in_x = lambda x: (x - ss.window_size[0] / 2) * zoom_scalar + ss.window_size[0] / 2
        zoom_in_y = lambda y: (y - ss.window_size[1] / 2) * zoom_scalar + ss.window_size[1] / 2

        # [pg.draw.circle(screen, 255, zoom_screen(map_idx_to_screen(pos)), 4) for pos in ss.print()]
        [pg.draw.circle(screen, 255, map_idx_to_screen((zoom_in_x(pos[0]), zoom_in_y(pos[1]))), 1) for pos in ss.print()]

        textsurface = my_font.render('FRAME: {}'.format(ss.elapsed_time), False, (0, 0, 0))
        screen.blit(textsurface, (0, 0))
        pg.display.flip()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
