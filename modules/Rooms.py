import numpy as np
import random
from itertools import combinations
from modules.Board import Board


ASPECT_RATIO = 0.25


class TreeRect:
    def __init__(self, x0, y0, x1, y1, parent=None):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.parent = parent
        self.left_child = None
        self.right_child = None
        self.color = (255, 0, 0)
        self.empty = True

    def bisection(self, global_min):
        new_min = [0] * 2
        new_max = [0] * 2
        div = [0] * 2

        new_min[0] = max(int((self.y1 - self.y0) * ASPECT_RATIO), global_min)  + self.x0
        new_max[0] = self.x1 + self.x0 - new_min[0]
        div[0] = (new_min[0] < new_max[0])

        new_min[1] = max(int((self.x1 - self.x0) * ASPECT_RATIO), global_min) + self.y0
        new_max[1] = self.y1 + self.y0 - new_min[1]
        div[1] = (new_min[1] < new_max[1])

        if not any(div):
            return False
        if all(div):
            choice_div = random.choice([0, 1])
        else:
            choice_div = div.index(True)

        new_coord = random.randint(new_min[choice_div], new_max[choice_div])
        if choice_div: # y
            self.left_child = TreeRect(self.x0, self.y0, self.x1, new_coord, self)
            self.right_child = TreeRect(self.x0, new_coord, self.x1, self.y1, self)
        else: # x
            self.left_child = TreeRect(self.x0, self.y0, new_coord, self.y1, self)
            self.right_child = TreeRect(new_coord, self.y0, self.x1, self.y1, self)
        return True


class Room(TreeRect):
    def __init__(self, x0, y0, x1, y1, leaf_rect):
        super().__init__(x0, y0, x1, y1, leaf_rect)
        self.neighbours = []
        self.color = (0, 255, 0)
        self.empty = False


class Tree:
    def __init__(self, width, height):
        self.root = TreeRect(0, 0, width, height)
        self.leaves = []
        self.small_rooms = []
        self.edges = []
        self.tonnels = []
        self.levels = 3
        self.min_size = max([width, height]) // self.levels
        self.min_small_size = self.min_size / 2
        self.map = np.zeros((self.root.x1, self.root.y1), dtype=np.uint8)

    def generate(self):
        self.tree_generator()
        self.room_creator(self.min_small_size // 4, self.min_small_size)
        self.neighbour_search()
        self.tonnel_creator()

    def set_levels(self, num_levels):
        if num_levels > 0:
            self.levels = num_levels

    def set_min_size(self, min_size, min_small_size):
        if min_size > 0:
            self.min_size = min_size
        if min_small_size > 0:
            self.min_small_size = min_small_size

    def tree_generator(self, room=None):
        if room is None:
            self.leaves = []
            room = self.root
        if max([room.x1 - room.x0, room.y1 - room.y0]) > self.min_size and \
                room.bisection(self.min_size):
            self.tree_generator(room.left_child)
            self.tree_generator(room.right_child)
        else:
            self.leaves.append(room)

    def room_creator(self, distance, min_size):
        for rect in self.leaves:
            x0 = random.randint(rect.x0 + distance, min(rect.x1 - distance - min_size, (rect.x0 + rect.x1) // 2))
            y0 = random.randint(rect.y0 + distance, min(rect.y1 - distance - min_size, (rect.y0 + rect.y1) // 2))
            width = random.randint(min_size, rect.x1 - distance - x0)
            height = random.randint(min_size, rect.y1 - distance - y0)
            self.small_rooms.append(Room(x0, y0, x0 + width, y0 + height, rect))

    def neighbour_search(self):
        for room1, room2 in combinations(self.small_rooms, 2):
            xs1 = set(range(room1.parent.x0, room1.parent.x1 + 1))
            xs2 = set(range(room2.parent.x0, room2.parent.x1 + 1))
            ys1 = set(range(room1.parent.y0, room1.parent.y1 + 1))
            ys2 = set(range(room2.parent.y0, room2.parent.y1 + 1))
            if len(xs1 & xs2) * len(ys1 & ys2) > 1:
                room1.neighbours.append(room2)
                room2.neighbours.append(room1)
                self.edges.append((room1, room2))

    def tonnel_creator(self):
        for room1, room2 in self.edges:
            p1 = (int(random.gauss((room1.x0 + room1.x1) // 2, (room1.x1 - room1.x0) / 20)),
                  int(random.gauss((room1.y0 + room1.y1) // 2, (room1.y1 - room1.y0) / 20)))
            p2 = (int(random.gauss((room2.x0 + room2.x1) // 2, (room2.x1 - room2.x0) / 20)),
                  int(random.gauss((room2.y0 + room2.y1) // 2, (room2.y1 - room2.y0) / 20)))
            #width = int(random.gauss(self.min_small_size * 3, self.min_small_size / 2))
            width = random.choice(range(self.min_small_size // 4,
                                        max(self.min_small_size // 2, 4)))
            self.tonnels.append((p1, p2, width))

class Chamber(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.tree = Tree(width, height)


    def final(self):
        self.tree.set_min_size(15, 10)
        self.tree.generate()

        for room in self.tree.small_rooms:
            self.board[room.x0:room.x1, room.y0:room.y1] = 1

        for p1, p2, width in self.tree.tonnels:
            if abs(p1[0] - p2[0]) > abs(p1[1] - p2[1]):
                dx = 1 if p1[0] < p2[0] else -1
                k = (p1[1] - p2[1]) / (p1[0] - p2[0])
                for x in range(p1[0], p2[0] + 1, dx):
                    y = int(k * (x - p1[0])) + p1[1]
                    self.board[x, y - width // 2:y + width // 2] = 1
            else:
                dy = 1 if p1[1] < p2[1] else -1
                k = (p1[0] - p2[0]) / (p1[1] - p2[1])
                for y in range(p1[1], p2[1] + 1, dy):
                    x = int(k * (y - p1[1])) + p1[0]
                    self.board[x - width // 2:x + width // 2, y] = 1
        self.board[:, 0] = 0
        self.board[:, -1] = 0
        self.board[0, :] = 0
        self.board[-1, :] = 0

