from enum import Enum
from queue import PriorityQueue
import math

import pygame

HEIGHT = 800
WIDTH = 800
TOTAL_ROWS = 40
TOTAL_COLUMNS = 40
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A*")


class Colors(Enum):
    RED = (255, 0, 0)  # considered block
    WHITE = (255, 255, 255)  # empty block
    BLACK = (0, 0, 0)  # barrier block
    GREEN = (0, 255, 0)  # checked block
    BLUE = (0, 0, 255)  # end block
    GREY = (128, 128, 128)  # lines color
    YELLOW = (255, 255, 0)  # path block
    PURPLE = (128, 0, 128)  # start block


class Node:
    def __init__(self, row, col, total_rows, total_columns):
        self.row = row
        self.col = col
        self.height = HEIGHT // total_rows
        self.width = WIDTH // total_columns
        self.x = col * self.width
        self.y = row * self.height
        self.color = Colors.WHITE
        self.neighbours = []
        self.neighbours_corner = []

    def __lt__(self, other):
        return False

    def check_possible(self, row, col, grid):
        if row >= 0 and row < TOTAL_ROWS and col >= 0 and col < TOTAL_COLUMNS and not grid.grid[row][col].is_barrier():
            return True
        return False

    def update_neighbours(self, grid):
        if self.check_possible(self.row + 1, self.col, grid):  # DOWN
            self.neighbours.append(grid.grid[self.row + 1][self.col])

        if self.check_possible(self.row - 1, self.col, grid):  # UP
            self.neighbours.append(grid.grid[self.row - 1][self.col])

        if self.check_possible(self.row, self.col - 1, grid):  # LEFT
            self.neighbours.append(grid.grid[self.row][self.col - 1])

        if self.check_possible(self.row, self.col + 1, grid):  # RIGHT
            self.neighbours.append(grid.grid[self.row][self.col + 1])

        if self.check_possible(self.row + 1, self.col + 1, grid):  # DOWN - RIGHT
            self.neighbours_corner.append(grid.grid[self.row + 1][self.col + 1])

        if self.check_possible(self.row + 1, self.col - 1, grid):  # DOWN - LEFT
            self.neighbours_corner.append(grid.grid[self.row + 1][self.col - 1])

        if self.check_possible(self.row - 1, self.col + 1, grid):  # UP - RIGHT
            self.neighbours_corner.append(grid.grid[self.row - 1][self.col + 1])

        if self.check_possible(self.row - 1, self.col - 1, grid):  # UP - LEFT
            self.neighbours_corner.append(grid.grid[self.row - 1][self.col - 1])

    def is_start(self):
        return self.color == Colors.PURPLE

    def is_end(self):
        return self.color == Colors.BLUE

    def is_barrier(self):
        return self.color == Colors.BLACK

    def is_checked(self):
        return self.color == Colors.GREEN

    def is_considered(self):
        return self.color == Colors.RED

    def reset(self):
        self.color = Colors.WHITE

    def make_start(self):
        self.color = Colors.PURPLE

    def make_end(self):
        self.color = Colors.BLUE

    def make_barrier(self):
        self.color = Colors.BLACK

    def make_checked(self):
        self.color = Colors.GREEN

    def make_considered(self):
        self.color = Colors.RED

    def make_path(self):
        self.color = Colors.YELLOW

    def draw(self):
        pygame.draw.rect(WIN, self.color.value, (self.x, self.y, self.width, self.height))


def draw_lines():
    height_gap = HEIGHT // TOTAL_ROWS
    width_gap = WIDTH // TOTAL_COLUMNS
    for i in range(TOTAL_ROWS):
        pygame.draw.line(WIN, Colors.GREY.value, (0, i * height_gap), (WIDTH, i * height_gap))
    for j in range(TOTAL_ROWS):
        pygame.draw.line(WIN, Colors.GREY.value, (j * width_gap, 0), (j * width_gap, HEIGHT))


class Grid:
    def __init__(self):
        self.grid = [[Node(row, col, TOTAL_ROWS, TOTAL_COLUMNS) for col in range(TOTAL_COLUMNS)] for row in
                     range(TOTAL_ROWS)]

    def draw(self):
        WIN.fill(Colors.WHITE.value)
        for row in self.grid:
            for node in row:
                node.draw()

        draw_lines()
        pygame.display.update()


def get_clicked_pos(pos):
    x, y = pos
    height_gap = HEIGHT // TOTAL_ROWS
    width_gap = WIDTH // TOTAL_COLUMNS
    row = x // width_gap
    col = y // height_gap
    return col, row


def h(point1, point2):
    row1 = point1.row
    col1 = point1.col
    row2 = point2.row
    col2 = point2.col
    return abs(row1 - row2) + abs(col1 - col2)


def h2(point1, point2):
    row1 = point1.row
    col1 = point1.col
    row2 = point2.row
    col2 = point2.col
    return math.sqrt(pow(abs(row1 - row2), 2) + pow(abs(col1 - col2), 2))


def make_path(came_from, end, start):
    current_node = end
    while (current_node != start):
        current_node = came_from[current_node]
        current_node.make_path()


def a_star(start, end, grid):
    count = 0
    came_from = {}
    considered_queue = PriorityQueue()
    is_in_considered_set = {start}
    g_score = {node: float("Inf") for row in grid.grid for node in row}
    f_score = {node: float("Inf") for row in grid.grid for node in row}
    g_score[start] = 0
    f_score[start] = h2(start, end)
    considered_queue.put((f_score[start], count, start))

    while not considered_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current_node = considered_queue.get()[2]
        is_in_considered_set.remove(current_node)

        if current_node == end:
            make_path(came_from, end, start)
            start.make_start()
            return

        for neighbour in current_node.neighbours:
            temp_g_score = g_score[current_node] + 1
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current_node
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = g_score[neighbour] + h2(neighbour, end)
                if neighbour not in is_in_considered_set:
                    is_in_considered_set.add(neighbour)
                    considered_queue.put((f_score[neighbour], count, neighbour))
                    if neighbour != end:
                        neighbour.make_considered()

        for neighbour_corner in current_node.neighbours_corner:
            temp_g_score = g_score[current_node] + math.sqrt(2)
            if temp_g_score < g_score[neighbour_corner]:
                came_from[neighbour_corner] = current_node
                g_score[neighbour_corner] = temp_g_score
                f_score[neighbour_corner] = g_score[neighbour_corner] + h2(neighbour_corner, end)
                if neighbour_corner not in is_in_considered_set:
                    is_in_considered_set.add(neighbour_corner)
                    considered_queue.put((f_score[neighbour_corner], count, neighbour_corner))
                    if neighbour_corner != end:
                        neighbour_corner.make_considered()

        if current_node != start:
            current_node.make_checked()
        grid.draw()


def main():
    grid = Grid()
    start = None
    end = None
    running = True
    while running:
        grid.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for i in range(TOTAL_ROWS):
                        for j in range(TOTAL_COLUMNS):
                            grid.grid[i][j].update_neighbours(grid)

                    a_star(start, end, grid)
                if event.key == pygame.K_c:
                    grid = Grid()
                    start = None
                    end = None
            if pygame.mouse.get_pressed()[0]:  # lef button
                mouse_pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(mouse_pos)
                node = grid.grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()
            if pygame.mouse.get_pressed()[2]:  # right button
                mouse_pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(mouse_pos)
                node = grid.grid[row][col]
                if node.is_start():
                    start = None
                elif node.is_end():
                    end = None
                node.reset()


main()
