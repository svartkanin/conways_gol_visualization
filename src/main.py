import sys
import math
import pygame

from pygame.math import Vector3
from enum import Enum
from random import randint


class Color(Enum):
    DARKGREY = (47, 79, 79)
    BLACK = (0, 0, 0)
    SILVER = (192,192,192)


class Cube():

    def __init__(self, vectors, screen_width, screen_height, initial_angle):
        self._vectors = vectors
        self._angle = initial_angle
        self._screen_width = screen_width
        self._screen_height = screen_height

        self._transformed_vectors = None

        # Define the vectors that compose each of the 6 faces
        self._faces  = [(0,1,2,3),
                       (1,5,6,2),
                       (5,4,7,6),
                       (4,0,3,7),
                       (0,4,5,1),
                       (3,2,6,7)]

        self._setup_initial_positions(initial_angle)

    def _setup_initial_positions(self, angle):
        tmp = []
        for vector in self._vectors:
            rotated_vector = vector.rotate_x(angle)#.rotate_y(angle)#.rotateZ(self.angle)
            tmp.append(rotated_vector)

        self._vectors = tmp

    def transform_vectors(self, new_angle):
        # It will hold transformed vectors.
        transformed_vectors = []

        for vector in self._vectors:
            # Rotate the point around X axis, then around Y axis, and finally around Z axis.
            mod_vector = vector.rotate_y(new_angle)
            # Transform the point from 3D to 2D
            mod_vector = self._project(mod_vector, self._screen_width, self._screen_height, 256, 4)
            # Put the point in the list of transformed vectors
            transformed_vectors.append(mod_vector)
        
        self._transformed_vectors = transformed_vectors

    def _project(self, vector, win_width, win_height, fov, viewer_distance):
        factor = fov / (viewer_distance + vector.z)
        x = vector.x * factor + win_width / 2
        y = -vector.y * factor + win_height / 2
        return Vector3(x, y, vector.z)

    def calculate_average_z(self):
        avg_z = []
        for i, face in enumerate(self._faces):
            # for each point of a face calculate the average z value
            z = (self._transformed_vectors[face[0]].z + 
                 self._transformed_vectors[face[1]].z + 
                 self._transformed_vectors[face[2]].z + 
                 self._transformed_vectors[face[3]].z) / 4.0
            avg_z.append([i, z])

        return avg_z

    def create_polygon(self, face_index):
        face = self._faces[face_index]
        return [(self._transformed_vectors[face[0]].x, self._transformed_vectors[face[0]].y), 
                (self._transformed_vectors[face[1]].x, self._transformed_vectors[face[1]].y),
                (self._transformed_vectors[face[2]].x, self._transformed_vectors[face[2]].y),
                (self._transformed_vectors[face[3]].x, self._transformed_vectors[face[3]].y),
                (self._transformed_vectors[face[0]].x, self._transformed_vectors[face[0]].y)]


class Plane():

    def __init__(self, win_width, win_height, initial_angle, field_dim):
        self._field_dim = field_dim
        self._cube_dim = 0.3

        self._win_width = win_width
        self._win_height = win_height

        # initialize a plane of size: row x col
        self._2d_plane = {(i, j): 0 for i in range(self._field_dim) for j in range(self._field_dim)}

        self._cubes = []
        self._angle = initial_angle

    def init_plane(self, random=True):
        for pos in self._2d_plane.keys():
            if random:
                self._2d_plane[pos] = randint(0,1)

        # self._2d_plane[(1,0)] = 1
        # self._2d_plane[(1,1)] = 1
        # self._2d_plane[(1,2)] = 1

        self._create_cubes()

    def calculate_new_generation(self):
        def new_cell_status(pos):
            x = pos[0]
            y = pos[1]

            neighbours = [
                (x+1, y),
                (x+1, y+1),
                (x, y+1),
                (x-1, y+1),
                (x-1, y),
                (x-1, y-1),
                (x, y-1),
                (x+1, y-1)
            ]

            alive_neighbours = sum(self._2d_plane[neighbour] for neighbour in neighbours if neighbour in self._2d_plane)

            if self._2d_plane[pos] == 0:  # birth
                if alive_neighbours == 3:
                    return 1
            else: # survive or dead
                if alive_neighbours in (2, 3):
                    return 1
            return 0

        new_gen = {}
        for pos in self._2d_plane.keys():
            new_gen[pos] = new_cell_status(pos)

        self._2d_plane = new_gen

        self._create_cubes()

    def _create_cubes(self):
        vectors = []

        self._cubes = []

        for pos, val in self._2d_plane.items():
            if val == 1:
                x = pos[0]
                y = pos[1] + 1

                # to center the plain on the screen we redifine the
                # x origin point
                x_zero = -(self._field_dim / 2.0) * self._cube_dim
                y_zero = 0

                x_left = (x_zero) + (x * self._cube_dim)
                x_right = (x_left) + self._cube_dim
                y_down = (y_zero) + 0
                y_up = y_down + self._cube_dim
                z_back = y * -self._cube_dim
                z_front = (z_back) + self._cube_dim

                cube = Cube([
                    Vector3(x_left, y_up, z_back),
                    Vector3(x_right, y_up, z_back),
                    Vector3(x_right, y_down, z_back),
                    Vector3(x_left, y_down, z_back),
                    Vector3(x_left, y_up, z_front),
                    Vector3(x_right, y_up, z_front),
                    Vector3(x_right, y_down, z_front),
                    Vector3(x_left, y_down, z_front)
                ], self._win_width, self._win_height, self._angle)

                self._cubes.append(cube)

    def get_cubes(self):
        return self._cubes


class Simulation():

    def __init__(self, win_width, win_height, field_dim):
        pygame.init()
 
        self.screen = pygame.display.set_mode((win_width, win_height))
        self.clock = pygame.time.Clock()

        self._angle = 0
        initial_angle = -40

        self._plane = Plane(win_width, win_height, initial_angle, field_dim)
        self._plane.init_plane()
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._plane.calculate_new_generation()
 
            self.clock.tick(4)
            self.screen.fill(Color.DARKGREY.value)

            polygons = []
            for cube in self._plane.get_cubes():
                cube.transform_vectors(self._angle)
                avg_z = cube.calculate_average_z()

                for z in avg_z:
                    pointlist = cube.create_polygon(z[0])
                    polygons.append((pointlist, z[1]))

            for poly in sorted(polygons, key=lambda x: x[1], reverse=True):
                pygame.draw.polygon(self.screen, Color.SILVER.value,poly[0])
                pygame.draw.polygon(self.screen, Color.BLACK.value, poly[0], 3)

            # self._angle += 1
 
            pygame.display.flip()
 
if __name__ == "__main__":
    win_width = 1024
    win_height = 800
    field_dim = 10

    Simulation(win_width, win_height, field_dim).run()




# 640 x 480
# 10