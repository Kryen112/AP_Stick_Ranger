"""Launcher component that opens Stick Ranger on dan-ball.jp for the userscript.

The client is a userscript that runs on the official Stick Ranger page. The
room page on archipelago.gg links every player name to an
``archipelago://<slot>:None@<host>:<port>?game=Stick Ranger&room=<id>`` address.
The Launcher hands that address to the component registered for the game, so
this turns it into a link to the game page that carries the same host, port and
slot name for the connect form. They travel in the fragment (``#ap&host=…``):
the browser never sends a fragment to dan-ball.jp, and ``#ap`` is what puts the
userscript in AP mode. The password is never put in the link.
"""

from __future__ import annotations

from urllib.parse import unquote, urlencode, urlparse

PAGE_URL = "https://dan-ball.jp/en/javagame/ranger/"


def page_url_for(uri: str | None = None) -> str:
    """The game page, in AP mode with the connection details from ``uri`` if given."""
    if not uri or not uri.startswith("archipelago://"):
        return PAGE_URL
    parsed = urlparse(uri)
    details: dict[str, str] = {}
    if parsed.hostname:
        details["host"] = parsed.hostname
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port:
        details["port"] = str(port)
    if parsed.username:
        details["slot"] = unquote(parsed.username)
    if not details:
        return PAGE_URL
    return f"{PAGE_URL}#ap&{urlencode(details)}"


def launch_client(*args: str) -> None:
    import webbrowser

    webbrowser.open(page_url_for(args[0] if args else None))
