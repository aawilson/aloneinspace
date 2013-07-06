class Object(object):
    def __init__(self, gamelib, console, x, y, char, color, the_map):
        """gamelib should probably be libtcod"""
        self._gamelib = gamelib
        self._con = console
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.the_map = the_map

    def move(self, dx, dy):
        if not self.the_map.tiles[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        self._gamelib.console_set_default_foreground(
            self._con,
            self.color,
        )
        self._gamelib.console_put_char(
            self._con,
            self.x,
            self.y,
            self.char,
            self._gamelib.BKGND_NONE,
        )

    def clear(self):
        self._gamelib.console_put_char(
            self._con,
            self.x,
            self.y,
            ' ',
            self._gamelib.BKGND_NONE,
        )
