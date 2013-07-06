import poly


class Map(object):
    def __init__(
        self,
        gamelib,
        console,
        width,
        height,
        color_dark_wall,
        color_dark_ground,
        room_max_size=10,
        room_min_size=6,
        max_rooms=30,
    ):
        self._gamelib = gamelib
        self._console = console
        self.width = width
        self.height = height
        self.color_dark_ground = color_dark_ground
        self.color_dark_wall = color_dark_wall
        self.room_max_size = room_max_size
        self.room_min_size = room_min_size
        self.max_rooms = max_rooms

        self.tiles = [[Tile(True)
                for y in range(self.height)]
            for x in range(width)]

    def __getitem__(self, i):
        return self.tiles[i]

    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                if self[x][y].block_sight:
                    self._gamelib.console_set_char_background(
                        self._console,
                        x,
                        y,
                        self.color_dark_wall,
                        self._gamelib.BKGND_SET,
                    )
                else:
                    self._gamelib.console_set_char_background(
                        self._console,
                        x,
                        y,
                        self.color_dark_ground,
                        self._gamelib.BKGND_SET,
                    )

    def generate(self):
        rooms = []
        start_room = None

        print("HERE: %s" % (self.room_min_size))
        for r in range(self.max_rooms):
            w = self._gamelib.random_get_int(
                0,
                self.room_min_size,
                self.room_max_size,
            )
            h = self._gamelib.random_get_int(
                0,
                self.room_min_size,
                self.room_max_size,
            )
            x = self._gamelib.random_get_int(
                0,
                0,
                self.width - w - 1,
            )
            y = self._gamelib.random_get_int(
                0,
                0,
                self.height - h - 1,
            )

            new_room = poly.Rect(x, y, w, h)
            new_x, new_y = new_room.center()
            failed = False
            for other_room in rooms:
                if new_room.intersects(other_room):
                    failed = True
                    break

            if not failed:
                create_room(self, new_room)
                if len(rooms) == 0:
                    start_room = new_room
                else:
                    (prev_x, prev_y) = rooms[-1].center()

                    if self._gamelib.random_get_int(0, 0, 1) == 1:
                        create_h_tunnel(self, prev_x, new_x, prev_y)
                        create_v_tunnel(self, prev_y, new_y, new_x)
                    else:
                        create_h_tunnel(self, prev_x, new_x, new_y)
                        create_v_tunnel(self, prev_y, new_y, prev_x)

                rooms.append(new_room)

        return start_room

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self._gamelib.console_set_char_background(
                    self._console,
                    x,
                    y,
                    self.color_dark_ground,
                    self._gamelib.BKGND_SET,
                )


class Tile(object):
    def __init__(
        self,
        blocked,
        block_sight=None,
    ):
        self.blocked = blocked
        if block_sight is None:
            self.block_sight = blocked
        else:
            self.block_sight = block_sight


def create_room(the_map, room):
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            the_map[x][y].blocked = False
            the_map[x][y].block_sight = False


def create_h_tunnel(the_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        the_map[x][y].blocked = False
        the_map[x][y].block_sight = False


def create_v_tunnel(the_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        the_map[x][y].blocked = False
        the_map[x][y].block_sight = False
