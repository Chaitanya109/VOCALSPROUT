import os
import unittest
from unittest.mock import patch

from vocalsprout_app import subscription


class SubscriptionTests(unittest.TestCase):
    def test_checkout_url_uses_default_pricing_page(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(subscription.checkout_url(), subscription.CHECKOUT_URL)

    def test_checkout_url_can_be_configured_for_real_checkout(self):
        with patch.dict(os.environ, {"VOCALSPROUT_CHECKOUT_URL": "https://pay.example.com/vocalsprout"}):
            self.assertEqual(subscription.checkout_url(), "https://pay.example.com/vocalsprout")

    def test_checkout_url_still_honours_legacy_aylo_variable(self):
        with patch.dict(os.environ, {"AYLO_CHECKOUT_URL": "https://pay.example.com/old"}, clear=True):
            self.assertEqual(subscription.checkout_url(), "https://pay.example.com/old")

    def test_open_checkout_opens_configured_url(self):
        with patch.dict(os.environ, {"VOCALSPROUT_CHECKOUT_URL": "https://pay.example.com/vocalsprout"}), patch(
            "webbrowser.open", return_value=True
        ) as browser_open:
            self.assertTrue(subscription.open_checkout())
        browser_open.assert_called_once_with("https://pay.example.com/vocalsprout")

    def test_open_checkout_is_disabled_without_configured_url(self):
        with patch.dict(os.environ, {}, clear=True), patch("webbrowser.open") as browser_open:
            self.assertFalse(subscription.open_checkout())
        browser_open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
