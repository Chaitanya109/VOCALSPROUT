import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import release


class ReleaseTests(unittest.TestCase):
    def test_sha256_is_uppercase(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.bin"
            path.write_bytes(b"VOCALSPROUT")
            self.assertEqual(
                release.sha256(path),
                "C40D8F13640C3A581B14474B7A6D6E97798DC6B6A7E75DDDD5C49147C92E6D4A",
            )

    def test_find_inno_setup_uses_configured_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ISCC.exe"
            path.write_bytes(b"")
            with patch.dict(os.environ, {"VOCALSPROUT_ISCC": str(path)}, clear=False), patch("release.shutil.which", return_value=None):
                self.assertEqual(release.find_inno_setup(), str(path))

    def test_find_inno_setup_still_honours_legacy_aylo_variable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ISCC.exe"
            path.write_bytes(b"")
            with patch.dict(os.environ, {"AYLO_ISCC": str(path)}, clear=True), patch("release.shutil.which", return_value=None):
                self.assertEqual(release.find_inno_setup(), str(path))

    def test_release_artifacts_use_vocalsprout_names(self):
        self.assertEqual(release.DIST_EXE.name, "VOCALSPROUT.exe")
        self.assertEqual(release.INNO_SCRIPT.name, "VOCALSPROUT.iss")
        self.assertTrue(release.PORTABLE_ZIP.name.startswith("VOCALSPROUT-"))

    def test_sign_is_optional_without_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(release.sign(Path("VOCALSPROUT.exe")))

    def test_find_inno_setup_supports_user_local_install(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Programs" / "Inno Setup 6" / "ISCC.exe"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"")
            with patch.dict(os.environ, {"LOCALAPPDATA": directory}, clear=True), patch("release.shutil.which", return_value=None):
                self.assertEqual(release.find_inno_setup(), str(path))


if __name__ == "__main__":
    unittest.main()
