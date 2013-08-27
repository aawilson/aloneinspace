import os
import math
import sys

import libtcodpy as libtcod

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "lib", "python") )

import aloneinspace.game_map as game_map
import aloneinspace.keymeister as keymeister
import aloneinspace.obj as obj
import aloneinspace.rendermeister as rendermeister

SCREEN_WIDTH = 120
SCREEN_HEIGHT = 100
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 80

POLAR_CARDINALS = [
        (0, 1),
        (1, 1),
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, -1,),
        (-1, 0),
        (-1, 1),
    ]


def data_path(*args):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data", *args)


def font_path(*args):
    return data_path('fonts', *args)


if __name__ == "__main__":
    libtcod.console_set_custom_font(font_path('consolas_unicode_10x10.png'), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, 32, 64)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Alone in Space', False)

    the_map = game_map.GameMap(
        width=MAP_WIDTH,
        height=MAP_HEIGHT,
        color_dark_wall=libtcod.Color(0, 0, 100),
        color_dark_ground=libtcod.Color(50, 50, 150),
        color_light_wall=libtcod.Color(130, 110, 50),
        color_light_ground=libtcod.Color(200, 180, 50),
        color_bg=libtcod.Color(0, 0, 0),
    )

    rooms = the_map.generate(randlib=libtcod)

    player = obj.Object(
        x=rooms[0].center()[0],
        y=rooms[0].center()[1],
        char='@',
        color=libtcod.white,
        mapref=the_map,
        torch_radius=10,
    )

    cameras = []
    for room in rooms[1:]:
        cameras.append(obj.Object(
                    x=room.center()[0],
                    y=room.center()[1],
                    char='x',
                    color=libtcod.red,
                    mapref=the_map,
                    torch_radius=8,
                    fov_dir=libtcod.random_get_float(0, 0.0, 2.0 * math.pi)
                ))

    objects = [player] + cameras

    renderer = rendermeister.RenderMeister(drawlib=libtcod, fov_map=libtcod.map_new(the_map.width, the_map.height), mapref=the_map, objfocus=player, objrefs=objects)
    key_handler = keymeister.KeyMeister(keylib=libtcod)

    while not libtcod.console_is_window_closed():
        renderer.render_all()
        libtcod.console_flush()
        renderer.clear_all()

        key_handler.handle_keys()

        if key_handler.fov_recompute:
            renderer.recompute_fov()

        if key_handler.exit:
            break

        if key_handler.dx or key_handler.dy:
            player.move(key_handler.dx, key_handler.dy)
            print "Air: %s" % the_map[player.x][player.y].air

        if key_handler.switch_focus == 1:
            if renderer.objfocus == objects[-1]:
                renderer.objfocus = objects[0]
            else:
                renderer.objfocus = objects[objects.index(renderer.objfocus) + 1]
        elif key_handler.switch_focus == -1:
            if renderer.objfocus == objects[0]:
                renderer.objfocus = objects[-1]
            else:
                renderer.objfocus = objects[objects.index(renderer.objfocus) - 1]
