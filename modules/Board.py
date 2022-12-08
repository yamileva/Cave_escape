import numpy as np
import pygame


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = np.zeros((width, height), dtype=np.uint8)
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.active_sell = None

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # отрисовка
    def render(self, screen):
        for row in range(self.height):
            for col in range(self.width):
                if self.board[col, row]:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (col * self.cell_size + self.left,
                                      row * self.cell_size + self.top,
                                      self.cell_size, self.cell_size))
                #else:
                #    pygame.draw.rect(screen, (255, 255, 255),
                 #                    (col * self.cell_size + self.left,
                #                      row * self.cell_size + self.top,
                 #                     self.cell_size, self.cell_size), 1)

    def get_cell(self, mouse_pos):
        row = (mouse_pos[1] - self.left) // self.cell_size
        col = (mouse_pos[0] - self.top) // self.cell_size
        if 0 <= row < self.height and 0 <= col < self.width:
            return (col, row)
        return None

    def on_click(self, cell_coords):
        self.active_sell = cell_coords

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

