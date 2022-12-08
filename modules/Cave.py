from modules.Board import Board
import numpy as np


class Cave(Board):
    # создание поля
    def __init__(self, width, height):
        super().__init__(width, height)
        self.ca_birth = 4
        self.ca_death = 3

    def next_move(self):
        neighbors = sum([np.roll(np.roll(self.board, -1, 1), 1, 0),
                         np.roll(np.roll(self.board, 1, 1), -1, 0),
                         np.roll(np.roll(self.board, 1, 1), 1, 0),
                         np.roll(np.roll(self.board, -1, 1), -1, 0),
                         np.roll(self.board, 1, 1),
                         np.roll(self.board, -1, 1),
                         np.roll(self.board, 1, 0),
                         np.roll(self.board, -1, 0)])
        self.board = (self.board == 0 & (neighbors > self.ca_birth)) |\
                     (self.board == 1 & ((neighbors < self.ca_death))).astype(np.uint8)

    def random_one(self, prob_limit=0.4):
        self.board = (np.random.sample(self.board.shape) > prob_limit).astype(np.uint8)
        step = self.board.shape[1] // 5
        self.board[:, 0] = 0
        self.board[:, -1] = 0
        self.board[0, :] = 0
        self.board[-1, :] = 0

    def random_two(self, prob_limit=0.4):
        self.board = (np.random.sample(self.board.shape) > prob_limit).astype(np.uint8)
        step = self.board.shape[1] // 5
        self.board[:, step // 2 - 1::step] = 1
        self.board[:, step // 2 + 1::step] = 1
        self.board[:, step // 2::step] = 1
        self.board[:, 0] = 0
        self.board[:, -1] = 0
        self.board[0, :] = 0
        self.board[-1, :] = 0

    def remove_islands(self):
        self.board.dtype = np.uint8
        clusters = {0: {0}}
        value = 2
        for i in range(self.width):
            for j in range(self.height):
                self.board[i, j] = int(self.board[i, j])
                if self.board[i, j]:
                    if j > 0 and self.board[i, j - 1] > 0:
                        self.board[i, j] = self.board[i, j - 1]
                        if i > 0 and self.board[i - 1, j] and self.board[i - 1, j] != self.board[i, j - 1]:
                            clusters[self.board[i, j - 1]] = \
                                clusters[self.board[i, j - 1]].union(clusters[self.board[i - 1, j]])
                            clusters[self.board[i - 1, j]] = clusters[self.board[i - 1, j]]
                            for key in clusters[self.board[i - 1, j]]:
                                if key != self.board[i, j - 1] and key != self.board[i - 1, j]:
                                    clusters[key] = clusters[self.board[i - 1, j]]
                    elif i > 0 and self.board[i - 1, j]:
                        self.board[i, j] = self.board[i - 1, j]
                    else:
                        self.board[i, j] = value
                        clusters[value] = {value}
                        value += 1
        for i in range(self.width):
            for j in range(self.height):
                self.board[i, j] = min(clusters[self.board[i, j]])
        cluster_nums = {}
        for key in clusters:
            clusters[key] = min(clusters[key])
            cluster_nums[clusters[key]] = cluster_nums.get(clusters[key], 0) + 1
        max_cluster = max(cluster_nums, key=lambda x: cluster_nums[x])
        for i in range(self.width):
            for j in range(self.height):
                if self.board[i, j] != max_cluster:
                    self.board[i, j] = 0

    def final(self):
        self.random_one()

        prev_board = np.copy(self.board)
        self.next_move()
        self.next_move()
        while (prev_board ^ self.board).any():
            prev_board = np.copy(self.board)
            self.next_move()
            self.next_move()
        self.board[:, 0] = 0
        self.board[:, -1] = 0
        self.board[0, :] = 0
        self.board[-1, :] = 0
        self.remove_islands()
        self.board[:, 0] = 0
        self.board[:, -1] = 0
        self.board[0, :] = 0
        self.board[-1, :] = 0


