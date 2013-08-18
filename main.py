import libtcodpy as libtcod
import obj
import game_map
import rendermeister

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45

def handle_keys():
    key = libtcod.console_wait_for_keypress(True)
    dx, dy = 0, 0
    fov_recompute = False

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return True, dx, dy, fov_recompute

    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_CHAR and key.c in [ord('k'), ord('y'), ord('u')]:
        dy = -1
        fov_recompute = True
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_CHAR and key.c in [ord('j'), ord('n'), ord('b')]:
        dy = 1
        fov_recompute = True

    if key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_CHAR and key.c in [ord('h'), ord('y'), ord('b')]:
        dx = -1
        fov_recompute = True
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_CHAR and key.c in [ord('l'), ord('u'), ord('n')]:
        dx = 1
        fov_recompute = True

    return False, dx, dy, fov_recompute


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

    start_room = the_map.generate(randlib=libtcod)

    player = obj.Object(
        x=start_room.center()[0],
        y=start_room.center()[1],
        char='@',
        color=libtcod.white,
        mapref=the_map,
        torch_radius=10,
    )

    objects = [player]

    renderer = rendermeister.RenderMeister(drawlib=libtcod, fov_map=libtcod.map_new(the_map.width, the_map.height), mapref=the_map, objfocus=player, objrefs=objects)

    while not libtcod.console_is_window_closed():
        dx, dy = 0, 0

        renderer.render_all()
        libtcod.console_flush()
        renderer.clear_all()

        exit, dx, dy, fov_recompute = handle_keys()

        if fov_recompute:
            renderer.recompute_fov()

        if exit:
            break

        if dx or dy:
            player.move(dx, dy)
            print "Air: %s" % the_map[player.x][player.y].air
