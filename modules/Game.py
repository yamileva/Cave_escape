import pygame
import os
import sys
import random
from modules.Cave import Cave
from modules.Rooms import Chamber
from modules.Camera import Camera
from modules.Sprites import Tile, SpriteGroup, Enemy, Player


class Settings:
    def __init__(self, game, fps=30, map_table_size=(60, 40), cell_size=30):
        self.fps = fps
        self.corner_left = 1
        self.corner_top = 1
        self.cell_size = cell_size
        self.map_table_rows, self.map_table_cols = self.map_table_size = map_table_size
        self.map_size = (self.map_table_cols * self.cell_size + 2 * self.corner_top,
                         self.map_table_rows * self.cell_size + 2 * self.corner_left)

        self.screen = game.screen
        self.screen_rect = game.screen.get_rect()
        self.map_rect = pygame.Rect((0, 0, *self.map_size))


class Game:
    MAP_TYPES = {"cave": Cave,
                 "chamber": Chamber}
    TILE_IMAGES = {'grey__squa': {'sheet': 'grey-black.png',
                                  'dir': 'squares',
                                  'table': False,
                                  'alpha': True
                                  },
                   'green_squa': {'sheet': 'green.png',
                                  'dir': 'squares',
                                  'table': False,
                                  'alpha': True
                                  },
                   'lblue_squa': {'sheet': 'light-blue.png',
                                  'dir': 'squares',
                                  'table': False,
                                  'alpha': False
                                  },
                   'orang_squa': {'sheet': 'orange.png',
                                  'dir': 'squares',
                                  'table': False,
                                  'alpha': False
                                  },
                   'diff__squa': {'sheet': 'square-set.png',
                                  'dir': 'squares',
                                  'table': True,
                                  'alpha': True,
                                  'tab_size': (2, 3),
                                  'tiles': {'green': (0, 0),
                                            'yellow': (0, 1),
                                            'blue': (0, 2),
                                            'orange': (1, 0),
                                            'red': (1, 1),
                                            'grey': (1, 2)
                                            }
                                  },
                   'grey__ball': {'sheet': 'grey.png',
                                  'dir': 'balls',
                                  'table': False,
                                  'alpha': True
                                  },
                   'green_ball': {'sheet': 'green.png',
                                  'dir': 'balls',
                                  'table': False,
                                  'alpha': True
                                  },
                   'neon__ball': {'sheet': 'neon.png',
                                  'dir': 'balls',
                                  'table': False,
                                  'alpha': True
                                  },
                   'hole__ball': {'sheet': 'outdoor.png',
                                  'dir': 'balls',
                                  'table': False,
                                  'alpha': False
                                  },
                   'diff__ball': {'sheet': 'balls.png',
                                  'dir': 'balls',
                                  'table': True,
                                  'alpha': False,
                                  'tab_size': (2, 2),
                                  'tiles': {'yellow': (0, 0),
                                            'lemon': (1, 0),
                                            'blue': (0, 1),
                                            'pink': (1, 1)
                                            }
                                  }
                   }
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.settings = Settings(self)

        self.hero_speed = 5
        self.enemy_speeds = list(range(2, 7))
        self.hero_image_name = ('diff__ball', 'blue')
        self.enemy_image_names = [('diff__ball', 'lemon'), ('diff__ball', 'yellow'), ('diff__ball', 'pink')]
        self.tile_image_name = ('grey__squa',)
        self.hole_image_name = ('green_squa', )

        self.set_images()
        self.wall_group = SpriteGroup()
        self.hero_group = SpriteGroup()
        self.enemy_group = SpriteGroup()
        self.hole_group = SpriteGroup()
        self.clock = pygame.time.Clock()
        self.reset_first_level()

    def reset_first_level(self):
        self.level = 0
        self.enemy_probability = 0.005

    def new_level(self):
        self.is_game_over = False
        self.is_level_passed = False
        self.level += 1
        self.start_level_screen(self.level)
        self.hero = None
        self.wall_group.empty()
        self.hero_group.empty()
        self.enemy_group.empty()
        self.hole_group.empty()
        self.generate_level()

    def generate_level(self):
        if self.level % 2:
            self.map_type = "chamber"
            self.enemy_probability *= 2
        else:
            self.map_type = "cave"

        self.generate_map()
        self.set_tiles()
        self.camera = Camera(self.hero, (self.wall_group, self.enemy_group, self.hole_group), self.settings)
        self.camera.apply()

    def generate_map(self):
        self.map = self.MAP_TYPES[self.map_type](*self.settings.map_table_size)
        self.map.set_view(self.settings.corner_left, self.settings.corner_top,
                          self.settings.cell_size)
        self.map.final()

    def load_image(self, keys, color_key=None):
        key = keys[0]
        name = self.TILE_IMAGES[key]['sheet']
        if 'dir' in self.TILE_IMAGES[key]:
            name = os.path.join(self.TILE_IMAGES[key]['dir'], name)
        name = os.path.join('data', name)
        try:
            image = pygame.image.load(name)
        except pygame.error as message:
            print('Не удаётся загрузить:', name)
            raise SystemExit(message)

        if color_key is not None and not self.TILE_IMAGES[key]['alpha']:
            image = image.convert()
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        elif self.TILE_IMAGES[key]['alpha']:
            image = image.convert_alpha()
        else:
            image = image.convert()

        if len(keys) > 1:
            subkey = keys[1]
            rows = self.TILE_IMAGES[key]['tab_size'][0]
            columns = self.TILE_IMAGES[key]['tab_size'][1]
            rect = pygame.Rect(0, 0, image.get_width() // columns, image.get_height() // rows)
            x = rect.w * self.TILE_IMAGES[key]['tiles'][subkey][1]
            y = rect.h * self.TILE_IMAGES[key]['tiles'][subkey][0]
            subimage = image.subsurface(pygame.Rect((x, y), rect.size))
            return subimage
        return image

    def set_images(self):
        self.hero_image = pygame.transform.scale(self.load_image((self.hero_image_name), -1),
                                                 (self.settings.cell_size // 4 * 3,
                                                  self.settings.cell_size // 4 * 3))
        self.enemy_images = [pygame.transform.scale(self.load_image(name, -1),
                                                    (self.settings.cell_size // 4 * 3,
                                                     self.settings.cell_size // 4 * 3))
                             for name in self.enemy_image_names]
        self.tile_image = pygame.transform.scale(self.load_image(self.tile_image_name, -1),
                                                 (self.settings.cell_size,
                                                  self.settings.cell_size))
        self.hole_image = pygame.transform.scale(self.load_image(self.hole_image_name, -1),
                                                 (self.settings.cell_size // 4 * 3,
                                                  self.settings.cell_size // 4 * 3))

    def set_tiles(self):
        for x in range(self.map.width):
            for y in range(self.map.height):
                if self.map.board[x, y] == 0:
                    Tile(self, self.wall_group,
                         x * self.settings.cell_size, y * self.settings.cell_size,
                         self.tile_image)
                else:
                    if self.hero is None:  # and x * CELL_SIZE < SCREEN_SIZE[0] // 2:
                        self.hero = Player(self, self.hero_group,
                                           x * self.settings.cell_size, y * self.settings.cell_size,
                                           self.hero_image, self.hero_speed)
                    elif random.random() < self.enemy_probability:
                        on_vert = 1
                        i = y
                        while i < self.settings.map_rect.bottom and self.map.board[x, i]:
                            i += 1
                            on_vert += 1
                        i = y
                        while i >= self.settings.map_rect.top and self.map.board[x, i]:
                            i -= 1
                            on_vert += 1
                        on_hor = 1
                        i = x
                        while i < self.settings.map_rect.right and self.map.board[i, y]:
                            i += 1
                            on_hor += 1
                        i = y
                        while i >= self.settings.map_rect.left and self.map.board[i, y]:
                            i -= 1
                            on_hor += 1

                        if on_vert < 3 and on_hor < 3:
                            continue
                        if on_vert > on_hor:
                            direction = (0, 1)
                        else:
                            direction = (1, 0)
                        speed = random.choice(self.enemy_speeds)
                        image = self.enemy_images[speed // len(self.enemy_images)]
                        Enemy(self, self.enemy_group,
                              x * self.settings.cell_size, y * self.settings.cell_size,
                              image, speed, direction)

        x = self.map.width - 1
        y = self.map.height - 1
        while self.map.board[x, y] == 0:
            y = random.randint(0, self.map.height - 1)
            x = random.randint(max(self.map.width // 2 - y,
                                   self.settings.screen_rect.right // self.settings.cell_size),
                               self.map.width - 1)

        Tile(self, self.hole_group, x * self.settings.cell_size, y * self.settings.cell_size, self.hole_image)

    def start_game_screen(self):
        intro_text = ["Выход из пещеры",
                      "", "Проведите голубой шар к выходу из пещеры,",
                      "уворачиваясь от других шаров"
                      "", "", "Пробел - начать игру",
                      "", "Escape - выйти"
                      ]

        #fon = pygame.transform.scale(load_image('fon.jpg'), SCREEN_SIZE)
        self.screen.fill(pygame.Color("black"))
        font = pygame.font.Font(None, 40)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('yellow'))
            intro_rect = string_rendered.get_rect()
            text_coord += 20
            intro_rect.top = text_coord
            intro_rect.x = 60
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.terminate()
                    elif event.key == pygame.K_SPACE:
                        return
            pygame.display.flip()
            self.clock.tick(self.settings.fps)

    def start_level_screen(self, level):
        intro_text = ["Выход из пещеры", "", str(level) + " уровень"]

        #fon = pygame.transform.scale(load_image('fon.jpg'), SCREEN_SIZE)
        self.screen.fill(pygame.Color("black"))
        font = pygame.font.Font(None, 40)
        text_coord = 80
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('yellow'))
            intro_rect = string_rendered.get_rect()
            text_coord += 20
            intro_rect.top = text_coord
            intro_rect.x = 80
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)
        t = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.terminate()
            if t > 2 * self.settings.fps:
                return
            pygame.display.flip()
            t += 1
            self.clock.tick(self.settings.fps)

    def fall_screen(self):
        intro_text = ["Вы проиграли",
                      "", "Пробел - начать игру заново",
                      "", "Escape - выйти"]

        #fon = pygame.transform.scale(load_image('fon.jpg'), SCREEN_SIZE)
        self.screen.fill(pygame.Color("black"))
        font = pygame.font.Font(None, 40)
        text_coord = 80
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('yellow'))
            intro_rect = string_rendered.get_rect()
            text_coord += 20
            intro_rect.top = text_coord
            intro_rect.x = 80
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.terminate()
                    elif event.key == pygame.K_SPACE:
                        return
            pygame.display.flip()
            self.clock.tick(self.settings.fps)

    def check_end_level(self):
        if pygame.sprite.spritecollideany(self.hero, self.enemy_group):
            self.is_game_over = True
            return True
        if pygame.sprite.spritecollideany(self.hero, self.hole_group):
            self.is_level_passed = True
            return True
        return False

    def run_level(self):
        # camera.update()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.hero.moved_up = True
                    elif event.key == pygame.K_DOWN:
                        self.hero.moved_down = True
                    elif event.key == pygame.K_LEFT:
                        self.hero.moved_left = True
                    elif event.key == pygame.K_RIGHT:
                        self.hero.moved_right = True
                    elif event.key == pygame.K_ESCAPE:
                        self.terminate()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.hero.moved_up = False
                    elif event.key == pygame.K_DOWN:
                        self.hero.moved_down = False
                    elif event.key == pygame.K_LEFT:
                        self.hero.moved_left = False
                    elif event.key == pygame.K_RIGHT:
                        self.hero.moved_right = False
            self.wall_group.update()
            self.hole_group.update()
            self.hero_group.update()
            self.enemy_group.update()
            self.camera.apply()

            self.screen.fill(pygame.Color("black"))
            self.wall_group.draw(self.screen)
            self.hole_group.draw(self.screen)
            self.hero_group.draw(self.screen)
            self.enemy_group.draw(self.screen)
            # отобразить данные на экране
            self.clock.tick(self.settings.fps)
            pygame.display.flip()

            if self.check_end_level():
                running = False

    def terminate(self):
        pygame.quit()
        sys.exit()

    def game(self):
        self.start_game_screen()
        while True:
            self.new_level()
            self.run_level()
            if self.is_game_over:
                self.reset_first_level()
                self.fall_screen()
