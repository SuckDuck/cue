from pynput import keyboard

class KeyboardInput:
    def __init__(self):
        self.down = set()
        self.prev = set()

        def on_press(key):
            self.down.add(key)

        def on_release(key):
            self.down.discard(key)

        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )

        self.listener.start()

    def _parse_keys(self, keys):
        if len(keys) == 1 and isinstance(keys[0], (list, tuple, set)):
            keys = keys[0]

        return [
            keyboard.KeyCode.from_char(k) if isinstance(k, str) else k
            for k in keys
        ]

    def is_down(self, *keys):
        keys = self._parse_keys(keys)
        return all(key in self.down for key in keys)

    def is_up(self, *keys):
        return not self.is_down(*keys)

    def is_pressed(self, *keys):
        keys = self._parse_keys(keys)
        return all(key in self.down for key in keys) and any(
            key in self.down and key not in self.prev
            for key in keys
        )

    def is_released(self, *keys):
        keys = self._parse_keys(keys)
        return all(key not in self.down and key in self.prev for key in keys)

    def update(self):
        self.prev = self.down.copy()

    def close(self):
        self.listener.stop()
