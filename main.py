import libtcodpy as libtcod
import obj
import game_map

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


def render_all(objects, the_map, fov_map, fov_recompute):
    if fov_recompute:
        libtcod.map_compute_fov(
            fov_map,
            objects[0].x,
            objects[0].y,
            objects[0].torch_radius,
            True,
            0,
        )
    for ob in objects:
        ob.draw(fov_map)
    the_map.draw(fov_map)

    libtcod.console_blit(main_console, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


def clear_all(objects, the_map):
    for ob in objects:
        ob.clear()
    the_map.clear()


if __name__ == "__main__":
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Alone in Space', False)
    main_console = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    the_map = game_map.Map(
        gamelib=libtcod,
        console=main_console,
        width=MAP_WIDTH,
        height=MAP_HEIGHT,
        color_dark_wall=libtcod.Color(0, 0, 100),
        color_dark_ground=libtcod.Color(50, 50, 150),
        color_light_wall=libtcod.Color(130, 110, 50),
        color_light_ground=libtcod.Color(200, 180, 50),
        color_bg=libtcod.Color(0, 0, 0),
    )

    start_room = the_map.generate()

    fov_map = libtcod.map_new(the_map.width, the_map.height)
    fov_recompute = True
    for y in range(the_map.height):
        for x in range(the_map.width):
            libtcod.map_set_properties(
                fov_map,
                x,
                y,
                not the_map[x][y].block_sight,
                not the_map[x][y].blocked,
            )

    player = obj.Object(
        gamelib=libtcod,
        console=main_console,
        x=start_room.center()[0],
        y=start_room.center()[1],
        char='@',
        color=libtcod.white,
        the_map=the_map,
        torch_radius=10,
    )

    # npc = obj.Object(
    #     gamelib=libtcod,
    #     console=main_console,
    #     x=player.x - 5,
    #     y=player.y,
    #     char='@',
    #     color=libtcod.yellow,
    #     the_map=the_map,
    # )

    objects = [player]

    while not libtcod.console_is_window_closed():
        dx, dy = 0, 0
        libtcod.console_set_default_foreground(main_console, libtcod.white)

        render_all(objects, the_map, fov_map, fov_recompute)
        libtcod.console_flush()
        clear_all(objects, the_map)

        exit, dx, dy, fov_recompute = handle_keys()

        if exit:
            break

        if dx or dy:
            player.move(dx, dy)
            print "Air: %s" % the_map[player.x][player.y].air
