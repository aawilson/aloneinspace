class KeyMeister(object):

    def __init__(self, keylib):
        self.keylib = keylib
        # TODO: states_handled will be passed in, along with handlers for keys
        self.states_handled = {
            'fov_recompute': bool,
            'switch_focus': int,
            'dx': int,
            'dy': int,
            'fullscreen': bool,
            'exit': bool,
        }

    def handle_keys(self):
        self.clear_key_state()
        key = self.keylib.console_wait_for_keypress(True)

        if key.vk == self.keylib.KEY_ENTER and key.lalt:
            self.fullscreen = True
            self.keylib.console_set_fullscreen(not self.keylib.console_is_fullscreen())
        elif key.vk == self.keylib.KEY_ESCAPE:
            self.exit = True

        if key.vk == self.keylib.KEY_UP or key.vk == self.keylib.KEY_CHAR and key.c in [ord('k'), ord('y'), ord('u')]:
            self.dy = -1
            self.fov_recompute = True
        elif key.vk == self.keylib.KEY_DOWN or key.vk == self.keylib.KEY_CHAR and key.c in [ord('j'), ord('n'), ord('b')]:
            self.dy = 1
            self.fov_recompute = True

        if key.vk == self.keylib.KEY_LEFT or key.vk == self.keylib.KEY_CHAR and key.c in [ord('h'), ord('y'), ord('b')]:
            self.dx = -1
            self.fov_recompute = True
        elif key.vk == self.keylib.KEY_RIGHT or key.vk == self.keylib.KEY_CHAR and key.c in [ord('l'), ord('u'), ord('n')]:
            self.dx = 1
            self.fov_recompute = True

        if key.vk == self.keylib.KEY_TAB:
            if key.shift:
                self.switch_focus = -1
                self.fov_recompute = True
            else:
                self.switch_focus = 1
                self.fov_recompute = True

        return

    def clear_key_state(self):
        for state, state_type in self.states_handled.iteritems():
            setattr(self, state, state_type())
