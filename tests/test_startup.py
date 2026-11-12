import unittest
from unittest.mock import Mock, patch

from vocalsprout_app import startup


class StartupTests(unittest.TestCase):
    def test_launch_command_uses_executable_for_packaged_app(self):
        with patch.object(startup.sys, "frozen", True, create=True), patch.object(startup.sys, "executable", r"C:\Apps\VOCALSPROUT.exe"):
            self.assertEqual(startup.launch_command(), r'"C:\Apps\VOCALSPROUT.exe"')

    def test_missing_registry_value_means_disabled(self):
        with patch.object(startup.winreg, "OpenKey", side_effect=FileNotFoundError):
            self.assertFalse(startup.is_startup_enabled())

    def test_enable_writes_current_launch_command(self):
        key = Mock()
        key.__enter__ = Mock(return_value=key)
        key.__exit__ = Mock(return_value=False)
        with patch.object(startup.winreg, "CreateKey", return_value=key), patch.object(startup.winreg, "SetValueEx") as set_value, patch.object(startup, "launch_command", return_value='"VOCALSPROUT.exe"'), patch.object(startup, "_remove_value") as remove_value:
            startup.set_startup_enabled(True)
        set_value.assert_called_once_with(key, startup.VALUE_NAME, 0, startup.winreg.REG_SZ, '"VOCALSPROUT.exe"')
        remove_value.assert_called_once_with(startup.LEGACY_VALUE_NAME)

    def test_disable_removes_current_and_legacy_aylo_entries(self):
        with patch.object(startup, "_remove_value") as remove_value:
            startup.set_startup_enabled(False)
        remove_value.assert_any_call(startup.VALUE_NAME)
        remove_value.assert_any_call(startup.LEGACY_VALUE_NAME)

    def test_startup_entry_is_named_vocalsprout(self):
        self.assertEqual(startup.VALUE_NAME, "VOCALSPROUT")
        self.assertEqual(startup.LEGACY_VALUE_NAME, "Aylo")

    def test_disable_ignores_missing_registry_value(self):
        with patch.object(startup.winreg, "OpenKey", side_effect=FileNotFoundError):
            startup.set_startup_enabled(False)


if __name__ == "__main__":
    unittest.main()
