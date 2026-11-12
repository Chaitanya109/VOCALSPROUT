import unittest
from unittest.mock import Mock, call, patch

from vocalsprout_app.app import VocalsproutApp
from vocalsprout_app.config import AppSettings


class AppClipboardPasteTests(unittest.TestCase):
    def make_app(self):
        with patch("vocalsprout_app.app.load_settings", return_value=AppSettings()), patch("vocalsprout_app.app.HistoryStore"):
            app = VocalsproutApp()
        app.log_error = Mock()
        return app

    def test_paste_restores_previous_clipboard(self):
        app = self.make_app()
        with patch("pyperclip.paste", return_value="copied source"), patch("pyperclip.copy") as copy, patch("pyautogui.hotkey") as hotkey, patch("pyautogui.keyUp") as key_up, patch("vocalsprout_app.app.time.sleep"):
            app._paste_text_preserving_clipboard("generated answer", release_keys=("ctrl", "space"))

        self.assertEqual(copy.call_args_list, [call("generated answer"), call("copied source")])
        hotkey.assert_called_once_with("ctrl", "v")
        self.assertEqual(key_up.call_args_list, [call("ctrl"), call("space")])
        self.assertFalse(app.state.is_pasting)

    def test_paste_restores_clipboard_after_hotkey_failure(self):
        app = self.make_app()
        with patch("pyperclip.paste", return_value="copied source"), patch("pyperclip.copy") as copy, patch("pyautogui.hotkey", side_effect=RuntimeError("paste failed")), patch("vocalsprout_app.app.time.sleep"):
            with self.assertRaisesRegex(RuntimeError, "paste failed"):
                app._paste_text_preserving_clipboard("generated answer")

        self.assertEqual(copy.call_args_list, [call("generated answer"), call("copied source")])
        self.assertFalse(app.state.is_pasting)


if __name__ == "__main__":
    unittest.main()
