"""Launcher component that opens the Stick Ranger website.

The room page on archipelago.gg links every player name to an
``archipelago://<slot>:None@<host>:<port>?game=Stick Ranger&room=<id>`` address.
The Launcher hands that address to the component registered for the game, so
this turns it into a website link that carries the same host, port and slot
name for the connect form to fill in.
"""

from __future__ import annotations

from urllib.parse import unquote, urlencode, urlparse

SITE_URL = "https://kryen112.github.io/"


def site_url_for(uri: str | None = None) -> str:
    """The website address, with the connection details from ``uri`` if given."""
    if not uri or not uri.startswith("archipelago://"):
        return SITE_URL
    parsed = urlparse(uri)
    query: dict[str, str] = {}
    if parsed.hostname:
        query["host"] = parsed.hostname
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port:
        query["port"] = str(port)
    if parsed.username:
        query["slot"] = unquote(parsed.username)
    if not query:
        return SITE_URL
    return f"{SITE_URL}?{urlencode(query)}"


def launch_client(*args: str) -> None:
    import webbrowser

    webbrowser.open(site_url_for(args[0] if args else None))
