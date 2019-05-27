import sys
import pygame
import argparse

from src.universe import Universe_2D, Universe_3D
from src.colors import Color


class Simulation():
    def __init__(self, sim_type, win_width, win_height, field_dim, population):
        """
        Create a new GOL simulation
        
        Args:
            sim_type (str): The type of the simulation; either '2D' or '3D'
            win_width (int): Window screen width
            win_height (int): Window screen height
            field_dim (int): Dimension of the universe
            population (int): Initial population of the universe in %
        """
        pygame.init()

        self._screen = pygame.display.set_mode((win_width, win_height))
        self._clock = pygame.time.Clock()

        self._rotation_angle = 0

        if sim_type == '2D':
            self._universe = Universe_2D(
                win_width, win_height, field_dim, population
            )
            self._rotate = False
        else:
            self._universe = Universe_3D(
                win_width, win_height, field_dim, population
            )
            self._rotate = True

        self._universe.init_universe()

    def run(self):
        """
        Run the simulation
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._universe.calculate_new_generation()

            self._clock.tick(5)
            self._screen.fill(Color.DARKGREY.value)

            self._universe.transform_vectors(self._rotation_angle)

            for polygon in self._universe.get_all_polygons():
                pygame.draw.polygon(self._screen, Color.SILVER.value, polygon)
                pygame.draw.polygon(self._screen, Color.BLACK.value, polygon, 3)

            if self._rotate:
                self._rotation_angle += 1

            pygame.display.flip()


def parse_args():
    """
    Parse the command line arguments
    
    Returns:
        dict: Command line arguments
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--win-size',
        '-w',
        help='Window size',
        default='1280x800',
        action='store'
    )
    parser.add_argument(
        '--simulation',
        '-s',
        default='2D',
        choices=['2D', '3D'],
        help='Simulation type'
    )
    parser.add_argument(
        '--dim',
        '-d',
        type=int,
        help='Field dimensions',
        default='10',
        action='store'
    )
    parser.add_argument(
        '--population',
        '-p',
        type=int,
        help='Initial population in %',
        default='50',
        action='store'
    )

    args = vars(parser.parse_args())

    win_size = args['win_size'].split('x')
    args['win_width'] = int(win_size[0])
    args['win_height'] = int(win_size[1])

    return args


def _main():
    args = parse_args()
    simulation = Simulation(
        args['simulation'], args['win_width'], args['win_height'], args['dim'],
        args['population']
    )
    simulation.run()


if __name__ == "__main__":
    _main()
