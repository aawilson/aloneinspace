class Object(object):
    def __init__(self, x, y, char, color, mapref, torch_radius=0, fov_dir=None):
        """gamelib should probably be libtcod"""
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.mapref = mapref
        self.torch_radius = torch_radius
        self.fov_dir = fov_dir

    def move(self, dx, dy):
        if not self.mapref.tiles[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
