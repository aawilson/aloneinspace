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
        color_light_wall,
        color_light_ground,
        color_bg,
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
        self.color_light_ground = color_light_ground
        self.color_light_wall = color_light_wall
        self.color_bg = color_bg
        self.room_max_size = room_max_size
        self.room_min_size = room_min_size
        self.max_rooms = max_rooms

        self.tiles = [[Tile(False)
                for y in range(self.height)]
            for x in range(width)]

    def __getitem__(self, i):
        return self.tiles[i]

    def draw(self, fov_map):
        for y in range(self.height):
            for x in range(self.width):
                visible = self._gamelib.map_is_in_fov(fov_map, x, y)
                wall = self[x][y].block_sight
                if self[x][y].explored and not visible:
                    if wall:
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
                elif visible:
                    self[x][y].explored = True
                    if wall:
                        self._gamelib.console_set_char_background(
                            self._console,
                            x,
                            y,
                            self.color_light_wall,
                            self._gamelib.BKGND_SET,
                        )
                    else:
                        self._gamelib.console_set_char_background(
                            self._console,
                            x,
                            y,
                            self.color_light_ground,
                            self._gamelib.BKGND_SET,
                        )

    def generate(self):
        rooms = []
        start_room = None

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
                    self.color_bg,
                    self._gamelib.BKGND_SET,
                )


class Tile(object):
    def __init__(
        self,
        blocked,
        block_sight=None,
        air=False,
    ):
        self.blocked = blocked
        if block_sight is None:
            self.block_sight = blocked
        else:
            self.block_sight = block_sight
        self.explored = False
        self.air=air


def create_room(the_map, room):
    for x in range(room.x1, room.x2 + 1):
        for y in range(room.y1, room.y2 + 1):
            if not the_map[x][y].air:
                the_map[x][y].blocked = True
                the_map[x][y].block_sight = True

    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            the_map[x][y].blocked = False
            the_map[x][y].block_sight = False
            the_map[x][y].air = True


def create_h_tunnel(the_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        the_map[x][y].blocked = False
        the_map[x][y].block_sight = False
        the_map[x][y].air = True

        if not the_map[x][y - 1].air:
            the_map[x][y - 1].blocked = True
            the_map[x][y - 1].block_sight = True

        if not the_map[x][y + 1].air:
            the_map[x][y + 1].blocked = True
            the_map[x][y + 1].block_sight = True
    for y in range(y-1, y + 2):
        x = min(x1, x2) - 1
        if not the_map[x][y].air:
            the_map[x][y].blocked = True
            the_map[x][y].block_sight = True

        x = max(x1, x2) + 1
        if not the_map[x][y].air:
            the_map[x][y].blocked = True
            the_map[x][y].block_sight = True


def create_v_tunnel(the_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        the_map[x][y].blocked = False
        the_map[x][y].block_sight = False
        the_map[x][y].air = True

        if not the_map[x + 1][y].air:
            the_map[x + 1][y].blocked = True
            the_map[x + 1][y].block_sight = True

        if not the_map[x - 1][y].air:
            the_map[x - 1][y].blocked = True
            the_map[x - 1][y].block_sight = True

    for x in range(x-1, x + 2):
        y = min(y1, y2) - 1
        if not the_map[x][y].air:
            the_map[x][y].blocked = True
            the_map[x][y].block_sight = True

        y = max(y1, y2) + 1
        if not the_map[x][y].air:
            the_map[x][y].blocked = True
            the_map[x][y].block_sight = True
