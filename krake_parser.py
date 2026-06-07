import gzip
from pathlib import Path
from typing import Dict, Set
import xml.etree.ElementTree as  ElementTree

KANJI_TO_RADICAL: Dict[str, Set[str]] = {}
RADICAL_TO_KANJI: Dict[str, Set[str]] = {}
KANJI_TO_MEANINGS: dict[str, Set[str]] = {}

def load_kanjidic2(path: Path) -> None:
    global KANJI_TO_MEANINGS
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            tree = ElementTree.parse(f)
    else:
        with open(path, encoding="utf-8") as f:
            tree = ElementTree.parse(f)

    result: dict[str, Set[str]] = {}
    for character in tree.getroot().findall("character"):
        literal = character.findtext("literal")
        if literal:
            meanings = {
                str(m.text) for m in character.findall(".//meaning")
                if m.get("m_lang") is None and m.text
            }
            if meanings:
                result[literal] = meanings

    KANJI_TO_MEANINGS = result


def load_krad(path: Path) -> None:
    with open(path, encoding="euc-jp") as f:
        for line in f:
            if line.startswith("#"):
                continue
            if ":" not in line:
                continue
            kanji, radicals = line.split(":")
            kanji = kanji.strip()
            radical_list = radicals.split()
            KANJI_TO_RADICAL[kanji] = set(radical_list)
            for r in radical_list:
                RADICAL_TO_KANJI.setdefault(r, set()).add(kanji)


def get_neighbours(kanji: str) -> list[str]:
    radicals = KANJI_TO_RADICAL.get(kanji, [])
    neighbours: set[str] = set()
    for r in radicals:
        neighbours.update(RADICAL_TO_KANJI.get(r, []))
    neighbours.discard(kanji)
    return list(neighbours)


def get_description(kanji: str) -> str:
    meanings = KANJI_TO_MEANINGS.get(kanji, [])
    return ", ".join(meanings) if meanings else "No description found"