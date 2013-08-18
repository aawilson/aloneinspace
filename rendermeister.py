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

    def set_focus(self, objfocus):
        self.objfocus = objfocus

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
                visible = self.drawlib.map_is_in_fov(self.fov_map, x, y)
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

    def draw_obj(self, objref):
        if self.drawlib.map_is_in_fov(self.fov_map, objref.x, objref.y):
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
