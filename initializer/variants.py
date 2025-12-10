import requests
import xml.etree.ElementTree as ET

API_URL = 'https://localhost:443/api'
API_KEY = 'DBV8CNPPZLBCCREL5PHLQECG5AN9PSHY' 

TARGETS = {
    "Over Pet Premium Szampon dla psów krótkowłosych 285 ml": {
        "group_name": "Pojemność",
        # wariant + o ile zmieni sie cena
        "variants": [
            {"val": "285 ml", "price_impact": 0.00},
            {"val": "500 ml", "price_impact": 12.00},
            {"val": "1 L",    "price_impact": 25.00}
        ]
    },
    "Vital Fresh Rukola 100 g": {
        "group_name": "Waga",
        "variants": [
            {"val": "100 g", "price_impact": 0.00},
            {"val": "200 g", "price_impact": 4.50}
        ]
    },
    "Czosnek opak. 250 g": {
        "group_name": "Waga",
        "variants": [
            {"val": "250 g", "price_impact": 0.00},
            {"val": "500 g", "price_impact": 3.00}
        ]
    },
    "Vital Fresh Marcheweczki 180 g": {
        "group_name": "Waga",
        "variants": [
            {"val": "180 g", "price_impact": 0.00},
            {"val": "360 g", "price_impact": 2.50}
        ]
    },
    "Papryka czerwona": {
        "group_name": "Pakowanie",
        "variants": [
            {"val": "1 szt.", "price_impact": 0.00},
            {"val": "3-pak",  "price_impact": 5.00}
        ]
    }
}

session = requests.Session()
session.auth = (API_KEY, '')
session.verify = False 
import urllib3
urllib3.disable_warnings()

def get_blank_schema(resource):
    """pusty xml"""
    try:
        r = session.get(f"{API_URL}/{resource}?schema=blank")
        return ET.fromstring(r.content)
    except Exception as e:
        print(f"error get_blank_schema {resource}: {e}")
        return None

def search_id(resource, name):
    """Szuka ID zasobu po nazwie"""
    r = session.get(f"{API_URL}/{resource}?filter[name]=[{name}]&display=[id]")
    try:
        xml = ET.fromstring(r.content)
        node = xml.find(resource)
        if node is not None and len(node) > 0:
            return node[0].find('id').text
    except:
        pass
    return None

def get_or_create_option(resource, name, group_id=None):
    existing_id = search_id(resource, name)
    if existing_id and resource == 'product_options': 
        return existing_id

    root = get_blank_schema(resource)
    if root is None: return None 
    
    item = root.find(resource[:-1]) 
    if item is None: 
        item = root[0]

    if resource == 'product_options': 
        item.find('name').find('language').text = name
        item.find('public_name').find('language').text = name
        item.find('group_type').text = 'select'
    else: 
        item.find('id_attribute_group').text = str(group_id)
        item.find('name').find('language').text = name

    r = session.post(f"{API_URL}/{resource}", data=ET.tostring(root))
    if r.status_code == 201:
        return ET.fromstring(r.content).find(f"{resource[:-1]}/id").text
    
    return existing_id

def create_combination(product_id, value_id, price_impact):
    """tworzy kombinacje z wartoscia"""
    root = get_blank_schema('combinations')
    combo = root.find('combination')
    
    combo.find('id_product').text = str(product_id)
    combo.find('price').text = str(price_impact)
    combo.find('minimal_quantity').text = '1'
    
    assocs = combo.find('associations')
    vals_node = ET.SubElement(assocs, 'product_option_values')
    val_node = ET.SubElement(vals_node, 'product_option_value')
    ET.SubElement(val_node, 'id').text = str(value_id)
    
    r = session.post(f"{API_URL}/combinations", data=ET.tostring(root))
    if r.status_code == 201:
        return ET.fromstring(r.content).find('combination/id').text
    
    print(f"nie udalo sie ttworzyc kombinacji (Kod {r.status_code}): {r.text[:200]}")
    return None

def update_stock(product_id, combo_id, qty):
    url = f"{API_URL}/stock_availables?display=full&filter[id_product]={product_id}&filter[id_product_attribute]={combo_id}"
    r = session.get(url)
    try:
        root = ET.fromstring(r.content)
        stock_node = root.find('stock_availables/stock_available')
        
        if stock_node is not None:
            stock_id = stock_node.find('id').text
            stock_node.find('quantity').text = str(qty)
            
            payload = ET.Element('prestashop')
            payload.set('xmlns:xlink', "http://www.w3.org/1999/xlink")
            payload.append(stock_node)
            
            session.put(f"{API_URL}/stock_availables/{stock_id}", data=ET.tostring(payload))
    except Exception as e:
        print(f"blad aktualizacji magazynu {e}")

print("--- Start: Dodawanie wariantów dla 5 produktów ---\n")

for prod_name, config in TARGETS.items():
    print("")
    print(f"Produkt: {prod_name}")
    
    pid = search_id('products', prod_name)
    if not pid:
        print(f"nie znaleziono produktu o nazwie '{prod_name}'. Pomijanie")
        continue
    print(f"ID Produktu: {pid}")
    
    group_name = config['group_name']
    gid = get_or_create_option('product_options', group_name)
    print(f"Grupa '{group_name}' ID: {gid}")
    
    if not gid:
        print("nie udalo sie stworzyc grupy atrybutow")
        continue

    for variant in config['variants']:
        val_name = variant['val']
        impact = variant['price_impact']
        
        vid = get_or_create_option('product_option_values', val_name, group_id=gid)
        if not vid:
            print(f"nie udalo sie stworzyc wartosci '{val_name}'")
            continue
            
        cid = create_combination(pid, vid, impact)
        if cid:
            print(f"wariant {val_name} stworzony")
            update_stock(pid, cid, 50)

            
print("\n\n--- Zakończono ---")
