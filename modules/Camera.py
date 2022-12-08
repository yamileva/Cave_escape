class Camera:
    def __init__(self, target, sprite_groups, settings):
        self.settings = settings
        self.target = target
        self.objects_groups = sprite_groups
        self.is_enabled_x = False
        self.is_enabled_y = False

    def checkTarget(self):
        self.is_enabled_x = self.target.map_pos.x > self.settings.screen_rect.centerx and \
            (self.settings.map_rect.h - self.target.map_pos.x) > self.settings.screen_rect.centerx
        self.is_enabled_y = self.target.map_pos.y > self.settings.screen_rect.centery and \
            (self.settings.map_rect.w - self.target.map_pos.y) > self.settings.screen_rect.centery

    def apply(self):
        self.checkTarget()
        if self.is_enabled_x:
            dx = -(self.target.rect.centerx - self.settings.screen_rect.centerx)
            for group in self.objects_groups:
                for tile in group:
                    tile.rect.x += dx
            self.target.rect.centerx = self.settings.screen_rect.centerx
        if self.is_enabled_y:
            dy = -(self.target.rect.centery - self.settings.screen_rect.centery)
            for group in self.objects_groups:
                for tile in group:
                    tile.rect.y += dy
            self.target.rect.centery = self.settings.screen_rect.centery

