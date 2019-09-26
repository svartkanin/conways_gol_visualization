import sys
import pygame
import argparse

from src.universe import Universe_2D, Universe_3D
from src.colors import Color


class Simulation():
    def __init__(
        self, sim_type, win_width, win_height, field_dim, population, rules
    ):
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
                win_width, win_height, field_dim, population, rules
            )
            self._rotate = False
            self._clock_tick = 10
        else:
            self._universe = Universe_3D(
                win_width, win_height, field_dim, population, rules
            )
            self._rotate = True
            self._clock_tick = 100

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

            # the 3D simulation dies off quite quickly so
            # lets wait a bit longer there
            self._clock.tick(self._clock_tick)
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
        help='Initial population in percent',
        default='50',
        action='store'
    )
    parser.add_argument(
        '--rules',
        '-r',
        type=str,
        help="""
            Ruleset after which a cells\' faith is decided; default values are 2333 for 2D and 5766 for 3D
        """,
        action='store',
        required=False
    )

    args = vars(parser.parse_args())

    win_size = args['win_size'].split('x')
    args['win_width'] = int(win_size[0])
    args['win_height'] = int(win_size[1])

    if args['rules'] is None:
        if args['simulation'] == '2D':
            args['rules'] = [2, 3, 3, 3]
        elif args['simulation'] == '3D':
            args['rules'] = [5, 7, 6, 6]
    else:
        if len(args['rules']) != 4:
            raise ValueError(
                'Ruleset has to be of length 4 and can only contain digits (e.g. 2333, 5766'
            )
        args['rules'] = [int(digit) for digit in args['rules']]

    return args


def _main():
    args = parse_args()
    simulation = Simulation(
        args['simulation'], args['win_width'], args['win_height'], args['dim'],
        args['population'], args['rules']
    )
    simulation.run()


if __name__ == "__main__":
    _main()
