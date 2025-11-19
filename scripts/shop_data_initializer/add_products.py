import os
import json
import requests
import xml.etree.ElementTree as ET
from random import randint
import unidecode
from dotenv import load_dotenv

load_dotenv()

PRESTASHOP_API_KEY = os.getenv("PRESTASHOP_API_KEY")
API_URL = "http://localhost:8080/api"
LANG_ID = 1
product_index = 0

HEADERS_XML = {
    "Content-Type": "application/xml",
    "Accept": "application/xml"
}


def set_or_create(node, tag, value):
    """Ustawia wartość w istniejącym węźle lub tworzy nowy."""
    child = node.find(tag)
    if child is None:
        child = ET.SubElement(node, tag)
    child.text = str(value)


def generate_link_rewrite(title):
    """Generuje poprawny link_rewrite dla PrestaShop."""
    return unidecode.unidecode(title).lower().replace(" ", "-").replace("/", "-")


def create_product_xml(product, category_id, product_index):
    """Tworzy XML dla produktu."""
    price = round(float(product['price'].replace(" PLN", "").replace(",", ".")) / 1.23, 2)
    link_rewrite = generate_link_rewrite(product['title'])

    description_combined = ""
    for section in product.get("description_sections", []):
        header = section.get("header", "")
        content = section.get("content", "")
        if header or content:
            description_combined += f"{header}: {content}\n"

    # Usuwamy ostatni znak nowej linii
    description_combined = description_combined.strip()

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
  <product>
    <id_manufacturer><![CDATA[0]]></id_manufacturer>
    <id_category_default><![CDATA[{category_id}]]></id_category_default>
    <new><![CDATA[1]]></new>
    <id_tax_rules_group><![CDATA[0]]></id_tax_rules_group>
    <cache_default_attribute><![CDATA[0]]></cache_default_attribute>
    <type><![CDATA[1]]></type>
    <id_shop_default><![CDATA[1]]></id_shop_default>
    <reference><![CDATA[{product_index}]]></reference>
    <state><![CDATA[1]]></state>
    <price><![CDATA[{price}]]></price>
    <wholesale_price><![CDATA[{price}]]></wholesale_price>
    <show_price><![CDATA[1]]></show_price>
    <unit_price><![CDATA[{price}]]></unit_price>
    <active><![CDATA[1]]></active>
    <minimal_quantity><![CDATA[1]]></minimal_quantity>
    <available_for_order><![CDATA[1]]></available_for_order>
    <meta_description>
        <language id="{LANG_ID}"><![CDATA[{product.get('meta_description','') }]]></language>
    </meta_description>
    <meta_keywords>
        <language id="{LANG_ID}"><![CDATA[{product.get('meta_keywords','') }]]></language>
    </meta_keywords>
    <meta_title>
        <language id="{LANG_ID}"><![CDATA[{product.get('meta_title','') }]]></language>
    </meta_title>
    <link_rewrite>
      <language id="{LANG_ID}"><![CDATA[{link_rewrite}]]></language>
    </link_rewrite>
    <name>
      <language id="{LANG_ID}"><![CDATA[{product['title']}]]></language>
    </name>
    <description>
      <language id="{LANG_ID}"><![CDATA[{description_combined}]]></language>
    </description>
    <description_short>
      <language id="{LANG_ID}"><![CDATA[{product.get('subname','') }]]></language>
    </description_short>
    <associations>
      <categories>
        <category><id><![CDATA[{category_id}]]></id></category>
      </categories>
    </associations>
  </product>
</prestashop>"""
    return xml.encode("utf-8")


def create_product(product, category_ids):
    """Tworzy produkt w PrestaShop i zwraca ID oraz stock ID."""
    global product_index
    category_name = product["absolute_path"].split("/")[-2]
    category_id = category_ids.get(category_name, 2)

    xml_data = create_product_xml(product, category_id, product_index)
    response = requests.post(
        f"{API_URL}/products",
        data=xml_data,
        headers=HEADERS_XML,
        auth=(PRESTASHOP_API_KEY, "")
    )

    if response.status_code not in [200, 201]:
        print(f"Błąd dodawania produktu '{product['title']}': {response.status_code}")
        print(response.text)
        return None

    root = ET.fromstring(response.content)
    product_id = int(root.find("product/id").text)
    print(f"Produkt '{product['title']}' dodany, ID: {product_id}")

    # Pobranie stock ID
    stock_url = f"{API_URL}/stock_availables/?filter[id_product]={product_id}"
    stock_resp = requests.get(stock_url, auth=(PRESTASHOP_API_KEY, ""))
    stock_root = ET.fromstring(stock_resp.content)
    first_stock = stock_root.find("stock_availables/stock_available")
    stock_id = int(first_stock.attrib["id"]) if first_stock is not None else None

    product_index += 1
    return product_id, stock_id, product.get("images", [])


def update_stock_quantity(stock_id, product_id, quantity=None):
    """Aktualizuje stock produktu na losową ilość."""
    if quantity is None:
        quantity = randint(40000, 90000)

    response_get = requests.get(
        f"{API_URL}/stock_availables/{stock_id}",
        auth=(PRESTASHOP_API_KEY, ""),
        headers=HEADERS_XML
    )

    if response_get.status_code != 200:
        print(f"Błąd pobierania stock ID {stock_id}")
        return False

    root = ET.fromstring(response_get.content)
    stock_node = root.find(".//stock_available")
    if stock_node is None:
        print("Nie znaleziono węzła stock_available")
        return False

    set_or_create(stock_node, "quantity", quantity)
    set_or_create(stock_node, "depends_on_stock", 0)
    set_or_create(stock_node, "out_of_stock", 1)

    prestashop_node = ET.Element("prestashop", {"xmlns:xlink": "http://www.w3.org/1999/xlink"})
    prestashop_node.append(stock_node)
    final_xml = ET.tostring(prestashop_node, encoding='utf-8', xml_declaration=True)

    response_put = requests.put(
        f"{API_URL}/stock_availables/{stock_id}",
        data=final_xml,
        headers=HEADERS_XML,
        auth=(PRESTASHOP_API_KEY, "")
    )

    if response_put.status_code == 200:
        print(f"Stock dla produktu ID {product_id} ustawiony na {quantity}")
        return True
    print(f"Błąd aktualizacji stock ID {stock_id}: {response_put.status_code}")
    return False


def upload_product_image(product_id, image_path):
    """Dodaje zdjęcie do produktu."""
    with open(image_path, "rb") as img_file:
        response = requests.post(
            f"{API_URL}/images/products/{product_id}",
            files={"image": img_file},
            auth=(PRESTASHOP_API_KEY, "")
        )

    if response.status_code in [200, 201]:
        print(f"Zdjęcie dla produktu {product_id} dodane.")
    else:
        print(f"Błąd dodawania zdjęcia dla produktu {product_id}: {response.status_code}")


def create_product_with_stock(product, category_ids):
    """Tworzy produkt, ustawia stock i dodaje zdjęcia."""
    result = create_product(product, category_ids)
    if not result:
        return None

    product_id, stock_id, images_paths = result
    update_stock_quantity(stock_id, product_id)

    for img_path in images_paths:
        if os.path.exists("../../scraper/" + img_path):
            upload_product_image(product_id, "../../scraper/" + img_path)
        else:
            print(f"{product_id} nie znaleziono zdjecia ../../scraper/{img_path}!")

    return product_id


def fetch_all_category_ids():
    """Pobiera wszystkie kategorie z PrestaShop i zwraca słownik {nazwa: id}."""
    response = requests.get(
        f"{API_URL}/categories?display=[id,name]&language={LANG_ID}",
        auth=(PRESTASHOP_API_KEY, ""),
        headers=HEADERS_XML
    )

    if response.status_code != 200:
        print("Błąd pobierania kategorii:", response.status_code)
        return {}

    root = ET.fromstring(response.content)
    categories = {}
    for cat in root.findall(".//category"):
        cat_id = int(cat.find("id").text)
        name_node = cat.find(f"name/language[@id='{LANG_ID}']")
        if name_node is not None and name_node.text:
            categories[name_node.text] = cat_id

    print(f"Pobrano {len(categories)} kategorii z PrestaShop.")
    return categories


products = []
with open("../../scraper/products.jsonl", "r", encoding="utf-8") as f:
    products = [json.loads(line.strip()) for line in f]

category_ids = fetch_all_category_ids()

for product in products:
    create_product_with_stock(product, category_ids)
