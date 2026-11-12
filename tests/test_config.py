import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vocalsprout_app import config
from vocalsprout_app.config import AppSettings, load_settings


class ConfigTests(unittest.TestCase):
    def test_creates_default_settings_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            settings = load_settings(path)
            self.assertEqual(settings, AppSettings())
            self.assertTrue(settings.mouse_side_button_mic)
            self.assertEqual(settings.mouse_forward_action, "command")
            self.assertFalse(settings.ai_features_enabled)
            with open(path, "r", encoding="utf-8") as handle:
                stored = json.load(handle)
            self.assertEqual(stored["samplerate"], 16000)
            self.assertTrue(stored["mouse_side_button_mic"])
            self.assertEqual(stored["mouse_forward_action"], "command")
            self.assertFalse(stored["ai_features_enabled"])

    def test_preserves_valid_values_and_ignores_unknown_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"mic_device": 3, "max_record_seconds": 45, "mouse_forward_action": "command", "unknown": True}, handle)
            settings = load_settings(path)
            self.assertEqual(settings.mic_device, 3)
            self.assertEqual(settings.max_record_seconds, 45)
            self.assertEqual(settings.mouse_forward_action, "command")
            with open(path, "r", encoding="utf-8") as handle:
                self.assertNotIn("unknown", json.load(handle))

    def test_invalid_values_fall_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "samplerate": -1,
                        "silence_rms_threshold": "loud",
                        "first_run_complete": "yes",
                        "mouse_side_button_mic": "yes",
                        "mouse_forward_action": "bad-action",
                        "ai_features_enabled": "yes",
                    },
                    handle,
                )
            settings = load_settings(path)
            self.assertEqual(settings.samplerate, AppSettings().samplerate)
            self.assertEqual(settings.silence_rms_threshold, AppSettings().silence_rms_threshold)
            self.assertEqual(settings.first_run_complete, AppSettings().first_run_complete)
            self.assertEqual(settings.mouse_side_button_mic, AppSettings().mouse_side_button_mic)
            self.assertEqual(settings.mouse_forward_action, AppSettings().mouse_forward_action)
            self.assertEqual(settings.ai_features_enabled, AppSettings().ai_features_enabled)

    def test_migrates_legacy_normal_sensitivity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"silence_rms_threshold": 0.002}, handle)
            settings = load_settings(path)
            self.assertEqual(settings.silence_rms_threshold, AppSettings().silence_rms_threshold)

    def test_migrates_previous_quiet_microphone_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"silence_rms_threshold": 0.00005}, handle)
            settings = load_settings(path)
            self.assertEqual(settings.silence_rms_threshold, AppSettings().silence_rms_threshold)

    def test_load_api_key_uses_existing_environment_value(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "from-environment"}, clear=False), patch("vocalsprout_app.config._migrate_credential") as migrate:
            self.assertEqual(config.load_api_key(), "from-environment")
        migrate.assert_not_called()

    def test_load_api_key_migrates_legacy_plain_text_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.env")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("GROQ_API_KEY=legacy-secret\n")
            with patch.dict(os.environ, {}, clear=True), patch("vocalsprout_app.config._migrate_credential", return_value=None), patch("vocalsprout_app.config._write_credential") as write:
                self.assertEqual(config.load_api_key(path), "legacy-secret")
                self.assertEqual(os.environ["GROQ_API_KEY"], "legacy-secret")
            write.assert_called_once_with("legacy-secret")
            self.assertTrue(os.path.exists(path))

    def test_migrates_aylo_settings_without_deleting_original(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy_dir = os.path.join(directory, "Aylo")
            vocalsprout_dir = os.path.join(directory, "VOCALSPROUT")
            os.makedirs(legacy_dir)
            legacy_settings = os.path.join(legacy_dir, "config.json")
            new_settings = os.path.join(vocalsprout_dir, "config.json")
            with open(legacy_settings, "w", encoding="utf-8") as handle:
                json.dump({"mic_device": 7, "first_run_complete": True}, handle)
            with patch.object(config, "SETTINGS_FILE", new_settings), patch.object(config, "LEGACY_SETTINGS_FILE", legacy_settings):
                settings = config.load_settings(config.SETTINGS_FILE)
            self.assertEqual(settings.mic_device, 7)
            self.assertTrue(settings.first_run_complete)
            self.assertTrue(os.path.exists(legacy_settings))
            self.assertTrue(os.path.exists(new_settings))

    def test_migrates_history_oauth_and_knowledge_without_deleting_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy_dir = os.path.join(directory, "Aylo")
            vocalsprout_dir = os.path.join(directory, "VOCALSPROUT")
            legacy_history = os.path.join(legacy_dir, "history.json")
            legacy_oauth = os.path.join(legacy_dir, "google_oauth_client.json")
            legacy_knowledge = os.path.join(legacy_dir, "knowledge")
            new_history = os.path.join(vocalsprout_dir, "history.json")
            new_oauth = os.path.join(vocalsprout_dir, "google_oauth_client.json")
            new_knowledge = os.path.join(vocalsprout_dir, "knowledge")
            os.makedirs(legacy_knowledge)
            with open(legacy_history, "w", encoding="utf-8") as handle:
                handle.write("[]")
            with open(legacy_oauth, "w", encoding="utf-8") as handle:
                handle.write('{"client_id": "legacy"}')
            with open(os.path.join(legacy_knowledge, "gmail.sqlite3"), "wb") as handle:
                handle.write(b"legacy-index")
            with patch.object(config, "legacy_appdata_dir", return_value=legacy_dir), patch.object(
                config, "voiceflow_appdata_dir", return_value=os.path.join(directory, "VoiceFlow")
            ), patch.object(config, "LEGACY_HISTORY_FILE", legacy_history), patch.object(
                config, "HISTORY_FILE", new_history
            ), patch.object(config, "GMAIL_CLIENT_SECRET_FILE", new_oauth), patch.object(
                config, "LEGACY_KNOWLEDGE_DIR", legacy_knowledge
            ), patch.object(config, "KNOWLEDGE_DIR", new_knowledge):
                config.migrate_legacy_appdata()
            self.assertTrue(os.path.exists(legacy_history))
            self.assertTrue(os.path.exists(legacy_oauth))
            self.assertTrue(os.path.exists(os.path.join(legacy_knowledge, "gmail.sqlite3")))
            self.assertTrue(os.path.exists(new_history))
            self.assertTrue(os.path.exists(new_oauth))
            self.assertEqual(Path(new_knowledge, "gmail.sqlite3").read_bytes(), b"legacy-index")

    def test_does_not_overwrite_existing_vocalsprout_knowledge_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy_dir = os.path.join(directory, "Aylo", "knowledge")
            vocalsprout_dir = os.path.join(directory, "VOCALSPROUT", "knowledge")
            os.makedirs(legacy_dir)
            os.makedirs(vocalsprout_dir)
            with open(os.path.join(legacy_dir, "gmail.sqlite3"), "wb") as handle:
                handle.write(b"legacy-index")
            with open(os.path.join(vocalsprout_dir, "gmail.sqlite3"), "wb") as handle:
                handle.write(b"current-index")
            self.assertFalse(config._copy_legacy_directory(legacy_dir, vocalsprout_dir))
            self.assertEqual(Path(vocalsprout_dir, "gmail.sqlite3").read_bytes(), b"current-index")

    def test_migrates_aylo_credential_without_deleting_old_target(self):
        with patch("vocalsprout_app.config.read_credential", side_effect=[None, "old-secret"]), patch(
            "vocalsprout_app.config.write_credential"
        ) as write:
            self.assertEqual(
                config._migrate_credential(config.CREDENTIAL_TARGET, config.LEGACY_CREDENTIAL_TARGET),
                "old-secret",
            )
        write.assert_called_once_with(config.CREDENTIAL_TARGET, "old-secret")

    def test_save_api_key_uses_credential_manager_and_removes_current_plain_text_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.env")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("GROQ_API_KEY=old-secret\n")
            with patch.dict(os.environ, {}, clear=True), patch("vocalsprout_app.config._write_credential") as write:
                config.save_api_key("new-secret", path)
                self.assertEqual(os.environ["GROQ_API_KEY"], "new-secret")
            write.assert_called_once_with("new-secret")
            self.assertFalse(os.path.exists(path))

    def test_write_credential_uses_windows_credential_manager(self):
        with patch("win32cred.CredWrite") as cred_write:
            config._write_credential("secret")
        credential, flags = cred_write.call_args.args
        self.assertEqual(flags, 0)
        self.assertEqual(credential["TargetName"], config.CREDENTIAL_TARGET)
        self.assertEqual(credential["CredentialBlob"], "secret")

    def test_missing_windows_credential_is_treated_as_not_configured(self):
        missing = RuntimeError("Element not found.")
        missing.winerror = 1168
        with patch("win32cred.CredRead", side_effect=missing):
            self.assertIsNone(config._read_credential())

    def test_app_name_and_credential_targets_are_vocalsprout(self):
        self.assertEqual(config.APP_NAME, "VOCALSPROUT")
        self.assertEqual(config.CREDENTIAL_TARGET, "VOCALSPROUT/GroqApiKey")
        self.assertEqual(config.LEGACY_CREDENTIAL_TARGET, "Aylo/GroqApiKey")
        self.assertEqual(config.VOICEFLOW_CREDENTIAL_TARGET, "VoiceFlow/GroqApiKey")

    def test_credential_migration_falls_back_to_voiceflow_target(self):
        with patch("vocalsprout_app.config.read_credential", side_effect=[None, None, "voiceflow-secret"]) as read, patch(
            "vocalsprout_app.config.write_credential"
        ) as write:
            self.assertEqual(
                config._migrate_credential(
                    config.CREDENTIAL_TARGET, config.LEGACY_CREDENTIAL_TARGET, config.VOICEFLOW_CREDENTIAL_TARGET
                ),
                "voiceflow-secret",
            )
        self.assertEqual(
            [call.args[0] for call in read.call_args_list],
            ["VOCALSPROUT/GroqApiKey", "Aylo/GroqApiKey", "VoiceFlow/GroqApiKey"],
        )
        write.assert_called_once_with("VOCALSPROUT/GroqApiKey", "voiceflow-secret")

    def test_aylo_credential_wins_over_voiceflow_target(self):
        with patch("vocalsprout_app.config.read_credential", side_effect=[None, "aylo-secret"]) as read, patch(
            "vocalsprout_app.config.write_credential"
        ):
            self.assertEqual(
                config._migrate_credential(
                    config.CREDENTIAL_TARGET, config.LEGACY_CREDENTIAL_TARGET, config.VOICEFLOW_CREDENTIAL_TARGET
                ),
                "aylo-secret",
            )
        self.assertEqual(read.call_count, 2)

    def test_aylo_data_wins_over_voiceflow_data_and_plugins_migrate(self):
        with tempfile.TemporaryDirectory() as directory:
            aylo_dir = os.path.join(directory, "Aylo")
            voiceflow_dir = os.path.join(directory, "VoiceFlow")
            new_dir = os.path.join(directory, "VOCALSPROUT")
            os.makedirs(os.path.join(aylo_dir, "plugins"))
            os.makedirs(voiceflow_dir)
            os.makedirs(new_dir)
            Path(aylo_dir, "config.json").write_text('{"mic_device": 3}', encoding="utf-8")
            Path(voiceflow_dir, "config.json").write_text('{"mic_device": 9}', encoding="utf-8")
            Path(aylo_dir, "plugins", "custom.json").write_text("{}", encoding="utf-8")
            new_plugins = os.path.join(new_dir, "plugins")
            os.makedirs(new_plugins)  # empty folder created at startup must not block migration
            with patch.object(config, "SETTINGS_FILE", os.path.join(new_dir, "config.json")), patch.object(
                config, "HISTORY_FILE", os.path.join(new_dir, "history.json")
            ), patch.object(config, "GMAIL_CLIENT_SECRET_FILE", os.path.join(new_dir, "google_oauth_client.json")), patch.object(
                config, "KNOWLEDGE_DIR", os.path.join(new_dir, "knowledge")
            ), patch.object(config, "PLUGINS_DIR", new_plugins), patch.object(
                config, "LEGACY_SETTINGS_FILE", os.path.join(aylo_dir, "config.json")
            ), patch.object(config, "LEGACY_PLUGINS_DIR", os.path.join(aylo_dir, "plugins")), patch.object(
                config, "VOICEFLOW_SETTINGS_FILE", os.path.join(voiceflow_dir, "config.json")
            ), patch.object(config, "legacy_appdata_dir", return_value=aylo_dir), patch.object(
                config, "voiceflow_appdata_dir", return_value=voiceflow_dir
            ):
                config.migrate_legacy_appdata()
            self.assertEqual(json.loads(Path(new_dir, "config.json").read_text(encoding="utf-8"))["mic_device"], 3)
            self.assertTrue(Path(new_plugins, "custom.json").exists())
            self.assertTrue(Path(aylo_dir, "config.json").exists())


if __name__ == "__main__":
    unittest.main()
