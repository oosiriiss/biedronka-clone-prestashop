import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import os

load_dotenv()

# --- KONFIGURACJA ---
API_URL = 'http://localhost:8080/api'
API_KEY = os.getenv("PRESTASHOP_API_KEY")

# Lista tych samych 5 produktów co w wariantach
TARGET_PRODUCTS = [
    "Over Pet Premium Szampon dla psów krótkowłosych 285 ml",
    "Vital Fresh Rukola 100 g",
    "Czosnek opak. 250 g",
    "Vital Fresh Marcheweczki 180 g",
    "Papryka czerwona"
]

# Promocja -10%
DISCOUNT_PERCENT = 0.10  # 10%

# --- POMOCNIKI API ---
session = requests.Session()
session.auth = (API_KEY, '')
session.verify = False 
import urllib3
urllib3.disable_warnings()

def get_blank_schema(resource):
    """Pobiera pusty XML"""
    try:
        r = session.get(f"{API_URL}/{resource}?schema=blank")
        return ET.fromstring(r.content)
    except Exception as e:
        print(f"blad schema {resource}: {e}")
        return None

def search_id(resource, name):
    """Szuka ID produktu po nazwie"""
    r = session.get(f"{API_URL}/{resource}?filter[name]=[{name}]&display=[id]")
    try:
        xml = ET.fromstring(r.content)
        node = xml.find(resource)
        if node is not None and len(node) > 0:
            return node[0].find('id').text
    except:
        pass
    return None

def set_promotion(product_id, reduction):
    """Tworzy cenę specyficzną (promocję)"""
    
    # 1. Pobierz pusty szablon
    root = get_blank_schema('specific_prices')
    if not root: return False
    
    price_node = root.find('specific_price')
    
    # 2. Uzupełnij dane
    price_node.find('id_shop').text = '1'              # ID sklepu
    price_node.find('id_cart').text = '0'              # Nie dotyczy konkretnego koszyka
    price_node.find('id_product').text = str(product_id)
    price_node.find('id_product_attribute').text = '0' # 0 = WSZYSTKIE warianty produktu
    price_node.find('id_currency').text = '0'          # Wszystkie waluty
    price_node.find('id_country').text = '0'           # Wszystkie kraje
    price_node.find('id_group').text = '0'             # Wszystkie grupy klientów
    price_node.find('id_customer').text = '0'          # Wszyscy klienci
    price_node.find('price').text = '-1'               # Cena bazowa (z produktu)
    price_node.find('from_quantity').text = '1'        # Od 1 sztuki
    price_node.find('reduction').text = str(reduction) # Wartość obniżki (np. 0.10)
    price_node.find('reduction_tax').text = '1'        # Obniżka brutto (z podatkiem)
    price_node.find('reduction_type').text = 'percentage' # Typ: procent
    price_node.find('from').text = '0000-00-00 00:00:00'  # Od zawsze
    price_node.find('to').text = '0000-00-00 00:00:00'    # Na zawsze
    
    # 3. Wyślij
    xml_str = ET.tostring(root, encoding='utf-8')
    r = session.post(f"{API_URL}/specific_prices", data=xml_str)
    
    if r.status_code == 201:
        return True
    elif "This specific price already exists" in r.text:
        print("Promocja istnieje")
        return True
    else:
        print(f"error API {r.status_code}: {r.text[:100]}")
        return False

# --- GŁÓWNA PĘTLA ---

print(f"--- Ustawianie promocji -{int(DISCOUNT_PERCENT*100)}% ---")

for prod_name in TARGET_PRODUCTS:
    print(f"\nProdukt: {prod_name}")
    
    # 1. Znajdź ID
    pid = search_id('products', prod_name)
    
    if not pid:
        print("Nie znaleziono produktu.")
        continue
        
    print(f"ID PRODUKTU {pid}")
    
    # 2. Ustaw promocję
    if set_promotion(pid, DISCOUNT_PERCENT):
        print("Promocja ustawiona.")

print("\n--- Zakończono ---")
