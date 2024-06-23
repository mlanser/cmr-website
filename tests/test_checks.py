import sys
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase, override_settings

from CMR.checks import check_dev_mode


def mock_dev_mode(value):
    return mock.patch.object(
        sys,
        'flags',
        SimpleNamespace(dev_mode=value),
    )


class CheckDevModeTests(SimpleTestCase):
    def test_success_dev_mode(self):
        with override_settings(DEBUG=True), mock_dev_mode(True):
            result = check_dev_mode()

        self.assertEqual(result, [])

    def test_success_not_debug(self):
        with override_settings(DEBUG=False), mock_dev_mode(False):
            result = check_dev_mode()

        self.assertEqual(result, [])

    def test_fail_not_dev_mode(self):
        with override_settings(DEBUG=True), mock_dev_mode(False):
            result = check_dev_mode()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 'CMR.W001')
