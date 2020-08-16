import pygame
from queue import PriorityQueue

WIDTH = 600
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

COLORS = {"red": (255, 118, 117), "green": (0, 184, 148), "blue": (9, 132, 227),
          "yellow": (253, 203, 110), "white": (255, 255, 255), "black": (0, 0, 0),
          "purple": (162, 155, 254), "orange": (255, 190, 118), "grey": (223, 230, 233),
          "turquoise": (116, 185, 255)}


class Square:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = COLORS["white"]
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.color == COLORS["black"]

    def reset(self):
        self.color = COLORS["white"]

    def make_closed(self):
        self.color = COLORS["red"]

    def make_open(self):
        self.color = COLORS["green"]

    def make_barrier(self):
        self.color = COLORS["black"]

    def make_start(self):
        self.color = COLORS["orange"]

    def make_end(self):
        self.color = COLORS["turquoise"]

    def make_path(self):
        self.color = COLORS["purple"]

    def draw(self, window):
        pygame.draw.rect(window, self.color,
                         (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {square: float("inf") for row in grid for square in row}
    g_score[start] = 0
    f_score = {square: float("inf") for row in grid for square in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            square = Square(i, j, gap, rows)
            grid[i].append(square)
    return grid


def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, COLORS["grey"], (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(window, COLORS["grey"], (j * gap, 0), (j * gap, width))


def draw(window, grid, rows, width):
    window.fill(COLORS["white"])
    for row in grid:
        for square in row:
            square.draw(window)

    draw_grid(window, rows, width)
    pygame.display.update()


def get_clicked_position(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


def main(width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None

    run = True
    while run:
        draw(WINDOW, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                square = grid[row][col]
                if not start and square != end:
                    start = square
                    start.make_start()
                elif not end and square != start:
                    end = square
                    end.make_end()
                elif square != end and square != start:
                    square.make_barrier()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                square = grid[row][col]
                square.reset()
                if square == start:
                    start = None
                if square == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for square in row:
                            square.update_neighbors(grid)

                    algorithm(lambda: draw(WINDOW, grid, ROWS, width), grid, start, end)

    pygame.quit()


main(WIDTH)
