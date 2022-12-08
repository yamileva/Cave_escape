import pygame


class Point:
    def __init__(self, x, y=None):
        if y is None:
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __mul__(self, value):
        return Point(self.x * value, self.y * value)

    def __call__(self):
        return self.x, self.y


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, game, group, x, y, image):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pygame.Rect((x, y, game.settings.cell_size, game.settings.cell_size)).center
        self.map_pos = Point(x, y)

    def get_event(self, event):
        pass

    def update(self):
        pass


class Tile(Sprite):
    def __init__(self, game, group, x, y, image):
        super().__init__(game, group, x, y, image)

    def update(self):
        pass


class MovedSprite(Sprite):
    def __init__(self, game, group, x, y, image):
        super().__init__(game, group, x, y, image)
        self.game = game

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)
        self.map_pos += Point(dx, dy)
        if pygame.sprite.spritecollideany(self, self.game.wall_group):
            self.rect.move_ip(-dx, -dy)
            self.map_pos -= Point(dx, dy)
            return False
        return True


class Player(MovedSprite):
    def __init__(self, game, group, x, y, image, speed):
        super().__init__(game, group, x, y, image)
        self.speed = speed
        self.moved_left = False
        self.moved_right = False
        self.moved_up = False
        self.moved_down = False

    def update(self):
        if self.moved_left:
            self.move(-self.speed, 0)
        if self.moved_right:
            self.move(self.speed, 0)
        if self.moved_up:
            self.move(0, -self.speed)
        if self.moved_down:
            self.move(0, self.speed)


class Enemy(MovedSprite):
    def __init__(self, game, group, x, y, image, speed, direction):
        super().__init__(game, group, x, y, image)
        self.velocity = Point(direction) * speed

    def update(self):
        if not self.move(*self.velocity()):
            self.velocity = -self.velocity

