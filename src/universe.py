import random

from pygame.math import Vector3


class Cell():
    def __init__(self, vectors, screen_width, screen_height, initial_angle):
        """
        Args:
            vectors (list): list of vectors that belong to this cube
            screen_width (int): Width of the window screen
            screen_height (int): Height of the window screen
            initial_angle (dict): Initial camera angle when starting the simulation
        """
        self._vectors = vectors
        self._camera_angle = initial_angle
        self._screen_width = screen_width
        self._screen_height = screen_height

        self._transformed_vectors = None
        self._avg_z = None
        self._polygons = None

        # the 8 neighbours of the cell
        self._faces = [
            (0, 1, 2, 3), (1, 5, 6, 2), (5, 4, 7, 6), (4, 0, 3, 7),
            (0, 4, 5, 1), (3, 2, 6, 7)
        ]

        self._setup_initial_positions()

    def _setup_initial_positions(self):
        """
        Instantiate the simulation by rotating all vectors to the
        initial camera angle
        """
        tmp = []

        # rotate the cells in the respective angles along the x-y-z axes
        for vector in self._vectors:
            if self._camera_angle['x'] != 0:
                vector = vector.rotate_x(self._camera_angle['x'])

            if self._camera_angle['y'] != 0:
                vector = vector.rotate_y(self._camera_angle['y'])

            if self._camera_angle['y'] != 0:
                vector = vector.rotate_z(self._camera_angle['z'])

            tmp.append(vector)

        self._vectors = tmp

    def transform_vectors(self, new_angle):
        """
        Transform all vectors to the new camera angle
        
        Args:
            new_angle (int): New angle to rotate all vectors to
        """
        self._transformed_vectors = []

        for vector in self._vectors:
            # Rotate the point around X axis, then around Y axis, and finally around Z axis.
            mod_vector = vector.rotate_y(new_angle)
            # Transform the point from 3D to 2D
            mod_vector = self._project_3d_to_2d(mod_vector, 256, 4)
            # Put the point in the list of transformed vectors
            self._transformed_vectors.append(mod_vector)

    def _project_3d_to_2d(self, vector, fov, viewer_distance):
        """
        Project a 3d vector to a 2d screen
        
        Args:
            vector (Vector3): The vector to be projected
            fov (int): 
            viewer_distance (int): View distance of the screen
        
        Returns:
            Vector3: The projected vector
        """
        factor = fov / (viewer_distance + vector.z)
        x = vector.x * factor + self._win_width / 2
        y = -vector.y * factor + self._win_height / 2
        return Vector3(x, y, vector.z)

    def calculate_average_z(self):
        """
        Calculate the average z value of all vectors and sides
        """
        self._avg_z = {}

        for idx, face in enumerate(self._faces):
            # for each vector of a face calculate the average z value
            avg_z = (
                self._transformed_vectors[face[0]].z +
                self._transformed_vectors[face[1]].z +
                self._transformed_vectors[face[2]].z +
                self._transformed_vectors[face[3]].z
            ) / 4.0
            self._avg_z[idx] = avg_z

    def create_polygons(self):
        """
        Cretae the polygons that ought to be drawn for the cube
        """
        self._polygons = []

        for idx, avg_z in self._avg_z.items():
            face = self._faces[idx]
            polygon = [
                (
                    self._transformed_vectors[face[0]].x,
                    self._transformed_vectors[face[0]].y
                ),
                (
                    self._transformed_vectors[face[1]].x,
                    self._transformed_vectors[face[1]].y
                ),
                (
                    self._transformed_vectors[face[2]].x,
                    self._transformed_vectors[face[2]].y
                ),
                (
                    self._transformed_vectors[face[3]].x,
                    self._transformed_vectors[face[3]].y
                ),
                (
                    self._transformed_vectors[face[0]].x,
                    self._transformed_vectors[face[0]].y
                )
            ]
            self._polygons.append([avg_z, polygon])

    def get_polygons(self):
        """
        Retrieve all polygons for the cube
        
        Returns:
            list: List of polygons
        """
        return self._polygons


class AbstractUniverse():
    def __init__(self, win_width, win_height, field_dim, cell_dim, population):
        """
        Args:
            win_width (int): Window screen width
            win_height (int): Window screen height
            field_dim (int): Dimension of the universe
            cell_dim (int): Dimension of one cell
            population (int): Initial population of the universe in %
        """
        self._win_width = win_width
        self._win_height = win_height

        self._field_dim = field_dim
        self._cell_dim = cell_dim

        self._cells = []

        self._population = population

    def init_universe(self):
        """
        Setup the universe with random cells acording to the population
        """
        total_decisions = len(self._universe.keys())
        alive_decisions = int(total_decisions * (self._population / 100.0))
        decisions = [1] * alive_decisions + [
            0
        ] * (total_decisions - alive_decisions)

        random.shuffle(decisions)

        for pos, decision in zip(self._universe.keys(), decisions):
            self._universe[pos] = decision

        self._create_cells()

    def get_cells(self):
        """
        Retrieve all cells of a universe
        
        Returns:
            list: List of cells belonging to that universe
        """
        return self._cells

    def transform_vectors(self, new_angle):
        """
        Transform all vectors of a universe to a new angle
        
        Args:
            new_angle (int): New camera angle
        """
        for cell in self._cells:
            cell.transform_vectors(new_angle)
            cell.calculate_average_z()
            cell.create_polygons()

    def get_all_polygons(self):
        """
        Retrieve all polygons of a universe
        
        Returns:
            list: List of all polygons of the universe
        """
        polygons = []
        for cell in self._cells:
            polygons += cell.get_polygons()

        polygons = sorted(polygons, key=lambda x: x[0], reverse=True)

        return [polygon[1] for polygon in polygons]

    def _create_cells(self):
        """
        Create all cells of the universe
        """
        self._cells = []

        for pos, val in self._universe.items():
            if val == 1:
                x = pos[0]
                y = pos[1] + 1

                if len(pos) == 3:  # 3 dimensions
                    z = pos[2]
                else:
                    z = 0

                # to center the plain on the screen,
                # we redifine the point of origin
                origin = -(self._field_dim / 2.0) * self._cell_dim

                x_left = origin + (x * self._cell_dim)
                x_right = (x_left) + self._cell_dim

                y_down = origin + (z * self._cell_dim)
                y_up = y_down + self._cell_dim

                z_back = origin - (y * -self._cell_dim)
                z_front = (z_back) + self._cell_dim

                cell = Cell(
                    [
                        Vector3(x_left, y_up, z_back),
                        Vector3(x_right, y_up, z_back),
                        Vector3(x_right, y_down, z_back),
                        Vector3(x_left, y_down, z_back),
                        Vector3(x_left, y_up, z_front),
                        Vector3(x_right, y_up, z_front),
                        Vector3(x_right, y_down, z_front),
                        Vector3(x_left, y_down, z_front)
                    ], self._win_width, self._win_height, self._camera_angle
                )

                self._cells.append(cell)


class Universe_2D(AbstractUniverse):
    def __init__(self, win_width, win_height, field_dim, population):
        """
        Create a 2D univerrse
        
        Args:
            win_width (int): Window screen width
            win_height (int): Window screen height
            field_dim (int): Dimension of the universe
            population (int): Initial population of the universe in %
        """
        cell_dim = 0.5

        super().__init__(win_width, win_height, field_dim, cell_dim, population)

        self._camera_angle = {'x': -90, 'y': 0, 'z': 0}

        # initialize a universe of size: row x col
        self._universe = {
            (i, j): 0
            for i in range(self._field_dim) for j in range(self._field_dim)
        }

    def calculate_new_generation(self):
        """
        Calculate a new generation of the universe
        """

        def new_cell_status(pos):
            """
            Determine if the cell is going to be alive or dead
            in the next generation
            
            Args:
                pos (tuple): Current position of the cell (int, int)
            
            Returns:
                int: 1 if the cell is going to be alive, otherwise 0
            """
            x = pos[0]
            y = pos[1]

            neighbours = [
                (x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y + 1),
                (x - 1, y), (x - 1, y - 1), (x, y - 1), (x + 1, y - 1)
            ]

            alive_neighbours = sum(
                self._universe[neighbour]
                for neighbour in neighbours if neighbour in self._universe
            )

            if self._universe[pos] == 0:  # birth
                if alive_neighbours == 3:
                    return 1
            else:  # survive or dead
                if alive_neighbours in (2, 3):
                    return 1
            return 0

        new_gen = {}
        for pos in self._universe.keys():
            new_gen[pos] = new_cell_status(pos)

        self._universe = new_gen

        self._create_cells()


class Universe_3D(AbstractUniverse):
    def __init__(self, win_width, win_height, field_dim, population):
        """
        Create a 3D univerrse
        
        Args:
            win_width (int): Window screen width
            win_height (int): Window screen height
            field_dim (int): Dimension of the universe
            population (int): Initial population of the universe in %
        """
        cell_dim = 0.3

        super().__init__(win_width, win_height, field_dim, cell_dim, population)

        self._camera_angle = {'x': 0, 'y': 0, 'z': 0}

        # initialize a universe of size: row x col x height
        self._universe = {
            (i, j, k): 0
            for i in range(self._field_dim) for j in range(self._field_dim)
            for k in range(self._field_dim)
        }

    def calculate_new_generation(self):
        """
        Calculate a new generation of the universe
        """

        def new_cell_status(pos):
            """
            Determine if the cell is going to be alive or dead
            in the next generation
            
            Args:
                pos (tuple): Current position of the cell (int, int)
            
            Returns:
                int: 1 if the cell is going to be alive, otherwise 0
            """
            x = pos[0]
            y = pos[1]
            z = pos[2]

            # the 26 neighbours of the cell
            neighbours = [
                (x + 1, y, z), (x + 1, y + 1, z), (x, y + 1, z),
                (x - 1, y + 1, z), (x - 1, y, z), (x - 1, y - 1, z),
                (x, y - 1, z), (x + 1, y - 1, z), (x + 1, y, z + 1),
                (x + 1, y + 1, z + 1), (x, y + 1, z + 1), (x - 1, y + 1, z + 1),
                (x - 1, y, z + 1), (x - 1, y - 1, z + 1), (x, y - 1, z + 1),
                (x + 1, y - 1, z + 1), (x + 1, y, z - 1), (x + 1, y + 1, z - 1),
                (x, y + 1, z - 1), (x - 1, y + 1, z - 1), (x - 1, y, z - 1),
                (x - 1, y - 1, z - 1), (x, y - 1, z - 1), (x + 1, y - 1, z - 1),
                (x, y, z + 1), (x, y, z - 1)
            ]

            alive_neighbours = sum(
                self._universe[neighbour]
                for neighbour in neighbours if neighbour in self._universe
            )

            if self._universe[pos] == 0:  # birth
                if alive_neighbours == 4:
                    return 1
            else:  # survive or dead
                if alive_neighbours in (3, 4):
                    return 1
            return 0

        new_gen = {}
        for pos in self._universe.keys():
            new_gen[pos] = new_cell_status(pos)

        self._universe = new_gen

        self._create_cells()
