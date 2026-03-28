from screenshot_ocr.hotkeys import DEFAULT_HOTKEY, HotkeyListener, normalize_hotkey


class FakeKeyboard:
    def __init__(self):
        self.calls = []

    def add_hotkey(self, hotkey, callback):
        self.calls.append(("add_hotkey", hotkey, callback))

    def on_press_key(self, hotkey, callback):
        self.calls.append(("on_press_key", hotkey, callback))

    def on_release_key(self, hotkey, callback):
        self.calls.append(("on_release_key", hotkey, callback))

    def unhook_all(self):
        self.calls.append(("unhook_all",))

    def clear_hotkeys(self):
        self.calls.append(("clear_hotkeys",))


class FakeTime:
    def __init__(self, values):
        self.values = iter(values)

    def time(self):
        return next(self.values)


def test_normalize_hotkey_rejects_unsupported_values():
    assert normalize_hotkey("mouse4") == DEFAULT_HOTKEY
    assert normalize_hotkey("not-a-key") == DEFAULT_HOTKEY


def test_hotkey_listener_registers_combo_hotkey():
    keyboard = FakeKeyboard()
    listener = HotkeyListener(
        hotkey="ctrl+e",
        mode="instant",
        long_press_time=1.0,
        on_trigger=lambda: None,
        keyboard_module=keyboard,
    )

    listener.start()

    assert keyboard.calls[0][0] == "add_hotkey"
    assert keyboard.calls[0][1] == "ctrl+e"


def test_hotkey_listener_triggers_after_long_press():
    keyboard = FakeKeyboard()
    triggered = []
    listener = HotkeyListener(
        hotkey="f9",
        mode="long_press",
        long_press_time=1.0,
        on_trigger=lambda: triggered.append(True),
        keyboard_module=keyboard,
        time_module=FakeTime([10.0, 11.5]),
    )

    listener.on_key_press(None)
    listener.on_key_release(None)

    assert triggered == [True]
