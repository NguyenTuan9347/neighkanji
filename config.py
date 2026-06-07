"""
config.py — lightweight JSON config for the addon.

Schema of config.json:
{
    "Deck Name": "FieldName",
    "Japanese::Kanji": "Expression",
    ...
}
"""

import json
from pathlib import Path

ADDON_DIR = Path(__file__).parent
RESOURCES_DIR = ADDON_DIR / "resources"
CONFIG_FILE = ADDON_DIR / "config.json"
WEBVIEW_DIR = RESOURCES_DIR / "webviews"
KRAD_PANEL = (WEBVIEW_DIR / "krad_panel")
KRAD_PANEL_HTML = (KRAD_PANEL / "index.html").read_text(encoding="utf-8")
KRAD_PANEL_JS   = (KRAD_PANEL / "main.js").read_text(encoding="utf-8")

def get_config() -> dict[str, str]:
    """Return the deck→field mapping. Empty dict if not yet configured."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(mapping: dict[str, str]) -> None:
    """Persist the deck→field mapping to disk."""
    CONFIG_FILE.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )