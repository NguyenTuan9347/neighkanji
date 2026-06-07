from anki.cards import Card
from aqt import gui_hooks, mw, QAction
from aqt.reviewer import Reviewer

from .config import RESOURCES_DIR, get_config, KRAD_PANEL_HTML, KRAD_PANEL_JS
from .krake_parser import load_krad, get_neighbours, get_description, load_kanjidic2
from .deck_field_dialog import show_deck_field_dialog

CFG = get_config()

_fetched_data: str | None = None

load_kanjidic2(RESOURCES_DIR / "kanjidic2.xml")
load_krad(RESOURCES_DIR / "kradfile")

action = QAction("Krad Addon Settings...", mw)
action.triggered.connect(show_deck_field_dialog)
mw.form.menuTools.addAction(action)
MAX_SIMILAR = 5

def get_field_for_card(card: Card) -> str | None:
    """Return the configured field value for this card's deck, or None."""
    deck_name: str = mw.col.decks.name(card.did)
    note = card.note()
    parts = deck_name.split("::")
    prefix = ""
    prefixes = []
    for part in parts:
        prefix = part if not prefix else prefix + "::" + part
        prefixes.append(prefix)

    # This can update config to support the nested deck a bit faster but
    # the deck names realistically can't exceed 10^5 character so this should be fine for linear search
    for candidate in reversed(prefixes):
        field_name = CFG.get(candidate, "")
        if field_name and field_name in note:
            return note[field_name]

    return None


import json

def on_webview_will_set_content(web_content, context):
    if not isinstance(context, Reviewer):
        return
    web_content.body += KRAD_PANEL_HTML
    web_content.body += f"<script>{KRAD_PANEL_JS}</script>"

def reviewer_did_show_answer(card: Card) -> None:
    global _fetched_data
    if _fetched_data is None:
        return

    neighbours = get_neighbours(_fetched_data)[:MAX_SIMILAR]
    if not neighbours:
        return

    payload = [
        {"kanji": k, "desc": get_description(k)}
        for k in neighbours
    ]
    mw.reviewer.web.eval(f"kradShow({json.dumps(_fetched_data)}, {json.dumps(payload)})")

def reviewer_did_show_question(card: Card) -> None:
    global _fetched_data
    _fetched_data = None
    _fetched_data = get_field_for_card(card)
    mw.reviewer.web.eval("kradHide()")


gui_hooks.reviewer_did_show_question.append(reviewer_did_show_question)
gui_hooks.reviewer_did_show_answer.append(reviewer_did_show_answer)
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)