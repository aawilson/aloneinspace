import math

class RenderMeister(object):

    def __init__(self, drawlib, fov_map, mapref, objfocus, objrefs=None):
        if not objrefs:
            objrefs = [objfocus]
        self.objrefs = objrefs
        self.mapref = mapref
        self.drawlib = drawlib
        self.main_console = self.drawlib.console_new(mapref.width, mapref.height)
        self.objfocus = objfocus
        self.fov_recompute = True
        self.fov_map = fov_map
        self.fov_vector = None

        for y in range(self.mapref.height):
            for x in range(self.mapref.width):
                self.drawlib.map_set_properties(
                    self.fov_map,
                    x,
                    y,
                    not self.mapref[x][y].block_sight,
                    not self.mapref[x][y].blocked,
                )

    def add_objref(self, objref):
        self.objrefs.insert_sorted(objref)

    def recompute_fov(self):
        self.fov_recompute = True

    def render_all(self):
        self.drawlib.console_set_default_foreground(self.main_console, self.drawlib.white)
        if self.fov_recompute:
            self.drawlib.map_compute_fov(
                self.fov_map,
                self.objfocus.x,
                self.objfocus.y,
                self.objfocus.torch_radius,
                True,
                0,
            )

            self.fov_recompute = False

        self.draw_map()

        for ob in self.objrefs:
            self.draw_obj(ob)

        self.drawlib.console_blit(self.main_console, 0, 0, self.mapref.width, self.mapref.height, 0, 0, 0)


    def clear_all(self):
        for ob in self.objrefs:
            self.clear_obj(ob)
        self.clear_map()


    def draw_map(self):
        # see below
        # current_objref_index = 0

        for y in range(self.mapref.height):
            for x in range(self.mapref.width):
                visible = self.is_visible(x, y)

                wall = self.mapref[x][y].block_sight
                if self.mapref[x][y].explored and not visible:
                    if wall:
                        self.drawlib.console_set_char_background(
                            self.main_console,
                            x,
                            y,
                            self.mapref.color_dark_wall,
                            self.drawlib.BKGND_SET,
                        )
                    else:
                        self.drawlib.console_set_char_background(
                            self.main_console,
                            x,
                            y,
                            self.mapref.color_dark_ground,
                            self.drawlib.BKGND_SET,
                        )

                elif visible:
                    self.mapref[x][y].explored = True
                    if wall:
                        self.drawlib.console_set_char_background(
                            self.main_console,
                            x,
                            y,
                            self.mapref.color_light_wall,
                            self.drawlib.BKGND_SET,
                        )
                    else:
                        self.drawlib.console_set_char_background(
                            self.main_console,
                            x,
                            y,
                            self.mapref.color_light_ground,
                            self.drawlib.BKGND_SET,
                        )

                    # kind of an optimization, probably not needed but i'll comment it here for reference
                    # while len(self.objrefs) > current_objref_index and (self.objrefs[current_objref_index].x, self.objrefs[current_objref_index].y) == (x, y):
                    #     self.draw_obj(self.objref[current_objref_index])
                    #     current_objref_index += 1

    def clear_map(self):
        for y in range(self.mapref.height):
            for x in range(self.mapref.width):
                self.drawlib.console_set_char_background(
                    self.main_console,
                    x,
                    y,
                    self.mapref.color_bg,
                    self.drawlib.BKGND_SET,
                )

    def is_visible(self, x, y):
        visible = self.drawlib.map_is_in_fov(self.fov_map, x, y)

        if visible and self.objfocus.fov_dir:
            difference = difference_v((x, y), (self.objfocus.x, self.objfocus.y))

            # things are visible to themselves
            if difference != (0, 0):
                visible = angle_is_between(math.atan2(difference[1], difference[0]), self.objfocus.fov_dir - math.pi / 4.0, self.objfocus.fov_dir + math.pi / 4.0)

        return visible


    def draw_obj(self, objref):
        if self.is_visible(objref.x, objref.y):
            self.drawlib.console_set_default_foreground(
                self.main_console,
                objref.color,
            )
            self.drawlib.console_put_char(
                self.main_console,
                objref.x,
                objref.y,
                objref.char,
                self.drawlib.BKGND_NONE,
            )

    def clear_obj(self, objref):
        self.drawlib.console_put_char(
            self.main_console,
            objref.x,
            objref.y,
            ' ',
            self.drawlib.BKGND_NONE,
        )


def normalize_angle(angle):
    """
    takes a radian angle and normalizes it to some positive number between 0 and 2pi
    (rather than atan2's range, which is -pi to pi)
    """
    while angle < 0:
        angle = angle + 2 * math.pi

    while angle > 2 * math.pi:
        angle = angle - 2 * math.pi

    return angle


def angle_is_between(angle, start, end, inclusive=True):
    """
    check that angle is between start and end, where 'between' means
    'exists on the arc defined from start to end going CCW'
    """
    if inclusive and angle == start or angle == end:
        return True

    nangle = normalize_angle(angle)
    nstart = normalize_angle(start)
    nend = normalize_angle(end)

    if nstart < nend:
        return nstart < nangle < nend
    else:
        return nangle < nend or nangle > nstart


def difference_v(start_tuple, end_tuple):
    return (end_tuple[0] - start_tuple[0], end_tuple[1] - start_tuple[1])

def almost_equal(float1, float2, decimal_places_error_allowed=7):
    return round(float1 - float2, ndigits=decimal_places_error_allowed) == 0


if __name__ == "__main__":
    assert math.atan2(1, 1) == normalize_angle(math.atan2(1, 1))
    assert math.atan2(1, 1) == normalize_angle(2.0 * math.pi + math.atan2(1, 1))
    assert math.atan2(1, 1) == normalize_angle(-2.0 * math.pi + math.atan2(1, 1))
    assert almost_equal(math.atan2(1, 1), normalize_angle(4.0 * math.pi + math.atan2(1, 1)))
    assert almost_equal(math.atan2(1, 1), normalize_angle(-4.0 * math.pi + math.atan2(1, 1)))

    assert angle_is_between(math.atan2(1, 1), math.atan2(0, 1), math.atan2(1, 0))
    assert not angle_is_between(math.atan2(1, 1), math.atan2(1, 0), math.atan2(0, 1))
    assert angle_is_between(math.atan2(1, 0), math.atan2(0, 1), math.atan2(-1, -1))
    assert not angle_is_between(math.atan2(-1, 1), math.atan2(0, 1), math.atan2(-1, -1))
    assert angle_is_between(math.atan2(1, 1), math.atan2(1, 1), math.atan2(1, 0))
    assert not angle_is_between(math.atan2(1, 1), math.atan2(1, 1), math.atan2(1, 0), inclusive=False)