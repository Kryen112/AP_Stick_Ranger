from __future__ import annotations

import unittest

from ..client import PAGE_URL, page_url_for


class TestPageUrl(unittest.TestCase):
    def test_room_link_carries_host_port_and_slot_in_the_fragment(self) -> None:
        url = page_url_for("archipelago://KryenSR:None@archipelago.gg:56476?game=Stick Ranger&room=l2hnKd9z")
        self.assertEqual(url, f"{PAGE_URL}#ap&host=archipelago.gg&port=56476&slot=KryenSR")

    def test_nothing_reaches_the_server_side_of_the_address(self) -> None:
        url = page_url_for("archipelago://KryenSR:None@archipelago.gg:56476?game=Stick Ranger")
        self.assertNotIn("?", url, "details in a query string would be sent to dan-ball.jp")

    def test_slot_name_is_unescaped(self) -> None:
        url = page_url_for("archipelago://Thomas%20SR:None@archipelago.gg:56476?game=Stick%20Ranger")
        self.assertEqual(url, f"{PAGE_URL}#ap&host=archipelago.gg&port=56476&slot=Thomas+SR")

    def test_password_is_not_forwarded(self) -> None:
        url = page_url_for("archipelago://KryenSR:hunter2@archipelago.gg:56476?game=Stick Ranger")
        self.assertNotIn("hunter2", url)

    def test_plain_launch_opens_the_page(self) -> None:
        self.assertEqual(page_url_for(), PAGE_URL)
        self.assertEqual(page_url_for("not a link"), PAGE_URL)

    def test_bad_port_is_dropped(self) -> None:
        url = page_url_for("archipelago://KryenSR:None@archipelago.gg:abc?game=Stick Ranger")
        self.assertEqual(url, f"{PAGE_URL}#ap&host=archipelago.gg&slot=KryenSR")
