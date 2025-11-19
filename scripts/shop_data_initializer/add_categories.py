import json
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import requests
import unidecode

load_dotenv()

PRESTASHOP_API_KEY = os.getenv("PRESTASHOP_API_KEY")
API_URL = "http://localhost:8080/api"
LANG_ID = 2
DEFAULT_PARENT_ID = 2 # Root
CATEGORIES_FILE = "../../scraper/categories.jsonl"

category_ids = {}


def slugify(name: str) -> str:
    """Konwertuje nazwę kategorii na link_rewrite."""
    return unidecode.unidecode(name).lower().replace(" ", "-")

def build_category_xml(name: str, parent_id: int) -> str:
    """Generuje XML dla nowej kategorii."""
    link_rewrite = slugify(name)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
  <category>
    <id_parent><![CDATA[{parent_id}]]></id_parent>
    <active><![CDATA[1]]></active>
    <name>
      <language id="{LANG_ID}"><![CDATA[{name}]]></language>
    </name>
    <link_rewrite>
      <language id="{LANG_ID}"><![CDATA[{link_rewrite}]]></language>
    </link_rewrite>
  </category>
</prestashop>
"""

def create_category(name: str, parent_id: int = None) -> int | None:
    """Tworzy kategorię w PrestaShop i zwraca jej ID."""
    parent_id = parent_id or DEFAULT_PARENT_ID
    xml_data = build_category_xml(name, parent_id)

    response = requests.post(
        f"{API_URL}/categories",
        data=xml_data.encode("utf-8"),
        headers={"Content-Type": "application/xml"},
        auth=(PRESTASHOP_API_KEY, "")
    )

    if response.status_code in (200, 201):
        root = ET.fromstring(response.content)
        new_id = int(root.find("category/id").text)
        print(f"Kategoria '{name}' dodana, ID: {new_id}")
        return new_id
    else:
        print(f"Nie udało się dodać kategorii '{name}'")
        print(response.status_code, response.text)
        return None

def add_category_recursive(cat: dict):
    """Dodaje kategorię uwzględniając rodzica."""
    parent_name = cat.get("parent")
    parent_id = category_ids.get(parent_name)
    cat_id = create_category(cat["name"], parent_id)
    if cat_id:
        category_ids[cat["name"]] = cat_id

def load_categories(file_path: str) -> list[dict]:
    """Ładuje kategorie z pliku JSONL."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def main():
    categories = load_categories(CATEGORIES_FILE)
    pending = categories.copy()

    while pending:
        still_pending = []
        for cat in pending:
            if cat.get("parent") is None or cat.get("parent") in category_ids:
                add_category_recursive(cat)
            else:
                still_pending.append(cat)

        if len(still_pending) == len(pending):
            missing_parents = [c["name"] for c in still_pending]
            print("[WARNING] Niektóre kategorie mają brakującego rodzica:", missing_parents)
            break

        pending = still_pending

    print("Dodawanie kategorii zakończone.")


if __name__ == "__main__":
    main()
