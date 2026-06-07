from __future__ import annotations

from typing import Optional

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    Qt,
    QVBoxLayout,
    QWidget,
)

from .config import get_config, save_config


def collect_deck_fields() -> dict[str, list[str]]:
    """
    Return {deck_name: [field_names, ...]} for every deck that has at least
    one note.  Field names are deduplicated and sorted.
    """
    col = mw.col
    result: dict[str, list[str]] = {}

    for deck in col.decks.all_names_and_ids():
        deck_name: str = deck.name
        # Find all note ids in this deck (including children)
        note_ids = col.find_notes(f'"deck:{deck_name}"')
        fields: set[str] = set()
        for nid in note_ids:
            note = col.get_note(nid)
            fields.update(note.keys())
        if fields:
            result[deck_name] = sorted(fields)

    return result


# ---------------------------------------------------------------------------
# Per-deck row widget
# ---------------------------------------------------------------------------

class DeckRow(QWidget):
    """One horizontal row: [✓ checkbox] [Deck label] [Field combo]"""

    def __init__(
        self,
        deck_name: str,
        fields: list[str],
        current_field: Optional[str],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.deck_name = deck_name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        # Enable checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(current_field is not None)
        self.checkbox.setFixedWidth(24)
        layout.addWidget(self.checkbox)

        # Deck name label
        label = QLabel(deck_name)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        label.setToolTip(deck_name)
        layout.addWidget(label, stretch=1)

        # Field combo
        self.combo = QComboBox()
        self.combo.setMinimumWidth(160)
        for f in fields:
            self.combo.addItem(f)

        if current_field and current_field in fields:
            self.combo.setCurrentText(current_field)
        elif fields:
            self.combo.setCurrentIndex(0)

        layout.addWidget(self.combo)

        # Gray out combo when checkbox is off
        self.combo.setEnabled(self.checkbox.isChecked())
        self.checkbox.toggled.connect(self.combo.setEnabled)

    def selected_field(self) -> Optional[str]:
        """Return the chosen field name, or None if this deck is disabled."""
        if not self.checkbox.isChecked():
            return None
        return self.combo.currentText()


class DeckFieldDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent or mw)
        self.setWindowTitle("Addon — Deck / Field Configuration")
        self.setMinimumWidth(540)
        self.setMinimumHeight(420)
        self._rows: list[DeckRow] = []
        self.build_ui()

    def build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        # Header
        header = QLabel(
            "<b>Configure which field to read per deck.</b><br>"
            "Tick a deck to enable the addon for it, then pick a field."
        )
        header.setWordWrap(True)
        root.addWidget(header)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(line)

        # Scrollable deck list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(2)
        inner_layout.setContentsMargins(4, 4, 4, 4)

        cfg = get_config()
        deck_fields = collect_deck_fields()

        if not deck_fields:
            inner_layout.addWidget(QLabel("No decks with notes found in collection."))
        else:
            for deck_name, fields in sorted(deck_fields.items()):
                current = cfg.get(deck_name)
                row = DeckRow(deck_name, fields, current, inner)
                self._rows.append(row)
                inner_layout.addWidget(row)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll, stretch=1)

        btn_box = QDialogButtonBox()
        save_btn = btn_box.addButton("Save", QDialogButtonBox.ButtonRole.AcceptRole)
        save_btn.clicked.connect(self.save_and_accept)
        root.addWidget(btn_box)

    def save_and_accept(self) -> None:
        mapping: dict[str, str] = {}
        for row in self._rows:
            field = row.selected_field()
            if field is not None:
                mapping[row.deck_name] = field
        save_config(mapping)
        self.accept()


def show_deck_field_dialog() -> None:
    """Create and exec the dialog (blocks until the user clicks Save)."""
    dlg = DeckFieldDialog()
    dlg.exec()
