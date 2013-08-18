import game_map
import keymeister
import libtcodpy as libtcod
import obj
import rendermeister

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45


if __name__ == "__main__":
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
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

    npc = obj.Object(
        x=rooms[1].center()[0],
        y=rooms[1].center()[1],
        char='x',
        color=libtcod.red,
        mapref=the_map,
        torch_radius=1,
    )

    objects = [player, npc]

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

        if key_handler.switch_focus:
            if renderer.objfocus == objects[-1]:
                renderer.objfocus = objects[0]
            else:
                renderer.objfocus = objects[objects.index(renderer.objfocus) + 1]
