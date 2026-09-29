from __future__ import annotations

import unittest

from ..client import SITE_URL, site_url_for


class TestSiteUrl(unittest.TestCase):
    def test_room_link_carries_host_port_and_slot(self) -> None:
        url = site_url_for("archipelago://KryenSR:None@archipelago.gg:56476?game=Stick Ranger&room=l2hnKd9z")
        self.assertEqual(url, f"{SITE_URL}?host=archipelago.gg&port=56476&slot=KryenSR")

    def test_slot_name_is_unescaped(self) -> None:
        url = site_url_for("archipelago://Thomas%20SR:None@archipelago.gg:56476?game=Stick%20Ranger")
        self.assertEqual(url, f"{SITE_URL}?host=archipelago.gg&port=56476&slot=Thomas+SR")

    def test_password_is_not_forwarded(self) -> None:
        url = site_url_for("archipelago://KryenSR:hunter2@archipelago.gg:56476?game=Stick Ranger")
        self.assertNotIn("hunter2", url)

    def test_plain_launch_opens_the_site(self) -> None:
        self.assertEqual(site_url_for(), SITE_URL)
        self.assertEqual(site_url_for("not a link"), SITE_URL)

    def test_bad_port_is_dropped(self) -> None:
        url = site_url_for("archipelago://KryenSR:None@archipelago.gg:abc?game=Stick Ranger")
        self.assertEqual(url, f"{SITE_URL}?host=archipelago.gg&slot=KryenSR")
